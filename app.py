from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_wtf.csrf import CSRFProtect
import json
from typing import List, Dict, Tuple
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
csrf = CSRFProtect(app)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001) 