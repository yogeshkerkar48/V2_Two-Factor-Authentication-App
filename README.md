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
DB_NAME=database
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
├──          
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
   uvicorn app:app --host localhost --port 8000 --reload
   ```

### Frontend Setup
1. Navigate to `frontend/`:
   ```bash
   cd version2/frontend
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

- Test the full flow in the browser at `http://localhost:8080`.

## Dockerization Setup Process for 2FA Application

This document provides a step-by-step guide to set up and dockerize the 2FA (Two-Factor Authentication) application, consisting of a FastAPI backend, a Vue.js frontend, and a MySQL database. The setup uses Docker to containerize the application, ensuring portability and consistency across development, testing, and production environments.

### Overview
- **Application Components**:
  - **Backend**: FastAPI-based API for user registration, login, and 2FA management.
  - **Frontend**: Vue.js application served via Nginx.
  - **Database**: MySQL 8.0 for storing user data.

- **Software**:
  - Docker Desktop installed and running.
  - Python 3.11 (for local backend development).
  - Node.js and npm (for local frontend development).
- **Account**:
  - Docker Hub account (for pushing images).

### Project Structure
```

└───AUTHETICATORAPP
    │   docker-compose.yml
    │   .env
    │   .dockerignore
    │
    └───backend
    │   │   Dockerfile
    │   │   app.py
    │   │   requirements.txt
    │   │   .dockerignore
    │
    └───frontend
        ├   App.vue       
        ├   main.js       
        │   Dockerfile
        │   package.json
        │   src/views/   #all 5 view files
        │   package-lock.json
        |   src/router/index.js
        │   .dockerignore
        │    index.html
        |    vite.config.js 

```

### Setup Process
#### 1. Install Docker and Dependencies
- Download and install Docker Desktop 
- Enable WSL 2:
  - Run `wsl --install` in PowerShell (as Administrator).
  
- Verify installation:
  ```CMD
  docker --version

#### 2. Prepare the Project Directory
- COPY the project to `VERSION2AUTHETICATOR directory`.
- Ensure the following files exist:
  - `docker-compose.yml`: Defines services (db, backend, frontend).
  - `VERSION2AUTHETICATOR/.env`: Contains environment variables.
  - `.dockerignore`: Excludes sensitive files from the build.
  - `backend/Dockerfile`: Builds the FastAPI image.
  - `frontend/Dockerfile`: Builds the Vue.js image.
  - `requirements.txt`: Lists Python dependencies.

#### 4. Create `.dockerignore` Files
- Prevent sensitive files (e.g., `.env`) from being copied into images.

#### 5. Build and Run the Application
- Navigate to the project directory:
  ```VS CODE
  cd "D:\VERSION2AUTHETICATOR"
  ```
- Build the images:
  ```VS CODE
  docker-compose build
  ```
- Start the containers:
  ```VS CODE
  docker-compose up -d
  ```
- Verify container status:
  ```VS CODE
  docker-compose ps
  ```
  - Expected: All three containers (`VERSION2AUTHETICATOR-backend`, `VERSION2AUTHETICATOR-db`, `VERSION2AUTHETICATOR-frontend`) show `Up`.

#### 6. Test the Application
- **Frontend**: Open `http://localhost:8080` in a browser to verify the UI.
- **Backend**: Access `http://localhost:8000/docs` for the API documentation.
- **Registration/Login**: Test user registration and login with 2FA.
- **Data Verification**: Connect to MySQL:
  ```VS CODE
  docker-compose exec db mysql -u app_user -psecurepassword123 2fa_db
  ```
  - Run: `SELECT * FROM users;` to view stored data.

#### 7. Troubleshoot Common Issues
- **Container Not Starting**:
  - Check logs: `docker-compose logs <service>` (e.g., `backend`).
  - Ensure dependencies (e.g., `python-multipart`) are in `requirements.txt`.
- **Connection Refused**:
  - Verify `DB_HOST` is `db` and MySQL is ready .
- **Docker Desktop Empty**:
  - Restart Docker Desktop .
  

#### 8. Push to Docker Hub 
- Log in:
  ```VS CODE
  docker login
  ```
- Tag images:
  ```VS CODE
  docker tag VERSION2AUTHETICATOR_backend:latest yourusername/VERSION2AUTHETICATOR-backend:latest
  docker tag VERSION2AUTHETICATOR_frontend:latest yourusername/VERSION2AUTHETICATOR-frontend:latest
  ```
- Push images:
  ```VS CODE
  docker push yourusername/VERSION2AUTHETICATOR-backend:latest
  docker push yourusername/VERSION2AUTHETICATOR-frontend:latest



#### `docker-compose.yml`

``` yaml
services:
  db:
    image: mysql:8.0
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - dbdata:/var/lib/mysql
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DB_HOST: ${DB_HOST}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: ${DB_NAME}
      SESSION_SECRET_KEY: ${SESSION_SECRET_KEY}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

volumes:
  dbdata:
```

#### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `frontend/Dockerfile`
```dockerfile
# Build stage
FROM node:18 AS build

WORKDIR /app

# Copy package files and install all dependencies (including dev deps for build)
COPY package.json package-lock.json ./
RUN npm ci  
# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```


### Conclusion
This process dockerizes the 2FA application, ensuring a reproducible setup. The data persists in the `dbdata` volume, and the application is accessible at `http://localhost:8080` (frontend) and `http://localhost:8000` (backend API).

## Dockerizing the setup of an application
- [YOUTUBE](https://www.youtube.com/watch?v=tV1pKMJDFZY)

## Use of AI Tools
- [GROK](https://grok.com/)
- [CHATGPT](https://chatgpt.com/)
