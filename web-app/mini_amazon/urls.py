from django.urls import path
from . import views
app_name = 'mini_amazon'
urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/register/', views.user_reg),
    # path('homepage/', views.homepage),
    path('accounts/editAccount/user/', views.edit_user_info),
    path('accounts/editAccount/ups/', views.edit_user_ups),
    path('accounts/editAccount/address/<int:address_id>/', views.edit_user_address),
    path('accounts/editAccount/address/', views.add_user_address),
    path('accounts/editAccount/delete_address/<int:address_id>/', views.delete_user_address),
    
    path('accounts/get_user_info/', views.get_user_info),
    path('accounts/login/', views.login),
    path('accounts/logout/', views.logout),
    path('accounts/historical_orders/', views.get_packages),
    path('accounts/get_order_info/<int:package_id>/', views.get_package_info),
    path('accounts/delete_order/<int:package_id>/', views.delete_package),
    path('get_shopping_cart/', views.get_shopping_cart),
    path('checkout/<str:results>/', views.checkout),

    path('product_details/<int:pd_id>/', views.product_details),
    path('search', views.search_product, name="search_product"),
    # path('search/<int:id>/', views.search_product, name="search_product"),
    path('search/<catName>/', views.search_pd_by_cat, name="search_pd_by_cat"),
    path('rate_product/<int:package_id>/', views.rate),

    path('about-us/', views.aboutUS),
    path('shopping-guide/', views.guide),
    path('contact-us/', views.contact),
    path('message-received/', views.msg_recved),
    path('return-and-exchange/', views.exchange),
    path('FAQ/', views.faq),
    path('subscribed/', views.subscribe),
]