from django.shortcuts import render

def show_main(request):
    context = {
        'npm' : '2406431334',
        'name': 'Jenisa Bunga',
        'class': 'PBP F'
    }

    return render(request, "main.html", context)

# Create your views here.
