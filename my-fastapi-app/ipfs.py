from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IPFS_API_URL = "http://localhost:5001/api/v0/add"

@app.post("/api/v0/add")
async def upload_file(file: UploadFile = File(...)):
    file_content = await file.read()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                IPFS_API_URL,
                files={"file": (file.filename, file_content)}
            )
            
            if response.status_code == 200:
                return JSONResponse(content=response.json())
            else:
                return JSONResponse(status_code=response.status_code, content={"error": response.text})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
