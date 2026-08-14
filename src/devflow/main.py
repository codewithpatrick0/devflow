from fastapi import FastAPI

from devflow.app.routers import auth_router

app = FastAPI(title='devflow')

app.include_router(auth_router)

@app.get('/health')
def check_health():
    return {
        'status': 'ok'
    }