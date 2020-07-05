from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateBlog
from .models import Blog, Comment
from .forms import BlogCommentForm
import requests
import json
import matplotlib.pyplot as plt


# Create your views here.
def index(request):
    return render(request, 'index.html')

def blogMain(request):
    blogs = Blog.objects.all()

    return render(request, 'blogMain.html', {'blogs': blogs})

from django.shortcuts import render, redirect

def createBlog(request):
    if request.method == 'POST':
        form = CreateBlog(request.POST)

        if form.is_valid():
            form.save()
            return redirect('blogMain')
        else:
            return redirect('index')
    else:
        form = CreateBlog()
        return render(request, 'createBlog.html', {'form': form})


def detail(request, blog_id):
    blog_detail = get_object_or_404(Blog, pk=blog_id)
    comments = Comment.objects.filter(blog_id=blog_id)

    if request.method == 'POST':
        comment_form = BlogCommentForm(request.POST)

        if comment_form.is_valid():
            content = comment_form.cleaned_data['comment_textfield']

            print(content)

            login_request_uri = 'https://kauth.kakao.com/oauth/authorize?'

            client_id = '3b449f681f68923f0932493ed4487c64'
            redirect_uri = 'http://127.0.0.1:8000/oauth'

            login_request_uri += 'client_id=' + client_id
            login_request_uri += '&redirect_uri=' + redirect_uri
            login_request_uri += '&response_type=code&scope=talk_message'

            request.session['client_id'] = client_id
            request.session['redirect_uri'] = redirect_uri


            return redirect(login_request_uri)
        else:
            return redirect('blogMain')

    else:
        comment_form = BlogCommentForm()

        context = {
            'blog_detail': blog_detail,
            'comments': comments,
            'comment_form': comment_form
        }

        return render(request, 'detail.html', context)

def oauth(request):
        code = request.GET['code']
        print('code = ' + str(code))
        client_id = request.session.get('client_id')
        redirect_uri = request.session.get('redirect_uri')

        access_token_request_uri = "https://kauth.kakao.com/oauth/token?grant_type=authorization_code&"

        access_token_request_uri += "client_id=" + client_id
        access_token_request_uri += "&redirect_uri=" + redirect_uri
        access_token_request_uri += "&code=" + code

        print(access_token_request_uri)

        access_token_request_uri_data = requests.get(access_token_request_uri)
        json_data = access_token_request_uri_data.json()
        access_token = json_data['access_token']
        print(access_token)

        user_profile_info_uri = "https://kapi.kakao.com/v1/api/talk/profile?access_token="
        user_profile_info_uri += str(access_token)

        user_profile_info_uri_data = requests.get(user_profile_info_uri)
        user_json_data = user_profile_info_uri_data.json()
        nickName = user_json_data['nickName']
        profileImageURL = user_json_data['profileImageURL']
        thumbnailURL = user_json_data['thumbnailURL']

        print("nickName = " + str(nickName))
        print("profileImageURL = " + str(profileImageURL))
        print("thumbnailURL = " + str(thumbnailURL))

        template_dict_data = str({
            "object_type": "feed",
            "content": {
                "title": "Magichanee_Django",
                "description": "여행, 게임, 공부",
                "image_url": "https://i.imgur.com/ffpsUss.jpg",
                "image_width": 640,
                "image_height": 640,
                "link": {
                    "web_url": "http://www.daum.net",
                    "mobile_web_url": "http://m.daum.net",
                    "android_execution_params": "contentId=100",
                    "ios_execution_params": "contentId=100"
                }
            },
            "social": {
                "like_count": 2015,
                "comment_count": 250,
                "shared_count": 29,
                "view_count": 400,
                "subscriber_count": 500
            },
            "buttons": [
                {
                    "title": "바로 이동하려면?!",
                    "link": {
                        "web_url": "http://www.daum.net",
                        "mobile_web_url": "http://m.daum.net"
                    }
                },
                {
                    "title": "앱으로 이동",
                    "link": {
                        "android_execution_params": "contentId=100",
                        "ios_execution_params": "contentId=100"
                    }
                }
            ]
        })
        kakao_to_me_uri = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "Bearer " + access_token,
        }

        template_json_data = "template_object=" + str(json.dumps(template_dict_data))
        template_json_data = template_json_data.replace("\"", "")
        template_json_data = template_json_data.replace("'", "\"")

        response = requests.request(method="POST", url=kakao_to_me_uri, data=template_json_data, headers=headers)
        print(response.json())

        return redirect('blogMain')


def search(request):
    blogs = Blog.objects.all().order_by('-id')

    q = request.POST.get('q', "")

    if q:
        blogs = blogs.filter(title__icontains=q)
        return render(request, 'search.html', {'blogs': blogs, 'q': q})

    else:
        return render(request, 'search.html')
