from django.shortcuts import render
from django.views import View


class Home(View):
    template_name = 'common/home.html'

    @staticmethod
    def get_context_data():
        context: dict = {
            'title': 'Домашняя страница',
        }

        return context

    def get(self, request):
        return render(request, self.template_name, context=Home.get_context_data())

