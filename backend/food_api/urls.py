from django.urls import include, path
from rest_framework.routers import DefaultRouter

from food_api.views import (
    IngredientsViewSet,
    TagsViewSet,
    RecipesViewSet,
    UserViewSet
)

app_name = 'food_api'

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet, basename='Recipes')
router.register('users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
