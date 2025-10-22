
from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class AskRequest(BaseModel):
    query: str

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
        result = TASKS[task_name]()
        return {"response": result}
    else:
        return {"response": "Unknown task."}


@app.post("/ask")
async def ask(request: AskRequest):
    query = request.query.lower()
    if "roll a die" in query:
        try:
            sides = int(query.split("with")[1].strip().split(" ")[0])
            return {"response": roll_die(sides)}
        except:
            return {"response": "Please specify the number of sides for the die."}
    elif "is" in query and "prime" in query:
        try:
            num = int(query.split("is")[1].strip().split(" ")[0])
            return {"response": is_prime(num)}
        except:
            return {"response": "Please provide a number to check for primality."}
    elif "cut hair" in query:
        return {"response": "This action requires confirmation.", "confirmation_required": True}
    else:
        return {"response": "I can roll a die, check if a number is prime, or cut hair."}
