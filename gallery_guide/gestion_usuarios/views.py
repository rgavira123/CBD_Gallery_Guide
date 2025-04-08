from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def sample_http(request):
    return HttpResponse("Hello App")
