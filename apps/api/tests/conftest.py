import os

# Set required env vars before any app module is imported.
# This ensures settings can be instantiated even without a local .env file.
os.environ.setdefault("DATABASE_URL", "postgresql://plot:plot@localhost:5432/plot_test")
os.environ.setdefault("AUTH0_DOMAIN", "placeholder.auth0.com")
os.environ.setdefault("AUTH0_AUDIENCE", "placeholder")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
