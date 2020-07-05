from django.shortcuts import render, redirect # 추가
from django.contrib.auth.models import User # 추가
from django.contrib import auth # 추가

# Create your views here.
def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            user = User.objects.create_user(
                request.POST['username'], password=request.POST['password1'])
            auth.login(request, user)
            return redirect('blogMain')

    return render(request, 'signup.html')

def signout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('blogMain')
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('blogMain')
        else:
            return render(request, 'signin.html', {'error': '입력 정보가 잘못되었습니다.'})
    else:
        return render(request, 'signin.html')