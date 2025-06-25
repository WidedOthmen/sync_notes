from fastapi import FastAPI , HTTPException , Depends
import schema
import os
import boto3
import json
from db import SessionLocal
from sqlalchemy.orm import Session
from models import Note as NoteModel


from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# // DB session 
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()



# // AWS S3 setup 
s3 = boto3.client('s3')
S3_BUCKET = os.getenv('S3_BUCKET')
print("Uploading to S3 Bucket:", S3_BUCKET)
if not S3_BUCKET:
    raise RuntimeError('S3_BUCKET is not set in the enviornment')




@app.post('/create_note/', response_model =schema.Note )
def create_note(note:schema.NoteCreate, db:Session=Depends(get_db)):
    note_obj = NoteModel(**note.dict())
    
    db.add(note_obj)
    db.commit()
    db.refresh(note_obj)
    
    s3.put_object(
        Bucket= S3_BUCKET,
        Key= f"Note/{note_obj.id}.json",
        Body= json.dumps(schema.Note.from_orm(note_obj).dict()),
        ContentType= "application/json"
    )
    
    return note_obj

@app.get('/list_notes/', response_model= list[schema.Note])
def list_notes(db: Session=Depends(get_db)):
    notes= db.query(NoteModel).all()
    return notes

@app.get('/get_note/{note_id}', response_model= schema.Note)
def get_note(note_id:int, db: Session= Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code = 404 , detail = "Note not found!")
    return note


@app.put('/update_note/{note_id}', response_model= schema.Note)
def update_note(note_id:int,updated_note:schema.NoteCreate, db: Session= Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code = 404 , detail = "Note not found!")
    
    # update fields
    for field , value in updated_note.dict().items():
        setattr(note,field,value)
        
    db.commit()
    db.refresh(note)
    
    s3.put_object(
        Bucket= S3_BUCKET,
        Key=f"Note/{note_id}.json",
        Body= json.dumps(schema.Note.from_orm(note).dict()),
        ContentType="application/json"   
    )
    
    return note

@app.delete('/delete_note/{note_id}')
def delete_note(note_id:int, db: Session= Depends(get_db)):
    note= db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code= 404,detail= "Note not found" )
    db.delete(note)
    db.commit()
    return {"detail": "Note deleted!"}