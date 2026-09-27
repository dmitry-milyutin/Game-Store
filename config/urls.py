from django.contrib import admin
from django.urls import path
from game import views
from django.conf.urls.static import static
from django.conf import settings
import django.contrib.auth.views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page),
    path('categories', views.categories_page),
    path('login', auth_views.LoginView.as_view(template_name="login.html")),
    path('gamesearch', views.gamesearch_page),
    path('registration', views.registration_page),
    path('game/<str:key>', views.game_page),
    path('logout', auth_views.LogoutView.as_view()),
    path('cart', views.cart_page),
    path('cart/<str:key>', views.toggle_cart),
    path('payment', views.payment),
    path('success', views.success),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)