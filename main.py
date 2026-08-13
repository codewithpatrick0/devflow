from fastapi import FastAPI

app = FastAPI(title='devflow')

@app.get('/health')
def check_health():
    return {
        'status': 'ok'
    }