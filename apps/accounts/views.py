from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('animal_list')
        messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'accounts/login.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_list(request):
    # Apenas staff/superuser podem ver a lista de usuários
    if not (request.user.is_staff or request.user.is_superuser):
        # 403 Forbidden para usuários autenticados sem permissão
        raise PermissionDenied
    User = get_user_model()
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})

def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(request, f'Conta criada para {user.username}!')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})