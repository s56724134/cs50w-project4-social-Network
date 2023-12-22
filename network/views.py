from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post, Follow, Like
import json
from django.http import JsonResponse
from django.db.models import Count

def post_like(request, pk):
    if request.method == "PUT":
        data = json.loads(request.body)
        like_count = int(data["like"])
        post = Post.objects.get(id=pk)
        checkLike = Like.objects.filter(user=request.user.id, post=post)
        if checkLike.exists():
            checkLike.delete()
            like_count -= 1
        else:
            newLike = Like(user=request.user, post=post)
            newLike.save()
            like_count += 1
        return JsonResponse({"data":like_count})
    
def edit(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(id=pk)
        edit_post.content = data["content"]
        edit_post.save()
        
        return JsonResponse({"message": "Change successful", "data":data["content"]})
        
        
        
def following_profile(request, pk):
    # 使用者是誰
    user = User.objects.get(id=pk)
    # 找出使用者追蹤的人
    followingPeople = Follow.objects.filter(user=user)
    # 將所有帖子的作者與使用者追蹤的人做比對
    posts = Post.objects.all().order_by('id').reverse()
    
    followingData = []
    for post in posts:
        for person in followingPeople:
            if post.author == person.user_follower:
                followingData.append(post)
                
    # 分頁
    paginator = Paginator(followingData, 10)
    page_number = request.GET.get('page')
    post_of_the_page = paginator.get_page(page_number)
    
        
    context = {"post_of_the_page":post_of_the_page}
               
    return render(request, "network/following.html", context)            
                
                                
def follow(request):
    # 被追蹤的人的資訊
    userFollow = request.POST["userfollow"]
    # 追蹤人的資訊
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userFollow)
    f = Follow(user=currentUser, user_follower=userfollowData)
    f.save()
    pk = userfollowData.id
    
    return HttpResponseRedirect(reverse(profile, kwargs={'pk':pk}))


def unfollow(request):
    # 被追蹤的人的資訊
    userFollow = request.POST["userfollow"]
    print("user follow:",userFollow )    
    
    # 追蹤人的資訊
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userFollow)
    print("User to unfollow:", userfollowData)
    f = Follow.objects.get(user=currentUser, user_follower=userfollowData)
    f.delete()
    pk = userfollowData.id
    
    return HttpResponseRedirect(reverse(profile, kwargs={'pk':pk}))
    
    
    
def profile(request,pk):
    
    user = User.objects.get(id=pk)
    allPosts = Post.objects.filter(author=user).order_by("date")
    
    # 追蹤人數logic
    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)#yu
    
    # 檢查此用戶是否追蹤其他用戶
    try:
        checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) != 0:
            isFollowing = True
        else:
            isFollowing = False
        
    except:
        isFollowing = False
        
    # 分頁
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    post_of_the_page = paginator.get_page(page_number)
    
        
    context = {"allPosts":allPosts, 
               "post_of_the_page":post_of_the_page,
               "following":following,
               "followers":followers,
               "userProfile":user,
               "isFollowing":isFollowing,
               }
    return render(request, "network/profile.html", context)
    
    
def new_post(request):
    if request.method == "POST":
        newpost = request.POST["content"]
        
        # 哪一位user
        currentUser = request.user
        
        # 存取新的newpost
        post = Post(content=newpost, author=currentUser)
        post.save()
        return HttpResponseRedirect(reverse("index"))
   
   
def index(request):
    allPosts = Post.objects.annotate(total_likes=Count('post_like')).order_by("-date")

    # 分頁
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    post_of_the_page = paginator.get_page(page_number)
    
                 
    context = {"allPosts":allPosts, 
               "post_of_the_page":post_of_the_page, 
               }
    return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
