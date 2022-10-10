# from pydantic.tools import T
import uvicorn
async def app(scope, receive, send):
    ...

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, log_level="info")