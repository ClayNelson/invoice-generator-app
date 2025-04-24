# Invoice Generator

[![Build and Test](https://github.com/ClayNelson/invoice-generator-app/actions/workflows/build.yml/badge.svg)](https://github.com/ClayNelson/invoice-generator-app/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/ClayNelson/invoice-generator-app/branch/main/graph/badge.svg)](https://codecov.io/gh/ClayNelson/invoice-generator-app)

A professional invoice generator application built with PyQt6. Create, customize, and export beautiful invoices with ease.

## Features

- Modern and intuitive GUI interface
- Company profile management with logo support
- Customer information management
- Dynamic item addition and total calculation
- Professional PDF invoice generation
- Cross-platform support (Intel and Apple Silicon Macs)

## Installation

### Download Pre-built Binaries

1. Go to the [Releases](https://github.com/ClayNelson/invoice-generator-app/releases) page
2. Download the appropriate version for your system:
   - `InvoiceGenerator-intel.zip` for Intel Macs
   - `InvoiceGenerator-arm64.zip` for Apple Silicon Macs
3. Extract the ZIP file
4. Run the application

### Build from Source

```bash
# Clone the repository
git clone https://github.com/ClayNelson/invoice-generator-app.git
cd invoice-generator-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python invoice_app.py
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Testing

The project uses pytest for testing. Run the test suite:

```bash
pytest tests/ -v
```

To run tests with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
