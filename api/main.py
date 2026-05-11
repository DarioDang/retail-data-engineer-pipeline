from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import overview, price, seller

app = FastAPI(
    title = "Retail Price Intelligence API",
    description = "FastAPI backend for the retail product price intelligence dashboard",
    version = "1.0.0",
)

# CORS middleware
# This tells browsers: "it is safe for JavaScript running on these origins
# to call this API."
#
# During local development, allow_origins=["*"] is fine.
# Once you deploy the frontend to Netlify, replace "*" with your actual URL:
#   allow_origins=["https://your-dashboard.netlify.app"]
#
# Without this middleware, every fetch() call from your HTML frontend
# will be blocked by the browser with a CORS error.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.netlify.app",   
        "*" 
        ], 
    allow_credentials=True,                       
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers 
    # This tells browsers: "it is safe for JavaScript running on these origins
    # to call this API."
    #
    # During local development, allow_origins=["*"] is fine.
    # Once you deploy the frontend to Netlify, replace "*" with your actual URL:
    #   allow_origins=["https://your-dashboard.netlify.app"]
    #
    # Without this middleware, every fetch() call from your HTML frontend
    # will be blocked by the browser with a CORS error.

app.include_router(overview.router, prefix="/api/overview", tags=["Overview"])
app.include_router(price.router,    prefix="/api/price",    tags=["Price Analysis"])
app.include_router(seller.router,   prefix="/api/seller",   tags=["Seller Intelligence"])

# Healthcheck
# Render and Railway both ping this endpoint to confirm the service is alive.
# You can also use it to confirm the API is reachable from your browser.
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}
