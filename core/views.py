from django.shortcuts import render, redirect
from django.utils.translation import get_language

# Create your views here.

def about(request):
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
