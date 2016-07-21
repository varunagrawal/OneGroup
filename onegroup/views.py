from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect


def index(request):
    return HttpResponse("Welcome to OneGroup")


def certificate(request):
    return HttpResponse("bUqyJai87Sc7zrIY5RsIj8dstyNUfJCKYUQw8xtRGeA.yecklpybaeAY4xEK1RSeVjEgtJiPA1jdYOh4zGe8idU")
