# Business Logic Service for the League Management

from fastapi import FastAPI

tags_metadata = [ # for the Swagger documentation
    
]

app = FastAPI(title="League Business Service", openapi_tags=tags_metadata) 

@app.get("/")
def read_root():  
    return {"message": "League Business Service is running"}