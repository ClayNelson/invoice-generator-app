import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QPushButton,
                           QFrame, QMessageBox, QScrollArea, QFileDialog,
                           QDialog, QDialogButtonBox, QMenuBar, QMenu, QComboBox, QCompleter, QGroupBox, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction, QIcon
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from datetime import datetime
import products_db

class CompanySettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Company Settings")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        # Logo and info section
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        # Logo preview
        self.logo_preview = QLabel("No logo selected")
        self.logo_preview.setFixedSize(100, 50)
        self.logo_preview.setStyleSheet("border: 1px solid gray;")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.logo_preview)
        # Company info summary
        self.info_summary = QLabel()
        self.info_summary.setStyleSheet("margin-left:16px;font-size:13px;")
        self.info_summary.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        info_layout.addWidget(self.info_summary)
        layout.addWidget(info_widget)

        logo_button = QPushButton("Select Logo")
        logo_button.clicked.connect(self.select_logo)
        layout.addWidget(logo_button)

        self.company_name = self._create_input_group("Company Name:", layout)
        self.company_email = self._create_input_group("Company Email:", layout)
        self.company_address = self._create_input_group("Company Address:", layout)
        self.logo_path = None

        # If settings provided, pre-fill fields and preview
        if settings:
            self.company_name.setText(settings.get('company_name', ''))
            self.company_email.setText(settings.get('company_email', ''))
            self.company_address.setText(settings.get('company_address', ''))
            if settings.get('logo_path'):
                self.load_logo(settings['logo_path'])
            # Set info summary if any info exists
            summary = []
            if settings.get('company_name'):
                summary.append(f"<b>{settings['company_name']}</b>")
            if settings.get('company_email'):
                summary.append(settings['company_email'])
            if settings.get('company_address'):
                summary.append(settings['company_address'])
            self.info_summary.setText('<br>'.join(summary) if summary else "")
        else:
            self.info_summary.setText("")

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
        # Enhanced error handling for logo loading
        import os
        self.logo_path = file_name
        if not os.path.exists(file_name):
            self.logo_preview.setText("Logo not found")
            self.logo_preview.setPixmap(QPixmap())
            self.logo_preview.setStyleSheet("border: 1px solid red;")
            return
        pixmap = QPixmap(file_name)
        if pixmap.isNull():
            self.logo_preview.setText("Unsupported image")
            self.logo_preview.setPixmap(QPixmap())
            self.logo_preview.setStyleSheet("border: 1px solid red;")
            return
        scaled_pixmap = pixmap.scaled(100, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_preview.setPixmap(scaled_pixmap)
        self.logo_preview.setText("")
        self.logo_preview.setStyleSheet("")
        # Also update info summary if fields are filled
        summary = []
        if self.company_name.text():
            summary.append(f"<b>{self.company_name.text()}</b>")
        if self.company_email.text():
            summary.append(self.company_email.text())
        if self.company_address.text():
            summary.append(self.company_address.text())
        self.info_summary.setText('<br>'.join(summary) if summary else "")

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

class EditProductDialog(QDialog):
    def __init__(self, product_id, name, desc, price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Product")
        self.setModal(True)
        layout = QVBoxLayout(self)
        self.product_id = product_id
        self.name_input = QLineEdit(name)
        self.desc_input = QLineEdit(desc)
        self.price_input = QLineEdit(str(price))
        layout.addWidget(QLabel("Product Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(QLabel("Price:"))
        layout.addWidget(self.price_input)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def get_data(self):
        return self.product_id, self.name_input.text(), self.desc_input.text(), self.price_input.text()

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Product Management")
        self.setMinimumSize(400, 350)
        layout = QVBoxLayout(self)

        # Add Product Section
        add_group = QFrame()
        add_layout = QVBoxLayout(add_group)
        add_group.setFrameStyle(QFrame.Shape.Box)
        add_group.setStyleSheet("margin-bottom: 10px;")
        add_label = QLabel("Add New Product")
        add_label.setStyleSheet("font-weight: bold;")
        add_layout.addWidget(add_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product Name")
        add_layout.addWidget(self.name_input)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (optional)")
        add_layout.addWidget(self.desc_input)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        add_layout.addWidget(self.price_input)
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_group)

        # Product List Section
        self.products_label = QLabel("Saved Products:")
        self.products_label.setStyleSheet("font-weight: bold;margin-top:10px;")
        layout.addWidget(self.products_label)
        self.products_area = QScrollArea()
        self.products_area.setWidgetResizable(True)
        self.products_widget = QWidget()
        self.products_layout = QVBoxLayout(self.products_widget)
        self.products_area.setWidget(self.products_widget)
        layout.addWidget(self.products_area)

        self.refresh_products()

    def add_product(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.text().strip()
        try:
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid price.")
            return
        if not name:
            QMessageBox.warning(self, "Input Error", "Product name is required.")
            return
        product_id = products_db.add_product(name, desc, price)
        QMessageBox.information(self, "Product Added", f"Product #{product_id} added.")
        self.name_input.clear()
        self.desc_input.clear()
        self.price_input.clear()
        self.refresh_products()

    def refresh_products(self):
        # Clear layout
        for i in reversed(range(self.products_layout.count())):
            widget = self.products_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Add products
        products = products_db.get_products()
        if not products:
            self.products_layout.addWidget(QLabel("No products saved."))
        else:
            for pid, name, desc, price in products:
                row = QWidget()
                row_layout = QHBoxLayout(row)
                lbl = QLabel(f"#{pid}: {name} - {desc} (${price:.2f})")
                row_layout.addWidget(lbl)
                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("padding:2px 10px;")
                def make_edit(pid=pid, name=name, desc=desc, price=price):
                    def edit():
                        dialog = EditProductDialog(pid, name, desc, price, self)
                        if dialog.exec():
                            _, new_name, new_desc, new_price = dialog.get_data()
                            try:
                                new_price = float(new_price)
                            except ValueError:
                                QMessageBox.warning(self, "Input Error", "Please enter a valid price.")
                                return
                            if not new_name:
                                QMessageBox.warning(self, "Input Error", "Product name is required.")
                                return
                            products_db.update_product(pid, new_name, new_desc, new_price)
                            self.refresh_products()
                    return edit
                edit_btn.clicked.connect(make_edit())
                row_layout.addWidget(edit_btn)
                self.products_layout.addWidget(row)
        self.products_widget.setLayout(self.products_layout)

class InvoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator")
        self.setMinimumSize(800, 600)
        self.company_settings = self.load_settings()
        self.customer_info = None
        
        products_db.init_db()
        self.setup_menu()
        self.setup_ui()
    
    def load_settings(self):
        try:
            with open('company_settings.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_settings(self, settings):
        with open('company_settings.json', 'w') as f:
            json.dump(settings, f)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Company Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        # Customer Info menu item
        customer_action = QAction("Customer Information", self)
        customer_action.triggered.connect(self.show_customer_dialog)
        file_menu.addAction(customer_action)

        # Product Management menu item
        product_action = QAction("Manage Products", self)
        product_action.triggered.connect(self.show_product_dialog)
        file_menu.addAction(product_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Header with New Invoice button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title_label = QLabel("<b style='font-size:20px'>Nelco Invoice</b>")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        new_invoice_btn = QPushButton("New Invoice")
        new_invoice_btn.setStyleSheet("padding:8px 20px;font-weight:bold;background:#f0f0f0;border-radius:6px;")
        new_invoice_btn.clicked.connect(self.new_invoice)
        header_layout.addWidget(new_invoice_btn)
        layout.addWidget(header)

        # Customer Info Section
        customer_box = QGroupBox("Customer Information")
        customer_box.setStyleSheet("QGroupBox { font-weight: bold; font-size: 15px; margin-top: 10px; } QGroupBox:title { subcontrol-origin: margin; left: 10px;}")
        customer_layout = QVBoxLayout(customer_box)
        self.customer_info_label = QLabel("No customer info set.")
        self.customer_info_label.setStyleSheet("margin-bottom: 6px; color: #555;")
        customer_layout.addWidget(self.customer_info_label)
        edit_customer_btn = QPushButton("Edit Customer Info")
        edit_customer_btn.setStyleSheet("padding: 4px 18px; background: #e3eaff; border-radius: 5px;")
        edit_customer_btn.clicked.connect(self.show_customer_dialog)
        customer_layout.addWidget(edit_customer_btn)
        layout.addWidget(customer_box)

        # Invoice Items Section
        items_box = QGroupBox("Invoice Items")
        items_box.setStyleSheet("QGroupBox { font-weight: bold; font-size: 15px; margin-top: 10px; } QGroupBox:title { subcontrol-origin: margin; left: 10px;}")
        items_box_layout = QVBoxLayout(items_box)
        items_box_layout.setSpacing(8)

        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.items_container = QVBoxLayout(scroll_widget)
        self.items_container.setSpacing(4)
        scroll.setWidget(scroll_widget)
        scroll.setMinimumHeight(180)
        scroll.setMaximumHeight(320)
        items_box_layout.addWidget(scroll)

        # Add Item button
        add_button = QPushButton("+ Add Item")
        add_button.setStyleSheet("padding: 7px 20px; font-weight: bold; background: #e3f7e8; border-radius: 6px;")
        add_button.clicked.connect(self.add_item_row)
        items_box_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(items_box)

        self.items = []
        self.add_item_row()

        # Bottom section (total and generate button)
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_label = QLabel("Total Amount: $")
        total_label.setStyleSheet("font-size: 18px;font-weight: bold;")
        total_layout.addWidget(total_label)
        self.total_label = QLabel("0.00")
        self.total_label.setStyleSheet("font-size: 22px; color: #2d5a8e; font-weight: bold;")
        total_layout.addWidget(self.total_label)
        bottom_layout.addWidget(total_widget)
        bottom_layout.addStretch()

        generate_button = QPushButton("Generate Invoice")
        generate_button.clicked.connect(self.generate_invoice)
        generate_button.setStyleSheet("padding: 12px 32px; font-size: 16px; font-weight: bold; background: #2d5a8e; color: white; border-radius: 8px;")
        generate_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        bottom_layout.addWidget(generate_button)

        layout.addWidget(bottom_widget)
        main_widget.setLayout(layout)
    
    def show_settings(self):
        dialog = CompanySettingsDialog(self, self.company_settings)
        if dialog.exec():
            self.company_settings = dialog.get_settings()
            self.save_settings(self.company_settings)
    
    def show_customer_dialog(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.customer_info = dialog.get_customer_info()
            # Update summary label
            info = self.customer_info
            summary = f"<b>{info['name']}</b><br>{info['email']}<br>{info['address']}"
            self.customer_info_label.setText(summary)
            QMessageBox.information(self, "Customer Info Saved", "Customer information has been updated.")
    
    def show_product_dialog(self):
        dialog = ProductDialog(self)
        dialog.exec()
    
    def new_invoice(self):
        # Clear all items
        for name, price, qty in self.items:
            name.deleteLater()
            price.deleteLater()
            qty.deleteLater()
        self.items.clear()

        # Reset customer info
        self.customer_info = None
        
        # Add one empty row
        self.add_item_row()
        # Only call update_total after items and UI are ready
        self.update_total()

    def add_item_row(self):
        # Only allow adding rows after total_label exists
        if not hasattr(self, 'total_label'):
            return
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setSpacing(8)
        row.setStyleSheet("background: #fbfbfb; border: 1px solid #e0e0e0; border-radius: 6px; padding: 4px 0;")

        # Fetch products for dropdown/autocomplete
        products = products_db.get_products()
        product_names = [f"#{pid}: {name}" for pid, name, desc, price in products]

        # Product ComboBox with autocomplete
        name_combo = QComboBox()
        name_combo.setEditable(True)
        name_combo.addItems(product_names)
        completer = QCompleter(product_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        name_combo.setCompleter(completer)
        name_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        name_combo.setPlaceholderText("Select or type product")
        name_combo.setMinimumWidth(180)
        row_layout.addWidget(name_combo)

        price = QLineEdit()
        price.setPlaceholderText("Price")
        price.setFixedWidth(80)
        price.textChanged.connect(self.update_total)
        row_layout.addWidget(price)

        qty = QLineEdit()
        qty.setPlaceholderText("Qty")
        qty.setFixedWidth(60)
        qty.textChanged.connect(self.update_total)
        row_layout.addWidget(qty)

        # Delete row button
        del_btn = QPushButton()
        del_btn.setIcon(QIcon.fromTheme("edit-delete"))
        del_btn.setText("")
        del_btn.setStyleSheet("background: #ffeaea; border-radius: 5px; font-size: 18px; padding: 2px 8px;")
        del_btn.setFixedWidth(38)
        def remove_row():
            row.setParent(None)
            self.items = [t for t in self.items if t[0] is not name_combo]
            self.update_total()
        del_btn.clicked.connect(remove_row)
        row_layout.addWidget(del_btn)

        # Auto-fill price when product is selected or typed
        def set_price_from_selection():
            idx = name_combo.currentIndex()
            if idx >= 0 and idx < len(products):
                price.setText(str(products[idx][3]))
            else:
                price.clear()
        name_combo.currentIndexChanged.connect(set_price_from_selection)

        # Auto-fill price when typing matches a product
        def handle_edit_text(text):
            text = text.strip().lower()
            for i, (pid, name, desc, prc) in enumerate(products):
                if text == f"#{pid}: {name}".lower() or text == name.lower():
                    price.setText(str(prc))
                    return
            price.clear()
        name_combo.lineEdit().textEdited.connect(handle_edit_text)

        # Prepopulate price if first product exists
        if products:
            price.setText(str(products[0][3]))

        self.items.append((name_combo, price, qty))
        self.items_container.addWidget(row)
        name_combo.setFocus()
    
    def update_total(self):
        total = 0
        for name_widget, price, qty in self.items:
            # name_widget can be QLineEdit (old) or QComboBox (new)
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
            
        # Ensure the invoices directory exists
        invoices_dir = os.path.expanduser("~/Documents/invoices")
        os.makedirs(invoices_dir, exist_ok=True)
        filename = os.path.join(
            invoices_dir,
            f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Add company logo
        if self.company_settings.get('logo_path'):
            try:
                # Calculate aspect ratio to fit in 100x50 space
                img = Image(self.company_settings['logo_path'])
                aspect = img.imageWidth / img.imageHeight
                if aspect > 2:  # wider than 2:1
                    img.drawHeight = 50
                    img.drawWidth = 100
                else:
                    img.drawHeight = 50
                    img.drawWidth = int(50 * aspect)
                img.wrapOn(c, width, height)
                img.drawOn(c, 50, height - 120)
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
        
        for name_widget, price, qty in self.items:
            # name_widget can be QLineEdit or QComboBox
            if hasattr(name_widget, 'currentText'):
                item_name = name_widget.currentText()
            else:
                item_name = name_widget.text()
            if item_name and price.text() and qty.text():
                try:
                    p = float(price.text())
                    q = float(qty.text())
                    item_total = p * q
                    total += item_total
                    data.append([
                        item_name,
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

        # Open the invoice PDF after saving
        try:
            if sys.platform == "darwin":
                os.system(f"open '{filename}'")
            elif sys.platform == "win32":
                os.startfile(filename)
            else:
                os.system(f"xdg-open '{filename}'")
        except Exception as e:
            QMessageBox.warning(self, "Open File Error", f"Could not open invoice: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("IMG_4309.PNG"))
    window = InvoiceApp()
    window.setWindowIcon(QIcon("IMG_4309.PNG"))
    window.show()
    sys.exit(app.exec())
