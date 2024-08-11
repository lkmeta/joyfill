from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from loguru import logger
import re
from app.models import generate_bert_suggestions, filter_positive_suggestions
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

# Define base directories using pathlib
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"

# Ensure the logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure Loguru to write logs to the logs directory
logger.add(
    LOGS_DIR / "app.log", rotation="1 MB", retention="10 days", compression="zip"
)

# JWT configuration
SECRET_KEY = "secure-secret-key"  # Secure secret key, temporary value for testing
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy user data
users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpassword"),
    }
}

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def verify_password(plain_password, hashed_password):
    """
    Verify the provided plain password against the hashed password stored in the database.

    Args:
        plain_password (str): The plain text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    """
    Authenticate the user by validating the username and password.

    Args:
        username (str): The username provided by the user.
        password (str): The plain text password provided by the user.

    Returns:
        dict or bool: The user data if authentication is successful, False otherwise.
    """
    user = users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT token for the authenticated user.

    Args:
        data (dict): The data to be included in the JWT token (e.g., the username).
        expires_delta (timedelta, optional): The token expiration time. Defaults to 30 minutes.

    Returns:
        str: The generated JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token", response_class=JSONResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to authenticate the user and return a JWT token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        JSONResponse: A JSON response containing the JWT token and token type.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        token (str): The JWT token provided in the Authorization header.

    Returns:
        dict: The authenticated user's data.

    Raises:
        HTTPException: If the token is invalid or the user cannot be authenticated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


@app.get("/", response_class=HTMLResponse)
# async def read_form(
#     request: Request, current_user: str = Depends(get_current_user)
# ) -> HTMLResponse:
async def read_form(request: Request) -> HTMLResponse:
    """
    Render the main form for JoyFill. Requires the user to be authenticated.

    Args:
        request (Request): The request object.
        current_user (str): The authenticated user's data (injected by Depends).

    Returns:
        HTMLResponse: The response containing the rendered index.html template.
    """
    logger.info("Rendering the main form page.")
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException) -> HTMLResponse:
    """
    Handle 404 errors and display the custom error page.

    Args:
        request (Request): The request object.
        exc (HTTPException): The exception object representing the 404 error.

    Returns:
        HTMLResponse: The response containing the rendered error.html template.
    """
    logger.warning(f"404 error encountered: {request.url}")
    # Skip logging for favicon.ico requests
    if "favicon.ico" not in str(request.url):
        logger.warning(f"404 error encountered: {request.url}")

    return templates.TemplateResponse(
        "error.html", {"request": request}, status_code=status.HTTP_404_NOT_FOUND
    )


# Function to validate the input format
def validate_input_format(text: str) -> bool:

    if "<blank>" not in text:
        return False

    # if multiple <blank> in the text return False
    if text.count("<blank>") > 1:
        return False

    pattern = r"\b\w*\b\s*<blank>\s*\b\w*\b|\b\w+\s*<blank>\s*|\s*<blank>\s*\b\w+\b"
    return bool(re.search(pattern, text))


@app.post("/suggestions", response_class=JSONResponse)
async def get_suggestions(text: str = Form(...)) -> JSONResponse:
    """
    Process the user's input and return positive suggestions to fill in the blank.
    Validate the input format is 'word <blank> word'.
    """
    logger.info(f"Received input text: {text}")

    # Remove multiple spaces and leading/trailing spaces
    text = re.sub(r"\s+", " ", text).strip()

    # logger.info(f"Processed input text: {text}")

    # Validate the input format
    if not validate_input_format(text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Please use the format 'word <blank> word'.",
        )

    # Replace <blank> with [MASK] for BERT model
    masked_text = text.replace("<blank>", "[MASK]")

    # Get suggestions using the BERT model
    # suggestions = generate_bert_suggestions(masked_text, top_k=3)
    suggestions = generate_bert_suggestions(masked_text, top_k=10)

    # Remove spaces beetwen words
    suggestions = [suggestion.replace(" ", "") for suggestion in suggestions]

    logger.info(f"Returning suggestions: {suggestions}")

    # Filter suggestions to keep only the positive ones
    positive_suggestions = filter_positive_suggestions(suggestions)

    logger.info(f"Returning filtered suggestions: {positive_suggestions}")

    return JSONResponse({"suggestions": positive_suggestions[:5]})


# Custom 400 error handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions and display a custom error page.
    """
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": exc.detail},
        status_code=exc.status_code,
    )
