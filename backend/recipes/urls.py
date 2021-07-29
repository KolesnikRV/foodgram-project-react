from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet,
                    RecipesViewSet, SubscriptionViewSet, TagsViewSet,)

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('users', SubscriptionViewSet, basename='users')


urlpatterns = [
#     path('recipes/download_shopping_cart/',
#          PurchaseViewSet.as_view()),
#     path('recipes/<int:id>/shopping_cart/',
#          PurchaseViewSet.as_view({'get': 'get', 'delete': 'delete'})),
#     path('recipes/<int:id>/favorite/',
#          FavoriteViewSet.as_view({'get': 'get', 'delete': 'delete'})),
#     path('users/subscriptions/',
#          SubscriptionViewSet.as_view({'get': 'list'})),
#     path('users/<int:id>/subscribe/',
#          SubscriptionViewSet.as_view({'get': 'get', 'delete': 'delete'})),
     path('', include(router.urls))
]

# urlpatterns += router.urls
