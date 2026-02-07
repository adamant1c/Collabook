from django.shortcuts import render, redirect
from django.utils.translation import get_language

# Create your views here.

def about(request):
    if 'token' not in request.session and not request.user.is_authenticated:
         # The 'token' check seems to be a legacy session token logic, but request.user is standard.
         # However, the code I saw only checked 'token'. I will leave it as serves `about` behavior.
         # But for `how_it_works`, it should probably be public.
         pass
    if 'token' not in request.session:
         return redirect('accounts:login')
    
    lang = get_language()
    template = 'about_it.html' if lang and lang.startswith('it') else 'about.html'
    return render(request, template)

def privacy_policy(request):
    lang = get_language()
    template = 'privacy_policy_it.html' if lang and lang.startswith('it') else 'privacy_policy.html'
    return render(request, template)

def terms(request):
    lang = get_language()
    template = 'terms_it.html' if lang and lang.startswith('it') else 'terms.html'
    return render(request, template)

def faq(request):
    lang = get_language()
    template = 'faq_it.html' if lang and lang.startswith('it') else 'faq.html'
    return render(request, template)

def how_it_works(request):
    lang = get_language()
    # Using one template with i18n tags is better practice, but following project style:
    template = 'how_it_works_it.html' if lang and lang.startswith('it') else 'how_it_works.html'
    # Actually, I'll restrict to one file for now to save tokens and time, and use translation tags if possible, 
    # but the project explicitely uses _it files. I'll create both to be safe and consistent.
    return render(request, template)
