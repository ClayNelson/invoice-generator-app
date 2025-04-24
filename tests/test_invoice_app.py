import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QLineEdit
import sys
from invoice_app import InvoiceApp

class TestInvoiceApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance for GUI tests
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.invoice_app = InvoiceApp()

    def test_add_item_row(self):
        # Test adding an item row
        initial_items = len(self.invoice_app.items)
        self.invoice_app.add_item_row()
        self.assertEqual(len(self.invoice_app.items), initial_items + 1)

    def test_update_total(self):
        # Test total calculation
        # Add test items
        self.invoice_app.add_item_row()
        item_index = len(self.invoice_app.items) - 1
        name, price, qty = self.invoice_app.items[item_index]
        
        # Set test values
        price.setText("10")
        qty.setText("2")
        
        self.invoice_app.update_total()
        expected_total = 20.0  # 10 * 2
        self.assertEqual(float(self.invoice_app.total_label.text().replace("Total: $", "")), expected_total)

    def test_new_invoice(self):
        # Test creating a new invoice
        # Set initial customer info
        self.invoice_app.customer_info = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'address': '123 Test St'
        }
        
        # Add some items first
        self.invoice_app.add_item_row()
        self.invoice_app.add_item_row()
        
        # Call new_invoice
        self.invoice_app.new_invoice()
        
        # Check that items were cleared
        self.assertEqual(len(self.invoice_app.items), 1)  # Should have one empty row
        self.assertIsNone(self.invoice_app.customer_info)

    def test_generate_invoice(self):
        # Test invoice generation
        self.invoice_app.customer_info = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'address': '123 Test St'
        }
        
        # Add a test item
        self.invoice_app.add_item_row()
        item_index = len(self.invoice_app.items) - 1
        name, price, qty = self.invoice_app.items[item_index]
        name.setText("Test Item")
        price.setText("10")
        qty.setText("2")

        with patch('invoice_app.QMessageBox') as mock_msg:
            self.invoice_app.generate_invoice()
            # Check that success message was shown
            mock_msg.information.assert_called_once()

if __name__ == '__main__':
    unittest.main()
