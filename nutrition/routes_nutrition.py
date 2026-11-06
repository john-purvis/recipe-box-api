
# nutrition/routes_nutrition.py
import ast
import json
import random
import time
from urllib.parse import unquote_plus

from flask import Blueprint, jsonify

nutrition_bp = Blueprint("nutrition", __name__)

DELAY_SECONDS = random.randint(1, 3)

def load_dict_via_readline(file_path: str) -> dict:
    lines = []
    inside_dict = False
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            while True:
                # read exactly one line at a time
                line = file.readline()

                # file.readline() returns an empty string when it hits the End of File (EOF)
                if not line:
                    break

                # clean up padding whitespace
                stripped = line.strip()

                # skip empty lines or pure standalone comment lines
                # allows for standard python and javascript comments
                if not stripped or stripped.startswith(("#", "//")):
                    continue

                # if your file has 'INGREDIENTS = {', isolate everything after the '='
                if "=" in line and "{" in line and not inside_dict:
                    line = line.split("=", 1)[1]
                    inside_dict = True
                elif "{" in line:
                    inside_dict = True

                if inside_dict:
                    lines.append(line)

        # combine the collected lines back into a single string literal
        dict_string = "".join(lines).strip()

        # safely convert the string structure into a real Python dictionary
        return ast.literal_eval(dict_string)
    # handle common file and data issues
    except FileNotFoundError:
        print(f"Error: The file {file_path} could not be found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid dictionary format.")

def load_json_via_readline(file_path: str) -> dict:
    lines = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            while True:
                # read exactly one line at a time
                line = file.readline()

                # file.readline() returns an empty string when it hits the End of File (EOF)
                if not line:
                    break

                # clean up padding whitespace
                stripped = line.strip()

                # skip empty lines or pure standalone comment lines
                # allows for standard python and javascript comments
                if not stripped or stripped.startswith(("#", "//")):
                    continue

                lines.append(line)

        # combine the collected lines back into a single string literal
        json_string = "".join(lines).strip()

        # safely convert the string to json
        return json.loads(json_string)
    # handle common file and data issues
    except FileNotFoundError:
        print(f"Error: The file {file_path} could not be found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON format.")

NUTRITION_DATA = load_dict_via_readline("D:\\Projects\\recipe-box-api\\nutrition_data.json")

def lookup(ingredient):
    key = ingredient.strip().lower()
    if key in NUTRITION_DATA:
        return dict(NUTRITION_DATA[key])
    rng = random.Random(key)  # same fake numbers every time for the same name
    return {
        "calories": rng.randint(20, 400),
        "protein_g": round(rng.uniform(0, 20), 1),
        "carbs_g": round(rng.uniform(0, 60), 1),
        "fat_g": round(rng.uniform(0, 30), 1),
    }

@nutrition_bp.route("/<ingredient>", methods=["GET"])
def nutrition(ingredient):
    """
    Get an ingredient's nutrition data by its name.
    ---
    tags:
      - Nutrition Data
    security:
      - AuthKey: []  # <--- Tells Swagger to fetch the token from the lock box
    parameters:
      - name: ingredient
        in: path
        type: string
        required: true
    responses:
      200:
        description: Ingredient found
      401:
        description: Unauthorized (not logged in)
      403:
        description: Access denied (not logged in)
      404:
        description: Ingredient not found
    """
    ingredient = unquote_plus(ingredient)
    DELAY_SECONDS = random.randint(1, 2)
    time.sleep(DELAY_SECONDS)  # the wait every caller feels
    if ingredient == "manticore":
        # provide one edge case for testing error
        data = {}
        data["ingredient"] = ingredient.strip().lower()
        data["took_seconds"] = DELAY_SECONDS
        data["error"] = "ingredient not found"
        return jsonify(data), 404
    # lookup will provide dummy data if not found
    data = lookup(ingredient)
    data["ingredient"] = ingredient.strip().lower()
    data["per"] = "100 g"
    data["took_seconds"] = DELAY_SECONDS
    return jsonify(data), 200