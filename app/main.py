from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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


app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request) -> HTMLResponse:
    """
    Render the main form for JoyFill.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: The response containing the rendered index.html template.
    """
    logger.info("Rendering the main form page.")
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@app.post("/suggestions", response_class=JSONResponse)
async def get_suggestions(text: str = Form(...)) -> JSONResponse:
    """
    Process the user's input and return positive suggestions to fill in the blank.

    Args:
        text (str): The user's input with a blank space.

    Returns:
        JSONResponse: A JSON response containing a list of positive suggestions.
    """
    logger.debug(f"Received input text: {text}")
    # Placeholder for NLP processing and sentiment filtering
    suggestions: list[str] = [
        "good",
        "excellent",
        "amazing",
    ]  # Replace this with actual NLP model output

    logger.info(f"Suggestions generated: {suggestions}")
    return JSONResponse({"suggestions": suggestions})


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """
    Handle 404 errors and display the custom error page.

    Args:
        request (Request): The request object.
        exc (HTTPException): The exception object representing the 404 error.

    Returns:
        HTMLResponse: The response containing the rendered error.html template.
    """
    logger.warning(f"404 error encountered: {request.url}")
    return templates.TemplateResponse(
        "error.html", {"request": request}, status_code=404
    )
