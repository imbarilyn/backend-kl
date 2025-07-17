from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import  auth, contracts, emailaddress
from app.database import create_tables

app = FastAPI()
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(emailaddress.router)

# @app.options("/{path:path}")
# async def preflight_handler(path: str, response: Response):
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
#     response.headers["Access-Control-Allow-Headers"] = "*"
#     return response
@app.middleware("http")
async def before_request(request, call_next):
    print('BEFORE REQUEST: ', request)
    if request.method == "OPTIONS":
        print('BEFORE REQUEST: ', request.method)
        return Response()
    return await call_next(request)

if __name__ == '__main__':
# Mount upload directory as  static files
    app.mount("/uploads", StaticFiles(directory='uploads'), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins= [
        "https://klafapp.vulavutech.org",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event('startup')
async def startup():
    await create_tables()