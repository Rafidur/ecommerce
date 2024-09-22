[# FastAPI Customer Management Application

## Overview

This project is a FastAPI-based web application designed for managing customers and their orders. It includes features for customer registration, order placement, and JWT authentication.

## Features

- **Customer Management**: Create, read, update, and delete customer profiles.
- **Order Management**: Place orders with associated products and manage their statuses.
- **JWT Authentication**: Secure API endpoints using JWT tokens.
- **Address Management**: Manage customer addresses, including setting default addresses.

## Technologies Used

- **FastAPI**: For building the API.
- **SQLAlchemy**: For database interaction.
- **PostgreSQL**: As the database.
- **Pydantic**: For data validation and serialization.
- **Bcrypt**: For password hashing.
- **JOSE**: For creating and verifying JWT tokens.

## Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL
- `pip` for installing Python packages

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Rafidur/ecommerce.git
   cd ecommerce

   
Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`


Install the required dependencies:
pip install -r requirements.txt


Run the application:
uvicorn app.main:app --reload
](https://github.com/Rafidur/ecommerce/tree/main

# FastAPI Customer Management Application

## Overview

This project is a FastAPI-based web application designed for managing customers and their orders. It includes features for customer registration, order placement, and JWT authentication.

## Features

- **Customer Management**: Create, read, update, and delete customer profiles.
- **Order Management**: Place orders with associated products and manage their statuses.
- **JWT Authentication**: Secure API endpoints using JWT tokens.
- **Address Management**: Manage customer addresses, including setting default addresses.

## Technologies Used

- **FastAPI**: For building the API.
- **SQLAlchemy**: For database interaction.
- **PostgreSQL**: As the database.
- **Pydantic**: For data validation and serialization.
- **Bcrypt**: For password hashing.
- **JOSE**: For creating and verifying JWT tokens.





















## Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL
- `pip` for installing Python packages




### Installation

Clone the repository:
   
   git clone https://github.com/Rafidur/ecommerce.git
   cd ecommerce

   
Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`


Install the required dependencies:
pip install -r requirements.txt


Run the application:
uvicorn app.main:app --reload















Application Overview
Purpose

This project is a FastAPI-based web application designed for managing customers and their orders. It includes features for customer registration, order placement, and JWT authentication. It supports both authenticated customer orders and guest orders.
Key Features
- User Authentication
JWT authentication for customers to secure their accounts.
Routes to register and log in users.
- Customer Management
Customers can create accounts, update their details, and view their account information.
Option for guest users to place orders without creating an account.
- Order Management
Customers can create new orders, including selecting products and variants.
Orders can be created for both authenticated customers and guest users.
Each order tracks details such as the total price, order status, and customer information.
- Product and Variant Handling
The application manages products, including their variants (e.g., sizes, colors).
It checks stock levels for products and their variants when creating orders to ensure sufficient inventory.
- Order Status Updates
Support for updating the status of orders (e.g., pending, confirmed, shipped, delivered, canceled).
Admin or managerial roles can manage order statuses as required.
- Order Retrieval
Customers can retrieve their orders using their customer ID or email.
The application provides endpoints to fetch all orders, specific orders by ID, and orders associated with a particular customer.
- Error Handling
Comprehensive error handling for various scenarios, such as insufficient stock, invalid input, and not found resources.
- Database Integration
Uses SQLAlchemy for ORM functionality, allowing for easy interaction with the database for creating, reading, updating, and deleting records.



Data Models
- Customer: Stores customer information, including email, name, and account status.
- Product: Represents the products available for order, including pricing and stock information.
- Variant: Details variations of products (e.g., different sizes or colors).
- Order: Captures order details, including customer info, order items, status, and total price.
- OrderItem: Links products and variants to specific orders, detailing the quantity and price per unit.

)
