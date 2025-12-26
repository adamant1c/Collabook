from django.views.generic import TemplateView

class RulesView(TemplateView):
    template_name = 'game/rules.html'
