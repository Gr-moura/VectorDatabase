from typing import List, Optional
from enum import IntEnum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

api = FastAPI()


class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1


class TodoBase(BaseModel):
    # ... means required field
    todo_name: str = Field(
        ..., min_length=3, max_length=512, description="Name of the todo item"
    )
    todo_description: str = Field(..., description="Description of the todo item")
    priority: Priority = Field(
        default=Priority.LOW, description="Priority of the todo item"
    )


class TodoCreate(TodoBase):
    pass


# Like TodoBase but all fields are optional
class TodoUpdate(BaseModel):
    todo_name: Optional[str] = Field(
        None, min_length=3, max_length=512, description="Name of the todo item"
    )
    todo_description: Optional[str] = Field(
        None, description="Description of the todo item"
    )
    priority: Optional[Priority] = Field(None, description="Priority of the todo item")


# Since Todo inherits from TodoBase, it has all the same fields, plus todo_id
class Todo(TodoBase):
    todo_id: int = Field(..., description="ID of the todo item")


# Trocamos pelos nossos novos modelos, tipos mais fortes do que apenas dict
all_todos = [
    Todo(
        todo_id=1,
        todo_name="Sports",
        todo_description="Go to the gym",
        priority=Priority.MEDIUM,
    ),
    Todo(
        todo_id=2,
        todo_name="Study",
        todo_description="Learn FastAPI",
        priority=Priority.HIGH,
    ),
    Todo(
        todo_id=3,
        todo_name="Grocery",
        todo_description="Buy vegetables",
        priority=Priority.LOW,
    ),
    Todo(
        todo_id=4,
        todo_name="Cleaning",
        todo_description="Clean the house",
        priority=Priority.MEDIUM,
    ),
    Todo(
        todo_id=5,
        todo_name="Cooking",
        todo_description="Prepare dinner",
        priority=Priority.LOW,
    ),
]


# Como não é mais um dict, precisamos ajustar as funções para lidar com os novos modelos
# Responde model significa que a resposta será do tipo Todo
@api.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            return todo

    raise HTTPException(status_code=404, detail="Todo not found")


@api.get("/todos", response_model=List[Todo])
def get_todos(first_n: int = None):
    if first_n is None:
        return all_todos
    return all_todos[:first_n]


@api.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    new_todo_id = max(todo.todo_id for todo in all_todos) + 1

    new_todo = Todo(
        todo_id=new_todo_id,
        todo_name=todo.todo_name,
        todo_description=todo.todo_description,
        priority=todo.priority,
    )

    all_todos.append(new_todo)
    return new_todo


@api.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updated_todo: TodoUpdate):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            if updated_todo.todo_name is not None:
                todo.todo_name = updated_todo.todo_name
            if updated_todo.todo_description is not None:
                todo.todo_description = updated_todo.todo_description
            if updated_todo.priority is not None:
                todo.priority = updated_todo.priority
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@api.delete("/todos/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int):
    for index, todo in enumerate(all_todos):
        if todo.todo_id == todo_id:
            deleted_todo = all_todos.pop(index)
            return deleted_todo
    raise HTTPException(status_code=404, detail="Todo not found")
