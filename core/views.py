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
from django.http import StreamingHttpResponse
from celery.result import AsyncResult
from rest_framework.negotiation import BaseContentNegotiation
from django.core.cache import cache

import time

def index(request):
    return render(request, 'index.html', {})

class IgnoreClientContentNegotiation(BaseContentNegotiation):
    def select_parser(self, request, parsers):
        """
        Select the first parser in the `.parser_classes` list.
        """
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix):
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        return (renderers[0], renderers[0].media_type)

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

class TaskStatusView(APIView):
    content_negotiation_class = IgnoreClientContentNegotiation

    def get(self, request, task_id):
        def event_stream(task_id):
            while True:
                result = cache.get(f'task_{task_id}_result')
                if result:
                    yield f'data: {result}\n\n'
                    break
                time.sleep(1)

        response = StreamingHttpResponse(event_stream(task_id), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response