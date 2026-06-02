from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.rate_limit import limiter
from app.routers import admin, auth, courses, enrollments


app = FastAPI(title="Course Enrollment Platform API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(admin.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
