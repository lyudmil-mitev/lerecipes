import os
from openai import OpenAI
from celery import shared_task
from .models import Recipe
from dotenv import load_dotenv
import json

load_dotenv()
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

@shared_task
def generate_recipe(recipe_id: int, theme: str = "pasta"):
    recipe = Recipe.objects.get(id=recipe_id)
    recipe.status = 'in_progress'
    recipe.save()

    system = "You are a celebrity chef with a no-nonsense attitude. Think carefully, so everything is clear and you don't make any mistakes for your readers."
    prompt = f"""
    Write a recipe for a {theme} dish.
    Please return the result in the following JSON format:

    ```
    {{
      "title": "<string>",
      "ingredients": [
        "<ingredient 1>",
        "<ingredient 2>",
        ...
      ],
      "steps": [
        "<step 1>",
        "<step 2>",
        ...
      ]
    }}
    ```

    Make sure to follow strictly this JSON format and do not include any explanations outside the JSON.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )

    generated_text = response.choices[0].message.content.strip()

    try:
        json_str = generated_text.strip("`").strip("json").strip()
        data = json.loads(json_str)
    except json.JSONDecodeError:
        data = {
            "title": "Untitled",
            "ingredients": [],
            "steps": []
        }

    title = data.get("title", "Untitled Recipe")
    ingredients_list = data.get("ingredients", [])
    steps_list = data.get("steps", [])

    ingredients_text = "\n".join(ingredients_list)
    steps_text = "\n".join(steps_list)

    recipe.title = title
    recipe.ingredients = ingredients_text
    recipe.steps = steps_text
    recipe.status = 'completed'
    recipe.save()

    return recipe.id
