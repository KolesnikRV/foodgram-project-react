from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipesViewSet, SubscriptionViewSet,
                    TagsViewSet)

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('users', SubscriptionViewSet, basename='users')

urlpatterns = [
     path('', include(router.urls))
]
