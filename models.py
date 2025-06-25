from sqlalchemy import Column, Integer, String
from db import Base

class Note(Base):
    __tablename__= "notes"
    
    id= Column(Integer , primary_key= True, index= True)
    title = Column(String , nullable=False)
    content= Column(String , nullable= False)
    author= Column(String , nullable=False)