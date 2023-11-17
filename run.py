import uvicorn
from app.main import app
from app.db.sqldb.schema import reset_schema

if __name__ == "__main__":
#    reset_schema()
    uvicorn.run(app, host="0.0.0.0", port=8000)
