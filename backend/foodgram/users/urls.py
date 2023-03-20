from django.urls import include, path
from rest_framework import routers
from users.views import CustomUserViewSet
from djoser.views import TokenCreateView, TokenDestroyView


app_name = 'users'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')

auth_urls = [
    path(r'token/login/', TokenCreateView.as_view()),
    path(r'token/logout/', TokenDestroyView.as_view()),
]

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include(auth_urls)),
]
