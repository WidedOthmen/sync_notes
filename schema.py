from pydantic import BaseModel

# For incoming requests (POST, PUT)
class NoteCreate(BaseModel):
    title: str
    content:str
    author:str
    
    # For responses (includes DB ID)
class Note(NoteCreate):
    id: int  
    
    class Config:
        from_attributes = True 