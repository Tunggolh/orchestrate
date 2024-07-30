# Orchestrate

## A Task Management Web Application for Organizations

> A Project to Focused on Learning and Applying Test-Driven Development

## Setup

### Prerequisites

- Python

### Backend Setup

1. **Clone the Repository:**

   ```bash
   git clone git@github.com:Tunggolh/orchestrate.git
   ```

2. **Navigate to orchestrate directory**

   ```bash
   cd orchestrate
   ```

3. **Create virtual environment**

   ```bash
   python -m venv .venv
   ```

4. **Activate virtual environment**

   _Windows_

   ```bash
   .venv\Scripts\activate
   ```

   _Mac_

   ```bash
   source .venv/bin/activate
   ```

5. **Install required packages**

   ```bash
   pip install -r requirements.txt
   ```

6. **Run command**

   ```bash
   python manage.py migrate
   ```

7. **Run server**
   ```bash
   python manage.py runserver
   ```

## Swagger UI

To view API documentation, replace `<your_server_address>` with your actual server address (including port) and go to:

`<your_server_address>/api/schema/swagger-ui/`

Example:

`http://localhost:8000/api/schema/swagger-ui/`
