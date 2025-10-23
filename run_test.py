import subprocess
import time
import os
from playwright.sync_api import sync_playwright

def run_test():
    env = os.environ.copy()
    env["MOCK_VERTEXAI"] = "true"

    with open("backend_test.log", "wb") as backend_log, open("frontend_test.log", "wb") as frontend_log:
        backend_process = subprocess.Popen(
            ["uvicorn", "agent.main:app", "--host", "127.0.0.1", "--port", "8000"],
            env=env,
            stdout=backend_log,
            stderr=subprocess.STDOUT
        )
        frontend_process = subprocess.Popen(
            ["python", "app.py"],
            env=env,
            stdout=frontend_log,
            stderr=subprocess.STDOUT
        )

        # Give the servers a moment to start up
        print("Waiting for servers to start...")
        time.sleep(10) # Increased sleep time
        print("Done waiting.")

        try:
            print("Starting Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                print("Navigating to page...")
                page.goto("http://127.0.0.1:7860")
                print("Page loaded. Waiting for selector...")
                page.wait_for_selector("textarea")
                print("Selector found. Filling text area...")
                page.fill("textarea", "roll a 20 sided die")
                page.press("textarea", "Enter")
                print("Waiting for response...")
                page.wait_for_selector("text=You rolled a 10")
                print("Response found. Taking screenshot...")
                page.screenshot(path="verification.png")
                browser.close()
                print("Playwright test finished successfully.")
        except Exception as e:
            print(f"Test failed: {e}")
            print("--- Backend Log ---")
            with open("backend_test.log", "r") as f:
                print(f.read())
            print("--- Frontend Log ---")
            with open("frontend_test.log", "r") as f:
                print(f.read())
            raise # re-raise the exception
        finally:
            # Clean up the server processes
            print("Terminating server processes.")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()

if __name__ == "__main__":
    run_test()
