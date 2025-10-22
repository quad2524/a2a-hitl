# Testing Guide

This document provides a comprehensive guide to testing the Human-in-the-Loop Agent Demo application.

## 1. Environment Setup

First, install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## 2. Configuration

### a. Google Vertex AI Configuration

The application uses Google's Vertex AI service. To connect to this service, you need to configure your environment:

1.  Create a `.env` file in the root of the project.
2.  Add the following line to the `.env` file, specifying the model you want to use:

    ```
    MODEL_NAME=gemini-1.0-pro
    ```

### b. Google Cloud Authentication

The application requires authentication to access Google Cloud services. The recommended way to authenticate in a local development environment is to use Application Default Credentials (ADC).

1.  Install the Google Cloud CLI. You can find instructions [here](https://cloud.google.com/sdk/docs/install).

2.  Once the `gcloud` CLI is installed, run the following command to log in and create your application default credentials:

    ```bash
    gcloud auth application-default login
    ```

    This will open a browser window for you to complete the authentication process.

## 3. Running the Application

To run the application, you need to start both the backend and frontend servers in separate terminals.

1.  **Start the backend server:**

    ```bash
    uvicorn agent.main:app --host 127.0.0.1 --port 8000
    ```

2.  **Start the frontend application:**

    ```bash
    python app.py
    ```

## 4. End-to-End Testing with Playwright

We use Playwright for end-to-end testing of the user interface.

1.  **Install Playwright and its dependencies:**

    ```bash
    pip install playwright
    playwright install --with-deps
    ```

2.  **Create a test script:**

    Create a Python file (e.g., `test_app.py`) with the following content:

    ```python
    from playwright.sync_api import sync_playwright

    def run(playwright):
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:7860")
        page.wait_for_selector("textarea")
        page.fill("textarea", "roll a 20 sided die")
        page.press("textarea", "Enter")
        page.wait_for_selector("text=You rolled a")
        page.screenshot(path="verification.png")
        browser.close()

    with sync_playwright() as playwright:
        run(playwright)
    ```

3.  **Run the test:**

    ```bash
    python test_app.py
    ```

    This will launch a headless browser, interact with the application, and save a screenshot named `verification.png` in the project root.

## 5. Mocking the Backend for Testing

If you need to test the application's functionality without connecting to the Google Vertex AI service, you can mock the backend to return a canned response.

1.  Open `agent/main.py` and comment out the `vertexai.init()` line:

    ```python
    # vertexai.init()
    ```

2.  Replace the `ask` function with the following mocked version:

    ```python
    @app.post("/ask")
    async def ask(request: AskRequest):
        logging.info(f"Received request: {request}")
        user_query = request.history[-1]['content']
        logging.info(f"User query: {user_query}")
        if "roll" in user_query:
            return {"response": "You rolled a 10"}
        elif "prime" in user_query:
            return {"response": "10 is not a prime number."}
        else:
            return {"response": "I'm a mocked response."}
    ```

3.  Restart the backend server. You can now run the Playwright test, and it will use the mocked response.
