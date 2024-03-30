import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import (
    ImageField,
    IntegerField,
    SerializerMethodField,
    CharField,
)
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.status import HTTP_400_BAD_REQUEST

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


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name', 'color', 'slug']


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = CharField(required=True, max_length=150)
    last_name = CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=author).exists()


class SubscribeSerializer(CustomUserSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='You already follow this user!',
                code=HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='You can\'t follow yourself!',
                code=HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit',)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipesShortSerializer(recipes, many=True).data


class IngredientsRecipesAddSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    amount = IntegerField(required=True)
    name = SerializerMethodField(source='ingredient.name',)
    measurement_unit = SerializerMethodField(
        source='ingredient.measurement_unit',)

    class Meta:
        model = IngredientsRecipes
        fields = [
            'id',
            'amount',
            'name',
            'measurement_unit'
        ]


class IngredientsRecipesSerializer(ModelSerializer):
    amount = IntegerField(min_value=1)
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(
        source='ingredient.measurement_unit'
    )
    id = IntegerField(min_value=1, source='ingredient.id')

    class Meta:
        model = IngredientsRecipes
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsRecipesSerializer(
        many=True,
        source='ingredientsrecipes'
    )
    image = Base64ImageField(required=False)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    cooking_time = IntegerField(min_value=1)

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'image',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorites.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Carts.objects.filter(user=user, recipe=obj).exists()


class RecipeAddSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsRecipesAddSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'image',
            'cooking_time'
        ]

    def validate_tags(self, value):
        if not value:
            raise ValidationError({
                'tags': 'Recipe needs to have at least one tag!'
            })
        unique_tags = set(value)
        if len(value) != len(unique_tags):
            raise ValidationError({
                'tags': 'Tags must be unique!'
            })
        for tag in unique_tags:
            if not Tags.objects.filter(id=tag.id).exists():
                raise ValidationError(
                    'Can\'t add non-existing tag'
                )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError({
                'ingredients': 'Recipe needs to have at least one ingredient!'
            })
        for ingredient in value:
            if int(ingredient['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Ingredient amount has to be greater than 0!'
                })
        for ingredient in value:
            if not Ingredients.objects.filter(id=ingredient['id']).exists():
                raise ValidationError(
                    {'ingredients': 'Ingredient doesn\'t exist!'}
                )
        ingredients = {ingredient['id'] for ingredient in value}
        if len(value) != len(ingredients):
            raise ValidationError(
                {'ingredients': 'Can\'t add repetative ingredients'}
            )
        return value

    def create_ingredients_amount(self, recipe, ingredients):
        all_ingredients = [IngredientsRecipes(
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        IngredientsRecipes.objects.bulk_create(all_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amount(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        if not validated_data.get('tags'):
            raise ValidationError({
                'tags': 'Recipe needs to have at least one tag!'
            })
        if not validated_data.get('ingredients'):
            raise ValidationError({
                'ingredients': 'Recipe needs to have at least one ingredient!'
            })
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amount(
            recipe=instance,
            ingredients=ingredients
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return serializer


class RecipesShortSerializer(ModelSerializer):
    image = base64

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
