import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QPushButton,
                           QFrame, QMessageBox, QScrollArea, QFileDialog,
                           QDialog, QDialogButtonBox, QMenuBar, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from datetime import datetime

class CompanySettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Company Settings")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        # Logo section
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        
        self.logo_preview = QLabel("No logo selected")
        self.logo_preview.setFixedSize(100, 50)
        self.logo_preview.setStyleSheet("border: 1px solid gray;")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(self.logo_preview)
        
        logo_button = QPushButton("Select Logo")
        logo_button.clicked.connect(self.select_logo)
        logo_layout.addWidget(logo_button)
        layout.addWidget(logo_widget)
        
        # Company info inputs
        self.company_name = self._create_input_group("Company Name:", layout)
        self.company_email = self._create_input_group("Company Email:", layout)
        self.company_address = self._create_input_group("Company Address:", layout)
        
        # Load existing settings
        self.logo_path = None
        if settings:
            self.company_name.setText(settings.get('company_name', ''))
            self.company_email.setText(settings.get('company_email', ''))
            self.company_address.setText(settings.get('company_address', ''))
            if settings.get('logo_path'):
                self.load_logo(settings['logo_path'])
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _create_input_group(self, label_text, parent_layout):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel(label_text))
        line_edit = QLineEdit()
        layout.addWidget(line_edit)
        parent_layout.addWidget(widget)
        return line_edit
    
    def select_logo(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Logo Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_name:
            self.load_logo(file_name)
    
    def load_logo(self, file_name):
        self.logo_path = file_name
        pixmap = QPixmap(file_name)
        scaled_pixmap = pixmap.scaled(100, 50, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo_preview.setPixmap(scaled_pixmap)
        self.logo_preview.setStyleSheet("")
    
    def get_settings(self):
        return {
            'company_name': self.company_name.text(),
            'company_email': self.company_email.text(),
            'company_address': self.company_address.text(),
            'logo_path': self.logo_path
        }

class CustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Information")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        self.customer_name = self._create_input_group("Customer Name:", layout)
        self.customer_email = self._create_input_group("Customer Email:", layout)
        self.customer_address = self._create_input_group("Customer Address:", layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _create_input_group(self, label_text, parent_layout):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel(label_text))
        line_edit = QLineEdit()
        layout.addWidget(line_edit)
        parent_layout.addWidget(widget)
        return line_edit
    
    def get_customer_info(self):
        return {
            'name': self.customer_name.text(),
            'email': self.customer_email.text(),
            'address': self.customer_address.text()
        }

class InvoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator")
        self.setMinimumSize(800, 600)
        self.company_settings = self.load_settings()
        self.customer_info = None
        
        self.setup_menu()
        self.setup_ui()
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Company Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Header with New Invoice button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        new_invoice_btn = QPushButton("New Invoice")
        new_invoice_btn.clicked.connect(self.new_invoice)
        header_layout.addWidget(new_invoice_btn)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Items Section
        items_frame = QFrame()
        items_frame.setFrameStyle(QFrame.Shape.Box)
        items_layout = QVBoxLayout(items_frame)
        
        items_title = QLabel("Invoice Items")
        items_title.setStyleSheet("font-weight: bold;")
        items_layout.addWidget(items_title)
        
        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.items_container = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        items_layout.addWidget(scroll)
        
        self.items = []
        self.add_item_row()
        
        # Add Item button
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item_row)
        items_layout.addWidget(add_button)
        
        layout.addWidget(items_frame)
        
        # Total and Generate
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_layout.addWidget(QLabel("Total Amount: $"))
        self.total_label = QLabel("0.00")
        total_layout.addWidget(self.total_label)
        bottom_layout.addWidget(total_widget)
        
        generate_button = QPushButton("Generate Invoice")
        generate_button.clicked.connect(self.generate_invoice)
        generate_button.setStyleSheet("padding: 10px; font-weight: bold;")
        bottom_layout.addWidget(generate_button)
        
        layout.addWidget(bottom_widget)
    
    def load_settings(self):
        try:
            with open('company_settings.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_settings(self, settings):
        with open('company_settings.json', 'w') as f:
            json.dump(settings, f)
    
    def show_settings(self):
        dialog = CompanySettingsDialog(self, self.company_settings)
        if dialog.exec():
            self.company_settings = dialog.get_settings()
            self.save_settings(self.company_settings)
    
    def new_invoice(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.customer_info = dialog.get_customer_info()
            # Clear existing items
            for i in reversed(range(self.items_container.count())): 
                self.items_container.itemAt(i).widget().deleteLater()
            self.items = []
            self.add_item_row()
            self.update_total()
    
    def add_item_row(self):
        row = QWidget()
        layout = QHBoxLayout(row)
        
        name = QLineEdit()
        name.setPlaceholderText("Item Name")
        layout.addWidget(name)
        
        price = QLineEdit()
        price.setPlaceholderText("Price")
        price.textChanged.connect(self.update_total)
        layout.addWidget(price)
        
        qty = QLineEdit()
        qty.setPlaceholderText("Qty")
        qty.textChanged.connect(self.update_total)
        layout.addWidget(qty)
        
        self.items.append((name, price, qty))
        self.items_container.addWidget(row)
    
    def update_total(self):
        total = 0
        for name, price, qty in self.items:
            try:
                p = float(price.text() or 0)
                q = float(qty.text() or 0)
                total += p * q
            except ValueError:
                pass
        self.total_label.setText(f"{total:.2f}")
    
    def generate_invoice(self):
        if not self.customer_info:
            QMessageBox.warning(self, "Error", "Please enter customer information")
            return
            
        filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Add company logo
        if self.company_settings.get('logo_path'):
            try:
                # Calculate aspect ratio to fit in 100x50 space
                img = Image(self.company_settings['logo_path'])
                aspect = img.imageWidth / img.imageHeight
                if aspect > 2:  # wider than 2:1
                    img_width = 100
                    img_height = 100 / aspect
                else:
                    img_height = 50
                    img_width = 50 * aspect
                
                c.drawImage(self.company_settings['logo_path'], 50, height - 120, width=img_width, height=img_height)
            except Exception as e:
                print(f"Error adding logo: {e}")
                # If logo fails, draw placeholder
                c.rect(50, height - 120, 100, 50)
                c.setFont("Helvetica", 8)
                c.drawString(70, height - 100, "Logo Error")
        else:
            # Draw placeholder if no logo
            c.rect(50, height - 120, 100, 50)
            c.setFont("Helvetica", 8)
            c.drawString(70, height - 100, "No Logo")
        
        # Add company info
        c.setFont("Helvetica-Bold", 12)
        company_y = height - 120
        c.drawString(200, company_y, self.company_settings.get('company_name', 'Your Company Name'))
        c.setFont("Helvetica", 10)
        c.drawString(200, company_y - 15, self.company_settings.get('company_email', 'company@example.com'))
        c.drawString(200, company_y - 30, self.company_settings.get('company_address', 'Company Address'))
        
        # Add invoice title and number
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 180, "INVOICE")
        c.setFont("Helvetica", 12)
        invoice_number = datetime.now().strftime("INV-%Y%m%d-%H%M")
        c.drawString(50, height - 200, f"Invoice Number: {invoice_number}")
        c.drawString(50, height - 220, f"Date: {datetime.now().strftime('%B %d, %Y')}")
        
        # Add customer info in a box
        c.setStrokeColor(colors.lightgrey)
        c.rect(50, height - 300, 250, 60)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, height - 250, "Bill To:")
        c.setFont("Helvetica", 10)
        c.drawString(60, height - 265, self.customer_info['name'])
        c.drawString(60, height - 280, self.customer_info['email'])
        c.drawString(60, height - 295, self.customer_info['address'] or "")
        
        # Add items table
        data = [["Item", "Quantity", "Price", "Total"]]
        total = 0
        
        for name, price, qty in self.items:
            if name.text() and price.text() and qty.text():
                try:
                    p = float(price.text())
                    q = float(qty.text())
                    item_total = p * q
                    total += item_total
                    data.append([
                        name.text(),
                        str(q),
                        f"${p:.2f}",
                        f"${item_total:.2f}"
                    ])
                except ValueError:
                    continue
        
        # Create table
        table = Table(data, colWidths=[3*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 1), (-1, -1), 12),
        ]))
        
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, height - 500)
        
        # Add total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, height - 520, "Total:")
        c.drawString(500, height - 520, f"${total:.2f}")
        
        # Add footer
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        footer_text = "Thank you for your business!"
        c.drawString(width/2 - c.stringWidth(footer_text, "Helvetica", 8)/2, 30, footer_text)
        
        c.save()
        QMessageBox.information(self, "Success", f"Invoice saved as {filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceApp()
    window.show()
    sys.exit(app.exec())
