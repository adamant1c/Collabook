import os
import django
from django.test import Client
from django.conf import settings
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collabook_frontend.settings")
django.setup()
# Ensure ALLOWED_HOSTS includes testserver
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

def verify_about_page():
    client = Client()
    url = reverse('about')

    print("--- 1. Testing Logged-in Access (English Default) ---")
    session = client.session
    session['token'] = 'fake_token'
    session.save()
    
    # Force EN
    client.cookies.load({'django_language': 'en'})
    response = client.get(url, HTTP_ACCEPT_LANGUAGE='en')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if "Senior Consultant" in content and "Consulenza senior" not in content:
            print("[PASS] English content served (found 'Senior Consultant')")
        elif "Consulenza senior" in content:
            print("[FAIL] Italian content served instead of English")
        else:
            print("[WARN] Could not verify specific English content string")
    else:
        print(f"[FAIL] Request failed with status {response.status_code}")

    print("\n--- 2. Testing Logged-in Access (Italian) ---")
    # Force IT
    client.cookies.load({'django_language': 'it'})
    response = client.get(url, HTTP_ACCEPT_LANGUAGE='it')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if "Consulenza senior" in content:
            print("[PASS] Italian content served (found 'Consulenza senior')")
        elif "Senior Consultant" in content:
             print("[FAIL] English content served instead of Italian")
        else:
             print("[WARN] Could not verify specific Italian content string")
    else:
        print(f"[FAIL] Request failed with status {response.status_code}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_about_page()
