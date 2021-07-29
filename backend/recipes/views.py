from django.http.response import HttpResponse
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .filters import CustomFilter
from .models import (Favorite, Ingredient, Purchase, Recipe, Subscription, Tag,
                     User)
from .permissions import CurrentUserOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeListSerializer,
                          RecipeMinifiedSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)


class TagsViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          CurrentUserOrAdminOrReadOnly)
    filter_class = CustomFilter

    def get_serializer_class(self):
        if self.request.method in ('GET',):
            return RecipeListSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        purchase_queryset = user.purchase_list.all()
        purchase_list = Purchase.get_purchase_list(purchase_queryset)
        result_purchase_list = []

        for ingredient, unit in purchase_list.items():
            result_purchase_list.append(
                f"{ingredient} ({unit['measurement_unit']}) — {unit['amount']}"
                + "\n"
            )

        filename = "Purchase_list.txt"
        response = HttpResponse(result_purchase_list,
                                content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if request.method == 'GET':
            if Purchase.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецепт уже в списке покупок',
                                status=status.HTTP_400_BAD_REQUEST)

            Purchase.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            user = self.request.user
            recipe_id = self.kwargs.get('pk')
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            purchase = get_object_or_404(Purchase, user=user, recipe=recipe)

            if not purchase:
                return Response(
                    'Рецепта нет в списке покупок.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            purchase.delete()
            return Response('Рецепт удалён из списка покупок.',
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if request.method == 'GET':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецепт уже в избранном.',
                                status=status.HTTP_400_BAD_REQUEST)

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            user = self.request.user
            recipe_id = self.kwargs.get('pk')
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)

            if not favorite:
                return Response(
                    'Рецепта нет в избранном.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response('Рецепт удалён из избранного.',
                            status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False)
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        subscription = User.objects.filter(following__user=user)

        page = self.paginate_queryset(subscription)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(subscription, many=True,
                                            context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET', 'DELETE'])
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user
        user_id = self.kwargs.get('pk')
        user_follow = get_object_or_404(User, pk=user_id)

        if request.method == 'GET':
            if user.id == user_id:
                return Response('Нельзя подписаться на самого себя.',
                                status=status.HTTP_400_BAD_REQUEST)

            if Subscription.objects.filter(user=user,
                                           author=user_follow).exists():
                return Response('Вы уже подписаны на этого пользователя.',
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=user_follow)
            serializer = SubscriptionSerializer(user_follow,
                                                context={'request': request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = get_object_or_404(Subscription, user=user,
                                             author=user_follow)
            if not subscription:
                return Response(
                    'Вы не подписаны на этого пользователя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response('Подписка отменена.',
                            status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ['^name']
    pagination_class = None
