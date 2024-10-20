from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image

from .app import inferance

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

infr = inferance()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read the uploaded file
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # Run inference
    result = infr.predict(image)

    return JSONResponse(content={"prediction": result})


@app.get("/")
async def root():
    return {"message": "Classification server is running"}


### prod 
## uvicorn Project_2.main:app --host 0.0.0.0 --port 4560 --workers 4

### dev
## uvicorn Project_2.main:app --host 0.0.0.0 --port 4560 --reload
