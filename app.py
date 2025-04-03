from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_wtf.csrf import CSRFProtect
import json
from typing import List, Dict, Tuple
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("SPOONACULAR_API_KEY")

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
csrf = CSRFProtect(app)

# Spoonacular API configuration
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
SPOONACULAR_BASE_URL = 'https://api.spoonacular.com'

def load_recipes():
    try:
        with open('recipes.json', 'r') as file:
            return json.load(file)['recipes']
    except FileNotFoundError:
        return []

def load_favorites():
    try:
        with open('favorites.json', 'r') as file:
            return json.load(file)['favorites']
    except FileNotFoundError:
        return []

def save_favorites(favorites):
    with open('favorites.json', 'w') as file:
        json.dump({'favorites': favorites}, file, indent=4)

def find_matching_recipes(user_ingredients, vegetarian_only=False):
    recipes = load_recipes()
    matching_recipes = []
    
    for recipe in recipes:
        # Skip non-vegetarian recipes if filter is active
        if vegetarian_only and not recipe.get('vegetarian', False):
            continue
            
        recipe_ingredients = [ing.lower() for ing in recipe['ingredients']]
        
        # Find matching and missing ingredients
        matches = []
        missing = []
        for user_ing in user_ingredients:
            if any(user_ing in recipe_ing for recipe_ing in recipe_ingredients):
                matches.append(user_ing)
            else:
                missing.append(user_ing)
        
        # Calculate match percentage
        match_percentage = (len(matches) / len(user_ingredients)) * 100
        
        if match_percentage > 0:
            matching_recipes.append((recipe, match_percentage, missing))
    
    # Sort by match percentage
    matching_recipes.sort(key=lambda x: x[1], reverse=True)
    return matching_recipes

def get_recipe_emoji(recipe_name):
    name = recipe_name.lower()
    if 'pasta' in name or 'spaghetti' in name or 'noodle' in name:
        return '🍝'
    elif 'salad' in name:
        return '🥗'
    elif 'pizza' in name:
        return '🍕'
    elif 'burger' in name or 'sandwich' in name:
        return '🍔'
    elif 'soup' in name:
        return '🍲'
    elif 'taco' in name or 'burrito' in name:
        return '🌮'
    elif 'sushi' in name:
        return '🍣'
    elif 'curry' in name:
        return '🍛'
    elif 'cake' in name or 'dessert' in name:
        return '🍰'
    elif 'ice cream' in name:
        return '🍦'
    elif 'pancake' in name or 'waffle' in name:
        return '🥞'
    elif 'egg' in name:
        return '🍳'
    elif 'fish' in name or 'seafood' in name:
        return '🐟'
    elif 'chicken' in name:
        return '🍗'
    elif 'steak' in name or 'beef' in name:
        return '🥩'
    elif 'rice' in name:
        return '🍚'
    elif 'bread' in name:
        return '🍞'
    else:
        return '🍽️'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/results')
def results():
    data = request.args.get('data')
    if not data:
        return render_template('results.html', recipes=[])
    
    try:
        recipes_data = json.loads(data)
        return render_template('results.html', recipes=recipes_data)
    except json.JSONDecodeError:
        return render_template('results.html', recipes=[])

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/api/search', methods=['POST'])
def search():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    vegetarian_only = data.get('vegetarian', False)
    
    if not ingredients:
        return jsonify({'error': 'Please enter at least one ingredient!'}), 400
    
    user_ingredients = [ing.strip().lower() for ing in ingredients]
    matching_recipes = find_matching_recipes(user_ingredients, vegetarian_only)
    
    # Add emojis to recipes
    recipes_with_emojis = []
    for recipe, match_percentage, missing in matching_recipes:
        emoji = get_recipe_emoji(recipe['name'])
        recipes_with_emojis.append({
            'name': recipe['name'],
            'ingredients': recipe['ingredients'],
            'instructions': recipe['instructions'],
            'vegetarian': recipe.get('vegetarian', False),
            'emoji': emoji,
            'match_percentage': match_percentage,
            'missing_ingredients': missing
        })
    
    return jsonify(recipes_with_emojis)

@app.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    recipe_name = data.get('recipe_name')
    favorites = load_favorites()
    
    if recipe_name in favorites:
        favorites.remove(recipe_name)
    else:
        favorites.append(recipe_name)
    
    save_favorites(favorites)
    return jsonify({'status': 'success'})

@app.route('/api/recipes')
def get_recipes():
    if not SPOONACULAR_API_KEY:
        return jsonify({'error': 'Spoonacular API key not configured'}), 500
        
    # Get ingredients from query parameter
    ingredients = request.args.get('ingredients', '')
    print(f"Searching for ingredients: {ingredients}")
    
    if not ingredients:
        return jsonify({'error': 'No ingredients provided'}), 400
    
    try:
        # First, find recipes by ingredients
        search_endpoint = f"{SPOONACULAR_BASE_URL}/recipes/findByIngredients"
        search_params = {
            'apiKey': SPOONACULAR_API_KEY,
            'ingredients': ingredients,
            'number': 5,
            'ranking': 2,
            'ignorePantry': True
        }
        
        print(f"Making request to Spoonacular: {search_endpoint}")
        print(f"With params: {search_params}")
        
        # Make request to find recipes
        search_response = requests.get(search_endpoint, params=search_params)
        search_response.raise_for_status()
        
        # Get the initial recipes and print the raw response
        initial_recipes = search_response.json()
        print(f"Status Code: {search_response.status_code}")
        print(f"Response Headers: {dict(search_response.headers)}")
        print("Raw Spoonacular Response:", json.dumps(initial_recipes, indent=2))
        
        if not initial_recipes:
            return jsonify({'error': 'No recipes found'}), 404
            
        detailed_recipes = []
        
        for recipe in initial_recipes:
            try:
                recipe_id = recipe.get('id')
                if not recipe_id:
                    print(f"Skipping recipe without ID: {recipe}")
                    continue
                
                print(f"Processing recipe ID: {recipe_id}")
                
                # Get full recipe details
                info_response = requests.get(
                    f"{SPOONACULAR_BASE_URL}/recipes/{recipe_id}/information",
                    params={'apiKey': SPOONACULAR_API_KEY}
                )
                info_response.raise_for_status()
                recipe_info = info_response.json()
                
                # Extract used and missed ingredients directly from the search response
                used_ingredients = recipe.get('usedIngredients', [])
                missed_ingredients = recipe.get('missedIngredients', [])
                
                print(f"Recipe {recipe_id} ingredients:")
                print(f"- Used ingredients: {used_ingredients}")
                print(f"- Missed ingredients: {missed_ingredients}")
                
                # Calculate match percentage
                used_count = recipe.get('usedIngredientCount', 0)
                missed_count = recipe.get('missedIngredientCount', 0)
                total_count = used_count + missed_count
                match_percentage = (used_count / total_count * 100) if total_count > 0 else 0
                
                detailed_recipe = {
                    'id': recipe_id,
                    'name': recipe_info.get('title', ''),
                    'image': recipe_info.get('image', ''),
                    'ingredients': [
                        ing.get('original', '')
                        for ing in recipe_info.get('extendedIngredients', [])
                    ],
                    'instructions': [
                        step.get('step', '').strip()
                        for instruction in recipe_info.get('analyzedInstructions', [])
                        for step in instruction.get('steps', [])
                    ] or [step.strip() for step in recipe_info.get('instructions', '').split('\n') if step.strip()],
                    'vegetarian': recipe_info.get('vegetarian', False),
                    'match_percentage': match_percentage,
                    'missing_ingredients': [
                        ing.get('original', '')
                        for ing in missed_ingredients
                    ],
                    'preparationMinutes': recipe_info.get('preparationMinutes'),
                    'cookingMinutes': recipe_info.get('cookingMinutes'),
                    'servings': recipe_info.get('servings'),
                    'sourceUrl': recipe_info.get('sourceUrl', ''),
                    'summary': recipe_info.get('summary', '')
                }
                
                detailed_recipes.append(detailed_recipe)
                print(f"Successfully processed recipe {recipe_id}")
                
            except Exception as e:
                print(f"Error processing recipe {recipe_id}: {str(e)}")
                print(f"Recipe data: {json.dumps(recipe, indent=2)}")
                continue
        
        if not detailed_recipes:
            return jsonify({'error': 'No valid recipes found'}), 404
            
        return jsonify(detailed_recipes)
        
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching recipes: {str(e)}"
        print(error_message)
        print(f"Full error: {e.__class__.__name__}: {str(e)}")
        return jsonify({'error': error_message}), 500
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        print(f"Full error: {e.__class__.__name__}: {str(e)}")
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 