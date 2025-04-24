import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
import sys
from invoice_app import InvoiceApp, CompanySettingsDialog, CustomerInfoDialog

class TestInvoiceApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance for GUI tests
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.invoice_app = InvoiceApp()

    def test_add_item(self):
        # Test adding an item to the invoice
        initial_count = self.invoice_app.items_table.rowCount()
        self.invoice_app.add_item()
        self.assertEqual(self.invoice_app.items_table.rowCount(), initial_count + 1)

    def test_calculate_total(self):
        # Test total calculation
        self.invoice_app.items_table.setRowCount(2)
        
        # Set test values in the table
        self.invoice_app.items_table.setItem(0, 2, MagicMock(text=lambda: "10"))  # price
        self.invoice_app.items_table.setItem(0, 3, MagicMock(text=lambda: "2"))   # quantity
        self.invoice_app.items_table.setItem(1, 2, MagicMock(text=lambda: "15"))  # price
        self.invoice_app.items_table.setItem(1, 3, MagicMock(text=lambda: "3"))   # quantity

        self.invoice_app.calculate_total()
        expected_total = (10 * 2) + (15 * 3)  # 65
        self.assertEqual(float(self.invoice_app.total_label.text().split(": $")[1]), expected_total)

class TestCompanySettingsDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.dialog = CompanySettingsDialog()

    def test_save_settings(self):
        # Test saving company settings
        test_name = "Test Company"
        test_email = "test@company.com"
        test_address = "123 Test St"

        self.dialog.name_input.setText(test_name)
        self.dialog.email_input.setText(test_email)
        self.dialog.address_input.setPlainText(test_address)

        with patch('PyQt6.QtWidgets.QDialog.accept') as mock_accept:
            self.dialog.accept()
            mock_accept.assert_called_once()

        self.assertEqual(self.dialog.company_info["name"], test_name)
        self.assertEqual(self.dialog.company_info["email"], test_email)
        self.assertEqual(self.dialog.company_info["address"], test_address)

class TestCustomerInfoDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.dialog = CustomerInfoDialog()

    def test_save_customer_info(self):
        # Test saving customer information
        test_name = "Test Customer"
        test_email = "customer@test.com"
        test_address = "456 Customer Ave"

        self.dialog.name_input.setText(test_name)
        self.dialog.email_input.setText(test_email)
        self.dialog.address_input.setPlainText(test_address)

        with patch('PyQt6.QtWidgets.QDialog.accept') as mock_accept:
            self.dialog.accept()
            mock_accept.assert_called_once()

        self.assertEqual(self.dialog.customer_info["name"], test_name)
        self.assertEqual(self.dialog.customer_info["email"], test_email)
        self.assertEqual(self.dialog.customer_info["address"], test_address)

if __name__ == '__main__':
    unittest.main()
