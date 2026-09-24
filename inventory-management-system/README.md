# Inventory Management System

A simple web application for managing products and their stock.

## Features

- Dashboard with inventory statistics
- Add products
- View products
- Edit products
- Delete products
- Search products by name
- Add stock
- Remove stock
- Low-stock warning for quantity below 5
- Basic form validation
- JSON file storage
- Responsive interface

## Technologies

- Python
- Flask
- HTML
- CSS
- JavaScript
- JSON

## Project Structure

```text
inventory-management-system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── products.json
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── add_product.html
│   └── edit_product.html
│
└── static/
    └── style.css
```

## Installation

Open the project folder in a terminal and install the required package:

```bash
pip install -r requirements.txt
```

## Run

Start the application:

```bash
python app.py
```

Open the local Flask address shown in the terminal.

## Data

Product information is stored in:

```text
data/products.json
```

The application creates the `data` folder and JSON file automatically if they do not exist.

## Future Improvements

- User login
- Supplier management
- Sales and purchase management
- Barcode scanning
- Reports
- Database integration
- PDF/Excel export
- Email notifications
