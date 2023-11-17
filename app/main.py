from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routers
from .db.sqldb import engine
from .db.sqldb.admin import admin_views
from .db.sqldb.auth import authentication_backend
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import os
from sqladmin import Admin

configure_azure_monitor(
    connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING'),
)

app = FastAPI(title="Gambrinus",
              description="AI that understands the flavor of beer.",
              version="0.5.0",
              docs_url="/docs")

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

# --- ROUTERS ---

for key in routers:
    app.include_router(routers[key])

# --- SQL ADMIN ---
admin = Admin(app, engine, authentication_backend=authentication_backend)
for key in admin_views:
    admin.add_view(admin_views[key])

# Telemetry Instrumentation
FastAPIInstrumentor.instrument_app(app)
