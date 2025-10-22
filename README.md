# Human-in-the-Loop Agent Demo

This project demonstrates a human-in-the-loop confirmation flow for an AI agent. It uses a Gradio frontend and a Python backend with Google's Generative AI.

## Setup

1. Install the dependencies:

2. Create a `.env` file in the root of the project and add the model you want to use:
   ```
   MODEL_NAME=gemini-1.0-pro
   ```

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the agent backend:

   ```bash
   uvicorn agent.main:app --reload
   ```

3. Run the Gradio frontend:

   ```bash
   python app.py
   ```

## How it works

The agent has three functions:

- `roll_die`: Rolls a die with a given number of sides.
- `is_prime`: Checks if a number is prime.
- `cut_hair`: A function that requires human confirmation before executing.

When a user asks to "cut hair", the agent doesn't execute the function immediately. Instead, it sends a message to the Gradio frontend, which then displays "Approve" and "Deny" buttons. The `cut_hair` function is only executed if the user clicks "Approve".
