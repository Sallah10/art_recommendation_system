from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.login_user, name='login_user'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('status/<int:pk>', views.change_status, name='status'),
]



