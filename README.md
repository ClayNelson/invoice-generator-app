# Invoice Generator

A professional invoice generation application with a modern user interface.

## Features
- Easy-to-use graphical interface
- Company profile management with logo
- Customer information management
- Multiple invoice items with automatic total calculation
- Professional PDF invoice generation
- Settings persistence between sessions

## Installation

### Option 1: Run the Executable (Recommended for testing)
1. Download the `InvoiceGenerator.zip` file
2. Extract the contents
3. Double-click the `InvoiceGenerator` application

### Option 2: Run from Source
If you want to run from source code, you'll need Python 3.8 or newer installed.

1. Clone or download this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python invoice_app.py
```

## Usage

1. First Time Setup:
   - Go to File → Company Settings
   - Enter your company information
   - Upload your company logo (optional)
   - Click OK to save

2. Creating an Invoice:
   - Click "New Invoice"
   - Enter customer information in the popup
   - Add items using the "Add Item" button
   - Enter item details (name, price, quantity)
   - The total updates automatically
   - Click "Generate Invoice" to create the PDF

3. Generated invoices will be saved in the same folder as the application

## Known Limitations
- The application stores settings locally in the same directory
- Generated PDFs are saved in the application directory
- Company logo should be a reasonable size (recommended: 300x150 pixels or smaller)

## Support
For support or bug reports, please contact [Your Contact Information]
