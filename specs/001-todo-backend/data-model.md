# Data Model: Task Entity

## Task Entity

### Fields
- `id`: Integer (Primary Key, Auto-generated)
- `title`: String (Required, max length 255)
- `description`: String (Optional, max length 1000)
- `completed`: Boolean (Default: False)
- `created_at`: DateTime (Auto-generated on creation)
- `updated_at`: DateTime (Auto-generated on update)
- `user_id`: String/Integer (Required, identifies task owner)

### Relationships
- No direct relationships required for this initial implementation

### Validation Rules
- `title` must not be empty or null
- `title` maximum length of 255 characters
- `description` maximum length of 1000 characters
- `user_id` must be provided for all operations

### State Transitions
- `completed` field can transition from False to True via PATCH /complete endpoint
- `completed` field can transition from True to False via PUT/PATCH with updated data
- `updated_at` automatically updates when any field changes

## SQLModel Definition
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: int  # or str depending on how user IDs are represented

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    user_id: Optional[int] = None  # Should remain constant
```