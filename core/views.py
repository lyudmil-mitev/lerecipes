from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe
from .tasks import generate_recipe
from .serializers import RecipeCreateSerializer, RecipeSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})

class RecipePagination(PageNumberPagination):
    page_size = 20

class CreateRecipeView(APIView):
    def get(self, request):
        queryset = Recipe.objects.exclude(status=Recipe.RecipeStatus.PENDING).order_by('-id')
        paginator = RecipePagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = RecipeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            serializer = RecipeSerializer(queryset, many=True)
            return Response(serializer.data)

    @method_decorator(ratelimit(key='ip', rate='15/m', block=True))
    @method_decorator(csrf_protect)
    def post(self, request):
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            theme = serializer.validated_data.get('theme', 'pasta')
            recipe = Recipe.objects.create(status='pending')
            task = generate_recipe.delay(recipe.id, theme)
            recipe.task_id = task.id
            recipe.save()

            return Response({"task_id": task.id, "recipe_id": recipe.id}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)