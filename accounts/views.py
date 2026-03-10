from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, CustomErrorList, ProfileForm
from .models import UserProfile
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from movies.models import Movie, Review

@staff_member_required  # Only admins can access this
def admin_stats(request):
    top_commenter = (
        Review.objects
        .values('user')   # Groups by username
        .annotate(comment_count=Count('id'))    # Count the comments per user
        .order_by('-comment_count')     # Sort the count by descending
        .first()    # Grab the top count of comments
    )
    return render(request, 'admin_stats.html', {
        'top_commenter': top_commenter
    })

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html', {'template_data': template_data})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

@login_required
def profile(request):
    template_data = {}
    template_data['title'] = 'My Profile'
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            template_data['success'] = 'Profile updated successfully.'
    else:
        form = ProfileForm(instance=user_profile)
    template_data['form'] = form
    return render(request, 'accounts/profile.html', {'template_data': template_data})

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request, 
            username = request.POST['username'], 
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            nationality = form.cleaned_data.get('nationality') or None
            # Single INSERT — no signal, no race condition.
            UserProfile.objects.create(user=user, nationality=nationality)
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request, 
            username = request.POST['username'], 
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')




@staff_member_required
def admin_dashboard(request):
    users_with_counts = User.objects.annotate(total_movies_purchased=Sum('order__item__quantity', default=0)).order_by('-total_movies_purchased')
    most_ordered_movie = Movie.objects.annotate(num_orders=Count('item')).order_by('-num_orders').first()
    most_reviewed_movie = Movie.objects.annotate(num_reviews=Count('review')).order_by('-num_reviews').first()

    top_user = users_with_counts.first()

    return render(request, 'accounts/admin_dashboard.html',
                  {'top_user': top_user, 'most_ordered_movie' : most_ordered_movie,
                   'most_reviewed_movie' : most_reviewed_movie})