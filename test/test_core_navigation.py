import pytest
from bs4 import BeautifulSoup

def test_landing_page_loads(session, base_url):
    """Test that the main landing page loads successfully and contains expected elements."""
    response = session.get(f"{base_url}/")
    
    assert response.status_code == 200, f"Failed to load landing page at {base_url}/"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Check for basic structure
    assert soup.title is not None, "Landing page has no title"
    # Basic check for Collabook branding
    assert "Collabook" in soup.text

def test_about_page_loads(session, base_url):
    """Test that the About page loads successfully."""
    response = session.get(f"{base_url}/about/")
    assert response.status_code == 200, "Failed to load About page"
    assert "Collabook" in response.text

def test_rules_page_loads(session, base_url):
    """Test that the game rules page loads successfully."""
    response = session.get(f"{base_url}/game/rules/")
    assert response.status_code == 200, "Failed to load Rules page"
    assert "Rule" in response.text or "Regole" in response.text

def test_login_page_loads(session, base_url):
    """Test that the login page loads and contains a form."""
    response = session.get(f"{base_url}/login/")
    assert response.status_code == 200, f"Failed to load Login page at {base_url}/login/"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    forms = soup.find_all('form')
    assert len(forms) > 0, "No form found on the login page"

def test_register_page_loads(session, base_url):
    """Test that the registration page loads and contains a form."""
    response = session.get(f"{base_url}/register/")
    assert response.status_code == 200, f"Failed to load Register page at {base_url}/register/"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    forms = soup.find_all('form')
    assert len(forms) > 0, "No form found on the registration page"

def test_nonexistent_page_returns_404(session, base_url):
    """Test that a garbage URL returns a 404."""
    response = session.get(f"{base_url}/this-page-definitely-does-not-exist-12345/")
    assert response.status_code == 404, "Non-existent page did not return 404"
