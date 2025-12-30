# Vehicle Parking App V1

## Project Overview
This is a Flask-based web application for managing vehicle parking. It provides interfaces for users to book and release parking spots, and for administrators to manage parking lots, view occupancy, and analyze summaries.

## Technology Stack
- **Language:** Python 3
- **Framework:** Flask
- **Database:** PostgreSQL (via SQLAlchemy)
- **ORM:** Flask-SQLAlchemy
- **Frontend:** Jinja2 Templates (HTML)

## Project Structure
- **`app.py`**: The application entry point. Handles configuration, database initialization, and imports controllers.
- **`models/`**: Contains database schemas.
    - `database.py`: Initializes the SQLAlchemy instance.
    - `user_model.py`: User and Admin models.
    - `parking_model.py`: ParkingLot, ParkingSpot, etc.
- **`controllers/`**: Contains route handlers and business logic.
    - `admincontorllers.py`: Admin-specific routes (dashboard, lot management).
    - `usercontrollers.py`: User-specific routes (booking, dashboard).
- **`templates/`**: HTML templates for the UI.

## Setup and Running

1.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```
    *Note: The `README.md` may mention `main.py`, but `app.py` is the correct entry point.*

4.  **Access the App:**
    - Open `http://127.0.0.1:5000` in your browser.
    - **Default Admin Credentials:** The app creates a default admin user on first run if one doesn't exist.
        - Password: `admin` (See `app.py` logic)
