from django.contrib import admin
from django.urls import path
from billing import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('accounts/login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('add_products/', views.add_products, name='add_products'),
    path('remove_products/', views.remove_products, name='remove_products'),
    path('products/', views.products, name='products'),
    path('calculation/', views.calculation, name='calculation'),
    path('bill-preview/', views.bill_preview, name='bill_preview'),
    path('bills/', views.bill_history, name='bill_history'),
    path('bill/<int:bill_id>/', views.view_bill, name='view_bill'),
    path('bill/<int:bill_id>/download/', views.download_bill, name='download_bill'),
]
