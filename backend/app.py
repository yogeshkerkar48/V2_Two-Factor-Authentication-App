from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
import pyotp
import qrcode
import pymysql
from io import BytesIO
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from fastapi.responses import RedirectResponse


load_dotenv()
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="SESSION_SECRET_KEY")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Redirect root to docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to MySQL
db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

# Create users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(150) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        secret VARCHAR(255),
        is_2fa_enabled BOOLEAN DEFAULT FALSE
    )
''')
db.commit()

def get_db():
    try:
        yield db
    finally:
        pass  # Connection kept open for simplicity, close if needed

@app.get("/register")
async def register_form(request: Request):
    flash_message = request.session.pop('flash', None)
    return JSONResponse({"message": flash_message or "", "redirect": None})

@app.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: pymysql.connections.Connection = Depends(get_db)
):
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    if cursor.fetchone():
        request.session['flash'] = 'Username already exists'
        return JSONResponse({"message": "Username already exists", "redirect": "/register"})
    
    hashed_password = generate_password_hash(password)
    sql = 'INSERT INTO users (username, password_hash) VALUES (%s, %s)'
    cursor.execute(sql, (username, hashed_password))
    db.commit()

    request.session['flash'] = 'Account created! Please log in.'
    return JSONResponse({"message": "Account created! Please log in.", "redirect": "/login"})

@app.get("/login")
async def login_form(request: Request):
    flash_message = request.session.pop('flash', None)
    return JSONResponse({"message": flash_message or "", "redirect": None})

@app.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: pymysql.connections.Connection = Depends(get_db)
):
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user[2], password): # user[2] is password_hash
        request.session.pop('flash', None)  
        if user[4]:  # user[4] is is_2fa_enabled
            request.session['user_id_temp'] = user[0]  # user[0] is id
            return JSONResponse({"message": "", "redirect": "/verify_2fa"})
        else:
            request.session['user_id'] = user[0]
            return JSONResponse({"message": "", "redirect": "/dashboard"})
    
    request.session['flash'] = 'Invalid username or password'
    return JSONResponse({"message": "Invalid username or password", "redirect": "/login"})

@app.get("/verify_2fa")
async def verify_2fa_form(request: Request):
    if 'user_id_temp' not in request.session:
        request.session['flash'] = 'Please log in first'
        return JSONResponse({"message": "Please log in first", "redirect": "/login"})
    flash_message = request.session.pop('flash', None)
    return JSONResponse({"message": flash_message or "", "redirect": None})

@app.post("/verify_2fa")
async def verify_2fa(
        request: Request,
        otp: str = Form(...),
        db: pymysql.connections.Connection = Depends(get_db)
):
    if 'user_id_temp' not in request.session:
        request.session['flash'] = 'Please log in first'
        return JSONResponse({"message": "Please log in first", "redirect": "/login"})

    cursor.execute('SELECT * FROM users WHERE id = %s', (request.session['user_id_temp'],))
    user = cursor.fetchone()
    if not user:
        request.session['flash'] = 'User not found'
        return JSONResponse({"message": "User not found", "redirect": "/login"})

    secret = user[3].strip()  # user[3] is secret
    totp = pyotp.TOTP(secret)
    if totp.verify(otp, valid_window=1):
        request.session.pop('user_id_temp', None)
        request.session['user_id'] = user[0]
        return JSONResponse({"message": "", "redirect": "/dashboard"})
    
    request.session['flash'] = 'Invalid 2FA code'
    return JSONResponse({"message": "Invalid 2FA code", "redirect": "/verify_2fa"})

@app.get("/dashboard")
async def dashboard(request: Request, db: pymysql.connections.Connection = Depends(get_db)):
    if 'user_id' not in request.session:
        request.session['flash'] = 'Please log in to access this page'
        return JSONResponse({"message": "Please log in to access this page", "redirect": "/login"})

    cursor.execute('SELECT username, is_2fa_enabled FROM users WHERE id = %s', (request.session['user_id'],))
    user = cursor.fetchone()
    if not user:
        request.session['flash'] = 'User not found'
        return JSONResponse({"message": "User not found", "redirect": "/login"})

    flash_message = request.session.pop('flash', None)
    return JSONResponse({
        "message": flash_message or "",
        "username": user[0],
        "is_2fa_enabled": user[1],
        "redirect": None
    })

@app.get("/enable_2fa")
async def enable_2fa_form(request: Request, db: pymysql.connections.Connection = Depends(get_db)):
    if 'user_id' not in request.session:
        request.session['flash'] = 'Please log in to enable 2FA'
        return JSONResponse({"message": "Please log in to enable 2FA", "redirect": "/login"})

    cursor.execute('SELECT * FROM users WHERE id = %s', (request.session['user_id'],))
    user = cursor.fetchone()
    if not user:
        request.session['flash'] = 'User not found'
        return JSONResponse({"message": "User not found", "redirect": "/login"})

    if user[4]:  # user[4] is is_2fa_enabled
        request.session['flash'] = '2FA is already enabled'
        return JSONResponse({"message": "2FA is already enabled", "redirect": "/dashboard"})

    # Generate QR code
    secret = pyotp.random_base32()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user[1], issuer_name='MyApp')  # user[1] is username
    img = qrcode.make(uri)
    buffered = BytesIO()
    img.save(buffered)
    qr_code = base64.b64encode(buffered.getvalue()).decode()

    flash_message = request.session.pop('flash', None)
    return JSONResponse({
        "message": flash_message or "",
        "qr_code": qr_code,
        "secret": secret,
        "redirect": None
    })

@app.post("/enable_2fa")
async def enable_2fa(
        request: Request,
        secret: str = Form(...),
        db: pymysql.connections.Connection = Depends(get_db)
):
    if 'user_id' not in request.session:
        request.session['flash'] = 'Please log in to enable 2FA'
        return JSONResponse({"message": "Please log in to enable 2FA", "redirect": "/login"})

    cursor.execute('SELECT * FROM users WHERE id = %s', (request.session['user_id'],))
    user = cursor.fetchone()
    if not user:
        request.session['flash'] = 'User not found'
        return JSONResponse({"message": "User not found", "redirect": "/login"})

    if user[4]:  # user[4] is is_2fa_enabled
        request.session['flash'] = '2FA is already enabled'
        return JSONResponse({"message": "2FA is already enabled", "redirect": "/dashboard"})

    sql = 'UPDATE users SET secret = %s, is_2fa_enabled = %s WHERE id = %s'
    cursor.execute(sql, (secret, True, request.session['user_id']))
    db.commit()

    request.session['flash'] = '2FA enabled successfully. Use your authenticator app to get the code.'
    return JSONResponse({"message": "2FA enabled successfully. Use your authenticator app to get the code.", "redirect": "/dashboard"})

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user_id', None)
    request.session.pop('user_id_temp', None)
    request.session['flash'] = 'Logged out successfully'
    return JSONResponse({"message": "Logged out successfully", "redirect": "/login"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)