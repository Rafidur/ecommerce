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
