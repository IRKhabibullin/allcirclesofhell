from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from game import views
from rest_framework.authtoken import views as auth_views

router = routers.DefaultRouter()
router.register(r'heroes', views.HeroViewSet)
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('api-token-auth/', auth_views.obtain_auth_token),
    url('game/', views.GameAction.as_view(), name='game_action')
]
