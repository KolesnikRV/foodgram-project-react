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

RESPONSE_MESSAGES = {
    'Purchase': {
        'exists': 'Рецепт уже в списке покупок',
        'not': 'Рецепта нет в списке покупок.',
        'deleted': 'Рецепт удалён из списка покупок.',
    },
    'Favorite': {
        'exists': 'Рецепт уже в избранном.',
        'not': 'Рецепта нет в избранном.',
        'deleted': 'Рецепт удалён из избранного.',
    },
    'Subscription': {
        'myself': 'Нельзя подписаться на самого себя.',
        'exists': 'Вы уже подписаны на этого пользователя.',
        'not': 'Вы не подписаны на этого пользователя.',
        'deleted': 'Подписка отменена.',
    },
}


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

        return get_response(request, Recipe, Purchase,
                            RecipeMinifiedSerializer)

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, *args, **kwargs):

        return get_response(request, Recipe, Favorite,
                            RecipeMinifiedSerializer)


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

        if self.request.user.id == self.kwargs.get('pk'):
            return Response(RESPONSE_MESSAGES.get(''),
                            status=status.HTTP_400_BAD_REQUEST)

        return get_response(request, User, Subscription,
                            SubscriptionSerializer)


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ['^name']
    pagination_class = None


def get_response(request, model, create_delete_model, serializer):
    user = request.user
    pk = request.parser_context['kwargs'].get('pk')
    instance = get_object_or_404(model, pk=pk)
    model_kwags = {}
    model_kwags['user'] = user

    if model.__name__ == 'User':
        model_kwags['author'] = instance
    elif model.__name__ == 'Recipe':
        model_kwags['recipe'] = instance

    if request.method == 'GET':
        if create_delete_model.objects.filter(**model_kwags).exists():
            return Response(
                RESPONSE_MESSAGES.get(
                    create_delete_model.__name__).get('exists'),
                status=status.HTTP_400_BAD_REQUEST
            )

        create_delete_model.objects.create(**model_kwags)
        serializer = serializer(instance, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        create_delete_instance = get_object_or_404(create_delete_model,
                                                   **model_kwags)
        if not create_delete_instance:
            return Response(
                RESPONSE_MESSAGES.get(
                    create_delete_model.__name__).get('not'),
                status=status.HTTP_400_BAD_REQUEST
            )
        create_delete_instance.delete()
        return Response(
            RESPONSE_MESSAGES.get(create_delete_model.__name__).get('deleted'),
            status=status.HTTP_204_NO_CONTENT,
        )
