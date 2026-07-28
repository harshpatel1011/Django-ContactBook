from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Contact, Post, Comment

from django.db.models import Q


def get_current_user(request):
    user_id = request.session.get("user_id")
    if user_id:
        return User.objects.filter(id=user_id).first()


def home(request):
    user = get_current_user(request)

    if not user:
        return redirect("login")

    contacts = user.contacts.all()
    posts = Post.objects.all().order_by("-created_at")

    q = request.GET.get("q")
    if q:
        contacts = contacts.filter(Q(name__icontains=q) | Q(phone_number__icontains=q))

    return render(
        request,
        "home.html",
        {
            "user": user,
            "contacts": contacts,
            "posts": posts,
        },
    )


def signup(request):
    if get_current_user(request):
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password != password_confirm:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("signup")

        new_user = User(username=username, email=email, password=password)
        new_user.save()

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "signup.html")


def login(request):
    if get_current_user(request):
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username).first()

        if user:
            if user.password == password:
                request.session["user_id"] = user.id

                messages.success(request, "Successfully logged in!")
                return redirect("home")
            else:
                messages.error(request, "Invalid password!")
        else:
            messages.error(request, "Invalid username!")
            return redirect("login")

    return render(request, "login.html")


def logout(request):
    request.session.flush()
    messages.success(request, "Successfully logged out!")
    return redirect("login")


def delete_account(request):
    user = get_current_user(request)
    
    if not user:
        messages.error(request, "You must be logged in to delete your account.")
        return redirect("login")
        
    if request.method == "POST":
        password = request.POST.get("password")
        if user.password != password:
            messages.error(request, "Incorrect password. Account deletion failed.")
            return redirect("delete_account")
            
        Post.objects.filter(author=user.username).delete()
        Comment.objects.filter(name=user.username).delete()
        Contact.objects.filter(user=user).delete()
            
        user.delete()
        request.session.flush()
        messages.success(request, "Your account and all associated data have been deleted successfully.")
        return redirect("login")

    return render(request, "delete_account.html", {"user": user})


def change_password(request):
    user = get_current_user(request)

    if not user:
        messages.error(request, "You must be logged in to change your password.")
        return redirect("login")

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if user.password != current_password:
            messages.error(request, "Current password is incorrect!")
            return redirect("change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match!")
            return redirect("change_password")

        if current_password == new_password:
            messages.error(
                request, "New password cannot be the same as the old password!"
            )
            return redirect("change_password")

        user.password = new_password
        user.save()

        request.session.flush()
        messages.success(request, "Password changed successfully! Please log in again.")
        return redirect("login")

    return render(request, "change_password.html", {"user": user})


def update_profile(request):
    user = get_current_user(request)

    if not user:
        messages.error(request, "You must be logged in to update your profile.")
        return redirect("login")

    if request.method == "POST":
        new_username = request.POST.get("username")
        new_email = request.POST.get("email")
        password = request.POST.get("password")

        if user.password != password:
            messages.error(request, "Incorrect password. Profile update failed.")
            return redirect("update_profile")

        if (
            new_username != user.username
            and User.objects.filter(username=new_username).exists()
        ):
            messages.error(request, "Username already taken!")
            return redirect("update_profile")

        if new_email != user.email and User.objects.filter(email=new_email).exists():
            messages.error(request, "Email already registered!")
            return redirect("update_profile")

        user.username = new_username
        user.email = new_email
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("home")

    return render(request, "update_profile.html", {"user": user})


def add_contact(request):
    user = get_current_user(request)
    if not user:
        messages.error(request, "You must be logged in to add a contact.")
        return redirect("login")

    if request.method == "POST":
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")

        Contact.objects.create(user=user, name=name, phone_number=phone_number)
        messages.success(request, "Contact added successfully!")
        return redirect("home")

    return render(request, "add_contact.html")


def edit_contact(request, contact_id):
    user = get_current_user(request)
    if not user:
        messages.error(request, "You must be logged in to edit a contact.")
        return redirect("login")

    contact = Contact.objects.filter(id=contact_id, user=user).first()
    if not contact:
        messages.error(request, "Contact not found or access denied.")
        return redirect("home")

    if request.method == "POST":
        contact.name = request.POST.get("name")
        contact.phone_number = request.POST.get("phone_number")
        contact.save()
        messages.success(request, "Contact updated successfully!")
        return redirect("home")

    return render(request, "edit_contact.html", {"contact": contact})


def delete_contact(request, contact_id):
    user = get_current_user(request)
    if not user:
        messages.error(request, "You must be logged in to delete a contact.")
        return redirect("login")

    contact = Contact.objects.filter(id=contact_id, user=user).first()
    if contact:
        contact.delete()
        messages.success(request, "Contact deleted successfully!")
    else:
        messages.error(request, "Contact not found or access denied.")

    return redirect("home")


def post_add(req):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    if req.method == "POST":
        Post.objects.create(
            title=req.POST["title"],
            content=req.POST["content"],
            author=user.username,
        )
        return redirect("home")
    return render(req, "post_add.html")


def post_detail(req, id):
    user = get_current_user(req)
    post = Post.objects.get(id=id)
    comments = post.comments.all().order_by("-created_at")
    return render(req, "post_detail.html", {"post": post, "comments": comments, "user": user})


def post_update(req, id):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    post = Post.objects.get(id=id)
    if post.author != user.username:
        messages.error(req, "You can only edit your own posts.")
        return redirect("home")

    if req.method == "POST":
        post.title = req.POST["title"]
        post.content = req.POST["content"]
        post.save()
        return redirect("home")
    return render(req, "post_update.html", {"post": post})


def post_delete(req, id):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    post = Post.objects.get(id=id)
    if post.author == user.username:
        post.delete()
        messages.success(req, "Post deleted successfully.")
    else:
        messages.error(req, "You can only delete your own posts.")
    return redirect("home")


def post_like(req, id):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    post = Post.objects.get(id=id)
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return redirect("post_detail", id=id)


def comment_add(req, id):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    post = Post.objects.get(id=id)
    if req.method == "POST":
        Comment.objects.create(
            post=post,
            name=user.username,
            text=req.POST["text"],
        )
    return redirect("post_detail", id=id)


def comment_update(req, id):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    comment = Comment.objects.get(id=id)
    post = comment.post

    if user.username != comment.name and user.username != post.author:
        messages.error(req, "You cannot edit this comment.")
        return redirect("post_detail", id=post.id)

    if req.method == "POST":
        comment.text = req.POST["text"]
        comment.save()
        messages.success(req, "Comment updated.")
        return redirect("post_detail", id=post.id)
        
    return render(req, "comment_update.html", {"comment": comment, "post": post})


def comment_delete(req, id):
    user = get_current_user(req)
    if not user:
        return redirect("login")

    comment = Comment.objects.get(id=id)
    post = comment.post

    if user.username == comment.name or user.username == post.author:
        comment.delete()
        messages.success(req, "Comment deleted.")
    else:
        messages.error(req, "You cannot delete this comment.")
    
    return redirect("post_detail", id=post.id)

