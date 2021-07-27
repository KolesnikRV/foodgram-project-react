from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientsViewSet, PurchaseViewSet,
                    RecipesViewSet, SubscriptionViewSet, TagsViewSet,)

router = DefaultRouter()
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('recipes/download_shopping_cart/',
         PurchaseViewSet.as_view({'get': 'list'})),
    path('recipes/<int:id>/shopping_cart/',
         PurchaseViewSet.as_view({'get': 'get', 'delete': 'delete'})),
    path('recipes/<int:id>/favorite/',
         FavoriteViewSet.as_view({'get': 'get', 'delete': 'delete'})),
    path('users/subscriptions/',
         SubscriptionViewSet.as_view({'get': 'list'})),
    path('users/<int:id>/subscribe/',
         SubscriptionViewSet.as_view({'get': 'get', 'delete': 'delete'})),
]

urlpatterns += router.urls
