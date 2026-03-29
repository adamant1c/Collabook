import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Determine the base URL for the tests based on the TEST_ENV environment variable.
    'dev' uses localhost:8501
    'prod' uses https://localhost (or the primary production URL accessible from where the script runs, e.g., https://collabook.click)
    """
    env = os.environ.get("TEST_ENV", "dev")
    if env == "prod":
        # In the context of the deploy script on the host, production is usually
        # served securely via Nginx on port 443. We can test against localhost
        # if Nginx exposes it, but since this is a live deployment script run on
        # the host, it's safer to test the public-facing URL or HTTPS localhost.
        # Nginx config binds to 80 and 443 statically, redirecting to https://collabook.click
        # For a truly robust test, testing the real domain is best.
        # If we just want to verify the local containers are up before DNS routes, we could test http://localhost
        # Let's default to HTTPS localhost, though the cert might complain if testing locally.
        # Alternatively, we can use https://collabook.click. We'll use the domain if the host knows it,
        # but for safety, testing the NGINX localhost endpoint with verify=False is common.
        # We'll use the domain here as it's the expected public face.
        return "https://collabook.click" 
    else:
        return "http://localhost:8501"

@pytest.fixture(scope="session")
def session():
    """Provides a requests session for testing."""
    s = requests.Session()
    # In case we test against a local nginx with a self-signed cert or mismatch
    s.verify = False 
    return s
