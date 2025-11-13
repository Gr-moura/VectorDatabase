from fastapi import FastAPI

api = FastAPI()

# Sample data
all_todos = [
    {"todo_id": 1, "todo_name": "Sports", "todo_description": "Go to the gym"},
    {"todo_id": 2, "todo_name": "Study", "todo_description": "Learn FastAPI"},
    {"todo_id": 3, "todo_name": "Grocery", "todo_description": "Buy vegetables"},
    {"todo_id": 4, "todo_name": "Cleaning", "todo_description": "Clean the house"},
    {"todo_id": 5, "todo_name": "Cooking", "todo_description": "Prepare dinner"},
]


# GET, POST (creating), PUT (changing), DELETE
@api.get("/")
def index():
    return {"message": "Hello World!"}


# localhost:8000/todos/1
# The information in {} is a path parameter and is used as the function argument
@api.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in all_todos:
        if todo["todo_id"] == todo_id:
            return {"result": todo}
    return {"error": "Todo not found"}


# Query parameters are optional parameters that are passed in the URL after a ?. The type is defined in the function argument
# Example: localhost:8000/todos?first_n=1
@api.get("/todos")
def get_todos(first_n: int = None):
    if first_n is None:
        return {"result": all_todos}
    return {"result": all_todos[:first_n]}


# If something is CPU bound, it has to do it, there is no need to use async
@api.get("/calculation")
def calculation():
    # do some heavy calculation
    pass
    return ""


# If it's a function that gets data from a database, sending requests for example, then you can use async
@api.get("/getdata")
async def get_data_from_db():
    # await
    pass
    return ""


@api.post("/todos")
def create_todo(todo: dict):
    new_todo_id = max(todo["todo_id"] for todo in all_todos) + 1
    new_todo = {
        "todo_id": new_todo_id,
        "todo_name": todo["todo_name"],
        "todo_description": todo["todo_description"],
    }

    all_todos.append(new_todo)
    return {"result": new_todo}


@api.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: dict):
    for todo in all_todos:
        if todo["todo_id"] == todo_id:
            todo["todo_name"] = updated_todo.get("todo_name", todo["todo_name"])
            todo["todo_description"] = updated_todo.get(
                "todo_description", todo["todo_description"]
            )
            return {"result": todo}
    return "Error, not found"


@api.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(all_todos):
        if todo["todo_id"] == todo_id:
            deleted_todo = all_todos.pop(index)
            return {"result": deleted_todo}
    return "Error, not found"
