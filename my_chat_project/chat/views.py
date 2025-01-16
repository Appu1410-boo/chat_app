from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import SignUpForm
from .models import Message
from django.db import models  # Import Q object for queries

# User signup view
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('chat:home')
    else:
        form = SignUpForm()
    return render(request, 'chat/signup.html', {'form': form})

# User login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/chat/')
                return redirect(next_url)
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'chat/login.html', {'form': form})

# User logout view
def logout_view(request):
    logout(request)
    return redirect('chat:login')

# Home view to display users and recent chats
@login_required
def home(request):
    users = User.objects.exclude(id=request.user.id)  # Exclude the logged-in user
    return render(request, 'chat/home.html', {'users': users})

# Chat window view
@login_required
def chat_window(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    users = User.objects.exclude(id=request.user.id)  # Get all users for the sidebar
    messages = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=receiver)) |
        (models.Q(sender=receiver) & models.Q(receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('chat:chat_window', user_id=user_id)

    return render(request, 'chat/chat_window.html', {
        'receiver': receiver,
        'messages': messages,
        'users': users
    })
