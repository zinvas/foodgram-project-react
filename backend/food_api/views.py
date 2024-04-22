from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND
)
import tempfile

from food_api.pagination import CustomPagination
from food_api.permissions import IsAuthorOrReadOnly
from food_api.serializers import (
    IngredientSerializer,
    TagSerializer,
    UserSerializer,
    SubscribeSerializer,
    RecipeSerializer,
    RecipeAddSerializer,
    RecipesShortSerializer
)
from food_api.filters import (
    IngredientFilter,
    RecipeFilter
)
from recipes.models import (
    Recipes,
    Tags,
    Ingredients,
    IngredientsRecipes,
    Favorites,
    Carts
)
from users.models import Subscribe

User = get_user_model()


class ShoppingCartMixin():
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsRecipes.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount_of_ingredient=Sum('amount'))
        today = timezone.now()
        filename = f'{today:%Y-%m-%d}_shopping_list.txt'
        shopping_list = 'Your personal shopping list:'
        temporary = tempfile.NamedTemporaryFile()
        with open(temporary.name, 'w') as file:
            file.write(shopping_list)
            for ingredient in ingredients:
                file.write(
                    f'\n{ingredient["ingredient__name"]} - '
                    f'{ingredient["amount_of_ingredient"]} '
                    f'{ingredient["ingredient__measurement_unit"]}'
                )
        file = open(temporary.name, 'rb')
        response = FileResponse(
            file,
            filename=filename,
            as_attachment=True,
            content_type='text/plain'
        )
        return response


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        serializer = SubscribeSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=user, author=author)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if not Subscribe.objects.filter(user=user, author=author).exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        subscription = get_object_or_404(
            Subscribe,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipesViewSet(ShoppingCartMixin, viewsets.ModelViewSet):
    queryset = Recipes.objects.prefetch_related('author', 'ingredients')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeAddSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, model, user, id):
        if not Recipes.objects.filter(id=id).exists():
            return Response(
                {'error': 'Recipe doesn\'t exist!'},
                status=HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(user=user, recipe__id=id).exists():
            return Response(
                {'error': 'Recipe already added!'},
                status=HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipes, id=id)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipesShortSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_recipe(self, model, user, id):
        if not Recipes.objects.filter(id=id).exists():
            return Response(
                {'error': 'Recipe doesn\'t exist!'},
                status=HTTP_404_NOT_FOUND
            )
        obj = model.objects.filter(user=user, recipe__id=id)
        if obj.exists():
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Recipe isn\'t added, can\'t be deleted'},
            status=HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.add_recipe(Favorites, request.user, pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk):
        return self.delete_recipe(Favorites, request.user, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_recipe(Carts, request.user, pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk):
        return self.delete_recipe(Carts, request.user, pk)
