
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import random
import os
import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel as RealGenerativeModel, Part, Tool, FunctionDeclaration, Content
load_dotenv()

# --- Configure the generative model ---
# Initialize Vertex AI. It will use your default GCP project and credentials.
# You can explicitly set the project and location like this:
# vertexai.init(project="your-gcp-project-id", location="us-central1")
class MockGenerativeModel:
    def __init__(self, model_name, tools, system_instruction):
        pass

    def start_chat(self, history):
        class MockChat:
            def send_message(self, user_query):
                class MockResponse:
                    @property
                    def text(self):
                        return "You rolled a 10"
                return MockResponse()
        return MockChat()

if os.getenv("MOCK_VERTEXAI") == "true":
    GenerativeModel = MockGenerativeModel
    print("Using Mock Generative Model")
else:
    GenerativeModel = RealGenerativeModel
    vertexai.init()
    print("Using Real Generative Model")

app = FastAPI()

class AskRequest(BaseModel):
    history: List[Dict[str, Any]]


def roll_die(sides: int):
    """Rolls a die with a given number of sides."""
    return f"You rolled a {random.randint(1, sides)}"

def is_prime(n: int):
    """Checks if a number is prime."""
    if n <= 1:
        return f"{n} is not a prime number."
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return f"{n} is not a prime number."
    return f"{n} is a prime number."

def cut_hair():
    """Metaphorically cuts hair."""
    return "Your hair is now cut."

TASKS = {
    "cut_hair": cut_hair
}

class ExecuteTaskRequest(BaseModel):
    task: str

@app.post("/execute_task")
async def execute_task(request: ExecuteTaskRequest):
    task_name = request.task
    if task_name in TASKS:
        # For this demo, we assume 'cut_hair' is the only task requiring execution.
        # A more robust implementation would pass arguments if needed.
        response = TASKS[task_name]()
        return {"response": response}
    else:
        return {"response": "Unknown task."}


@app.post("/ask")
async def ask(request: AskRequest):
    history = request.history
    user_query = history[-1]['content']

    # Define the tools for the Vertex AI model by wrapping the Python functions
    tools = Tool.from_function_declarations([
        FunctionDeclaration.from_func(roll_die),
        FunctionDeclaration.from_func(is_prime),
        FunctionDeclaration.from_func(cut_hair),
    ])
    model_name = os.getenv("MODEL_NAME", "gemini-1.0-pro")
    system_instruction = (
        "You are a helpful assistant. You have access to the following tools. "
        "Use them if necessary to answer the user's question. "
        "When rolling a die and checking for primality, first roll the die, "
        "report the result to the user, and then check if that result is prime."
    )

    model = GenerativeModel(model_name=model_name, tools=[tools], system_instruction=system_instruction)

    # Convert the history of dictionaries to a list of Content objects,
    # ensuring only 'role' and 'content' (as a Part) are used.
    content_history = [Content(role=msg["role"], parts=[Part.from_text(msg["content"])])
                       for msg in history[:-1]]

    # Start a chat session with history
    chat = model.start_chat(history=content_history) # Exclude the latest user message for sending
    response = chat.send_message(user_query)
    
    # Loop to handle multiple function calls
    while True:
        try:
            part = response.candidates[0].content.parts[0]
            if not part.function_call:
                # Model has returned a final text response, break the loop
                break
            
            # Handle the function call
            function_call = part.function_call
            function_name = function_call.name
            function_args = {key: value for key, value in function_call.args.items()}

            if function_name == "cut_hair":
                return {"response": "This action requires confirmation.", "confirmation_required": True}
            elif function_name == "roll_die":
                api_response = roll_die(**function_args)
            elif function_name == "is_prime":
                api_response = is_prime(**function_args)
            else:
                api_response = f"Unknown function: {function_name}"

            # Send the function's result back to the model
            response = chat.send_message(
                Part.from_function_response(name=function_name, response={"result": api_response})
            )
        except (IndexError, ValueError, AttributeError):
            # Break the loop if the response has no function call or is malformed
            break

    return {"response": response.text}
