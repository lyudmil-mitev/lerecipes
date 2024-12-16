from rest_framework import serializers
from .models import Recipe

class RecipeCreateSerializer(serializers.Serializer):
    theme = serializers.CharField(required=False, default="Pasta", max_length=50, min_length=3)

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'