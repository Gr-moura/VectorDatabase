from pydantic import BaseModel, Field


class ChunkBase(BaseModel):
    content: str = Field(..., description="Content of the chunk")
