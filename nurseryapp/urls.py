from django.urls import path, include
from . import views
from django.views.generic import TemplateView

app_name = 'nurseryapp'

urlpatterns = [
    path('', views.home, name='home'),    
    path('signup/', views.signup_index, name='signup'),    
    path('signup/<int:user>/', views.signup_form, name='signup_form'),    
    path('signup/post/<int:user>/', views.signup, name='post_signup'), 

    path('dashboard/', views.dashboard, name='dashboard'), 

    path('login/', views.user_login, name='login'),
    path('login_page/', TemplateView.as_view(template_name='user/login.html'), name='login_page'),
    path('logout/', views.user_logout, name='logout'),

    path('addplant_form/', views.addplant_form, name='addplant_form'),
    path('addplant/', views.addplant, name='addplant'),

    path('cart_action/<int:p_id>/<int:action>/', views.cart_action, name="cart_action"),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_order/', views.process_order, name='process_order'),
]
