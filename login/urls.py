from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('contact/add/', views.add_contact, name='add_contact'),
    path('contact/edit/<int:contact_id>/', views.edit_contact, name='edit_contact'),
    path('contact/delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('post/add/', views.post_add, name='post_add'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('post/<int:id>/update/', views.post_update, name='post_update'),
    path('post/<int:id>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:id>/like/', views.post_like, name='post_like'),
    path('post/<int:id>/comment/', views.comment_add, name='comment_add'),
    path('comment/<int:id>/update/', views.comment_update, name='comment_update'),
    path('comment/<int:id>/delete/', views.comment_delete, name='comment_delete'),
]
