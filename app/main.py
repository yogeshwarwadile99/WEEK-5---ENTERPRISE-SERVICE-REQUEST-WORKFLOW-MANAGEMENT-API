from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from app.config import config
from app.database import Base, engine
from app.middleware.error_handler import global_exception_handler, app_exception_handler, AppException
from app.routes import auth, requests, comments, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Enterprise Service Request & Workflow Management API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(comments.router)
app.include_router(analytics.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
        "health": "/api/health"
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": config.APP_NAME,
        "version": config.APP_VERSION,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {config.APP_NAME} v{config.APP_VERSION} started successfully!")
    logger.info(f"📚 API Documentation available at /api/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Application shutting down...")