from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import get_language

# Create your views here.

@login_required
def about(request):
    return render(request, 'about.html')

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
