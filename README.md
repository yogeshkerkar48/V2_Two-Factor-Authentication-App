# Project Title

Two-Factor Authentication (2FA) App

>   
This project is a Two-Factor Authentication web application featuring a distinct backend built with FastAPI (Python) and MySQL, and a separate frontend developed with Vue.js. The backend serves JSON APIs for user authentication and 2FA management, while the frontend handles the user interface and navigation. User credentials and 2FA secrets are stored in a MySQL database.

## Tech Stack

### Backend
- Framework: FastAPI (Python)
- Database: MySQL (accessed via PyMySQL)
- 2FA & Helpers: pyotp (TOTP generation/verification), qrcode (QR code image generation)
- Password Hashing: passlib (e.g., bcrypt through passlib.context.CryptContext)
- Env Management: python-dotenv (load .env)
- ASGI Server (dev): uvicorn
- Session Management: starlette.middleware.sessions (SessionMiddleware)
- CORS: fastapi.middleware.cors (for frontend communication)

### Frontend
- Framework: Vue.js (v3)
- Routing: vue-router (v4)
- HTTP Client: axios
- Build Tool: Vite
- Styling: Tailwind CSS (optional, for component styling)

## Database Setup

This authentication app relies on a MySQL database to store user credentials and related data.

1. Create the Database Application
2. Create a `users` table for storing user credentials:
   - The table includes:
     - `id` INT
     - `username` VARCHAR(150)
     - `password_hash` VARCHAR(255)
     - `secret` VARCHAR(255)
     - `is_2fa_enabled` BOOLEAN DEFAULT FALSE
3. Create a `.env` file in the project root directory to store database credentials.
4. Ensure the `.env` file is added to `.gitignore`.
5. The app uses the `pymysql` library to connect to MySQL. The connection is managed via a dependency (`get_db`) in the FastAPI application.
6. Run the FastAPI app using `uvicorn` to ensure the database setup works.
7. Access the registration page via the frontend and attempt to register a user.

## Environment Configuration

Create a `.env` file in the project root (this file must NOT be committed — add it to `.gitignore`). Example `.env` contents:

```
DB_HOST=localhost
DB_USER=twofa_user
DB_PASSWORD=strong_password
DB_NAME=twofa_app
SECRET_KEY=a_long_random_secret_for_sessions_or_signing
```

Add `.env` to `.gitignore`:

```
.env
```

Load `.env` in code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
```

## Project Structure

```
my-2fa-app/
├── app.py                # FastAPI backend code
├── .env                  # Environment variables
├── frontend/             # Vue.js frontend
│   ├── src/
│   │   ├── App.vue       # Root Vue component
│   │   ├── main.js       # Vue app entry point
│   │   ├── router/       # Routing configuration
│   │   │   ├── index.js  # Vue Router setup
│   │   ├── views/        # Vue components for each page
│   │   │   ├── RegisterView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── Enable2FAView.vue
│   │   │   ├── Verify2FAView.vue
│   ├── index.html        # Entry HTML file
│   ├── package.json      # Node.js project configuration
│   ├── vite.config.js    # Vite configuration
├── README (1).md         # This file
```

## API Design

### Clear Separation of Concerns
- The backend serves JSON APIs instead of rendering HTML, allowing a distinct frontend to consume them.
- Endpoints that retrieve data or forms return JSON (e.g., GET `/register`, GET `/login`).
- Endpoints that perform changes use POST and return JSON with a `redirect` field for frontend navigation (e.g., POST `/register`, POST `/login`).

### HTTP Verbs
- GET: Retrieval of initial form data or dashboard info (e.g., `/register`, `/dashboard`).
- POST: Actions like registration, login, enabling 2FA, and verifying 2FA (e.g., `/register`, `/verify_2fa`).
- GET: Logout action (e.g., `/logout`).

### Protection of Sensitive Flows
- Endpoints modifying authentication state (e.g., `/login`, `/enable_2fa`, `/verify_2fa`) return appropriate JSON responses with `message` and `redirect` fields.
- Success responses include a `redirect` to guide the frontend.
- Failures return a `message` with an error (e.g., "Invalid username or password") and a `redirect` back to the form.

### 2FA Flow (TOTP)
- **User Registration**: User provides username and password. Password is hashed and stored.
- **Enable 2FA**: 
  - User logs in, requests 2FA setup via `/enable_2fa`.
  - Backend generates a TOTP secret (`pyotp.random_base32()`), stores it in `secret`, and returns a QR code (base64 via `qrcode`).
  - User scans the QR code with an authenticator app and submits the first TOTP code.
  - Backend verifies the code with `pyotp.TOTP(otp_secret).verify(code)` and sets `is_2fa_enabled` to `true`.
- **Login with 2FA**: 
  - After verifying username/password, if `is_2fa_enabled` is `true`, the backend redirects to `/verify_2fa`.
  - User enters the TOTP code, which the backend verifies before establishing the session.

## Setup Instructions

### Backend Setup
1. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn pyotp qrcode[pil] pymysql python-dotenv passlib[bcrypt] starlette
   ```
2. Configure `.env` with MySQL credentials.
3. Run the backend:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```

### Frontend Setup
1. Navigate to `frontend/`:
   ```bash
   cd my-2fa-app/frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Run the frontend development server:
   ```bash
   npm run dev
   ```
4. Access the app at `http://localhost:8080`.

## Testing
- Use `curl` to test backend APIs:
  - Register: `curl -v -X POST http://localhost:8000/register -d "username=testuser&password=testpass" -c cookies.txt`
  - Login: `curl -v -X POST http://localhost:8000/login -d "username=testuser&password=testpass" -b cookies.txt -c cookies.txt`
  - Enable 2FA: `curl -v -b cookies.txt http://localhost:8000/enable_2fa`
  - Verify 2FA: `curl -v -X POST -b cookies.txt http://localhost:8000/verify_2fa -d "otp=<6-digit-OTP>"`
  - Dashboard: `curl -v -b cookies.txt http://localhost:8000/dashboard`
  - Logout: `curl -v -b cookies.txt http://localhost:8000/logout`
- Test the full flow in the browser at `http://localhost:8080`.

## Use of AI Tools
- CHATGPT
- GROK