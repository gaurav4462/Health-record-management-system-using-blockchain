from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from userlogin import app as userlogin_app
from doclogin import app as doclogin_app  
from ipfs import app as ipfs_app 
from docsignup import router as docsignup_router
from docdatasignup import app as docdatasignup_app
from doctitlefill import app as doctitlefill_app
from admin_login import app as admin_login_app
from createrelation import app as createrealtion_app
from createpatienthealthrecord import app as createpatienthealthrecord_app
from usertitlefill import app as usertitlefill_app
from access import app as access_app
from get_access import app as get_access_app
from remarks import app as remarks_app
from username import app as username_app
# from userpage import app as uesrpage_app

app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# Add CORS middleware to allow requests from React (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router from userlogin.py
app.include_router(userlogin_app.router)

# Include the router from doclogin.py
app.include_router(doclogin_app.router)  

# Include the router from ipfs.py
app.include_router(ipfs_app.router)  

# Include the router from docsignup.py
app.include_router(docsignup_router)  

app.include_router(docdatasignup_app.router)

app.include_router(doctitlefill_app.router)

app.include_router(admin_login_app.router)

app.include_router(createrealtion_app.router)

app.include_router(createpatienthealthrecord_app.router)

app.include_router(usertitlefill_app.router)

app.include_router(access_app.router)

app.include_router(get_access_app.router)

app.include_router(remarks_app.router)

app.include_router(username_app.router)




