# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory, session, g, url_for, redirect
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, gettext as _
from flask_migrate import Migrate
import json
import os
import uuid
from dotenv import load_dotenv
from translations import INGREDIENT_TRANSLATIONS, REVERSE_TRANSLATIONS

# Load environment variables from .env file
load_dotenv()

def get_recipe_emoji(recipe_title):
    """Get an appropriate emoji for a recipe based on its title."""
    title_lower = recipe_title.lower()
    
    # Define emoji mappings for different types of dishes
    emoji_map = {
        'pizza': '🍕',
        'pasta': '🍝',
        'salad': '🥗',
        'soup': '🥣',
        'cake': '🍰',
        'bread': '🍞',
        'fish': '🐟',
        'chicken': '🍗',
        'rice': '🍚',
        'sandwich': '🥪',
        'burger': '🍔',
        'steak': '🥩',
        'cookie': '🍪',
        'pie': '🥧',
        'egg': '🍳',
        'sushi': '🍱',
        'taco': '🌮',
        'burrito': '🌯'
    }
    
    # Check for matching keywords in the title
    for keyword, emoji_char in emoji_map.items():
        if keyword in title_lower:
            return emoji_char
            
    # Default emoji for recipes without specific matches
    return '🍽️'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 15}  # Add timeout to prevent database lock issues
}

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
babel = Babel(app)
migrate = Migrate(app, db)

# Add template globals
app.jinja_env.globals['get_recipe_emoji'] = get_recipe_emoji
app.jinja_env.globals['min'] = min  # Add Python's min function to Jinja environment

# Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = {
    'en': 'English',
    'it': 'Italiano'
}

def translate_ingredient(ingredient, target_lang='en'):
    """Translate an ingredient to or from English"""
    ingredient = ingredient.lower().strip()
    if target_lang == 'en':
        # Italian to English
        return REVERSE_TRANSLATIONS.get(ingredient, ingredient)
    else:
        # English to Italian
        return INGREDIENT_TRANSLATIONS.get(ingredient, ingredient)

@babel.localeselector
def get_locale():
    # Try to get the language from the URL parameter
    lang = request.args.get('lang')
    if lang and lang in app.config['LANGUAGES']:
        session['lang'] = lang
        return lang
    
    # Try to get the language from the session
    if 'lang' in session:
        return session['lang']
    
    # Try to get the language from the request header
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

@app.before_request
def before_request():
    g.locale = get_locale()
    g.lang_code = g.locale
    g.languages = app.config['LANGUAGES']
    
    # Set flask-babel locale for this request
    if hasattr(g, 'lang_code'):
        babel.locale_selector_func = lambda: g.lang_code

# Add Jinja2 extensions
app.jinja_env.add_extension('jinja2.ext.i18n')

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

# Models
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # English fields (required)
    title_en = db.Column(db.String(200), nullable=False)
    ingredients_en = db.Column(db.Text, nullable=False)
    instructions_en = db.Column(db.Text, nullable=False)
    # Italian fields (optional)
    title_it = db.Column(db.String(200), nullable=True)
    ingredients_it = db.Column(db.Text, nullable=True)
    instructions_it = db.Column(db.Text, nullable=True)
    # Common fields
    vegetarian = db.Column(db.Boolean, default=False)
    vegan = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), default='quick-meals')
    prep_time = db.Column(db.Integer, nullable=True)
    cook_time = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    source_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    favorites = db.relationship('Favorite', backref='recipe', lazy=True)

    def __repr__(self):
        return f'<Recipe {self.title_en}>'

    def get_image_url(self):
        """Get the image URL with robust fallback to default image"""
        # If there's no image URL at all, use default
        if not self.image_url:
            return url_for('static', filename='images/default.jpg')
        
        # If it's a placeholder URL from example.com, use default
        if 'example.com' in self.image_url:
            return url_for('static', filename='images/default.jpg')
        
        # Return the actual image URL directly - no URL manipulation
        return self.image_url

    def to_dict(self):
        return {
            'id': self.id,
            'title_en': self.title_en,
            'title_it': self.title_it,
            'ingredients_en': json.loads(self.ingredients_en),
            'ingredients_it': json.loads(self.ingredients_it) if self.ingredients_it else None,
            'instructions_en': json.loads(self.instructions_en),
            'instructions_it': json.loads(self.instructions_it) if self.instructions_it else None,
            'vegetarian': self.vegetarian,
            'vegan': self.vegan,
            'category': self.category or 'quick-meals',
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'image_url': self.image_url,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_title(self, lang='en'):
        """Get the title in the specified language"""
        return self.title_it if lang == 'it' and self.title_it else self.title_en

    def get_ingredients(self, lang='en'):
        """Get the ingredients in the specified language"""
        if lang == 'it' and self.ingredients_it:
            return json.loads(self.ingredients_it)
        return json.loads(self.ingredients_en)

    def get_instructions(self, lang='en'):
        """Get the instructions in the specified language"""
        if lang == 'it' and self.instructions_it:
            return json.loads(self.instructions_it)
        return json.loads(self.instructions_en)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return '<Favorite {} by {}>'.format(self.recipe_id, self.session_id)

    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'session_id', name='unique_favorite'),
    )

# Create database tables
def init_db():
    try:
        print("Checking database...")
        with app.app_context():
            # Only create tables if they don't exist
            db.create_all()
            print("Database tables verified.")
            
            # Check if we have any recipes
            recipe_count = Recipe.query.count()
            print(f"Found {recipe_count} recipes in the database.")
            
            if recipe_count == 0:
                print("No recipes found. Importing recipes from recipes.json...")
                # Run the import_recipes.py script as a separate process to avoid circular imports
                import subprocess
                import sys
                subprocess.run([sys.executable, 'import_recipes.py'])
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        import traceback
        print(traceback.format_exc())

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

@app.route('/api/recipes')
def get_recipes():
    # Get query parameters
    ingredients = request.args.get('ingredients', '').lower().split(',')
    ingredients = [i.strip() for i in ingredients if i.strip()]
    vegetarian = request.args.get('vegetarian', '').lower() == 'true'
    session_id = get_session_id()
    
    print(f"Searching for recipes with ingredients: {ingredients}")
    print(f"Current language: {g.lang_code}")
    
    if not ingredients:
        return jsonify({'error': 'No ingredients provided'}), 400
    
    try:
        # Translate ingredients to English if in Italian
        if g.lang_code == 'it':
            print("Translating search ingredients to English")
            ingredients = [translate_ingredient(ing, 'en') for ing in ingredients]
            print(f"Translated ingredients: {ingredients}")
        
        # Start with base query
        query = Recipe.query
        
        # Apply vegetarian filter if requested
        if vegetarian:
            query = query.filter_by(vegetarian=True)
        
        # Get all matching recipes
        recipes = query.all()
        matching_recipes = []
        
        # Get user's favorites
        favorites = {f.recipe_id for f in Favorite.query.filter_by(session_id=session_id).all()}
        
        for recipe in recipes:
            print(f"\nProcessing recipe: {recipe.get_title(g.lang_code)}")
            recipe_ingredients = recipe.get_ingredients(g.lang_code)
            recipe_instructions = recipe.get_instructions(g.lang_code)
            
            print(f"Search ingredients: {ingredients}")
            print(f"Recipe ingredients: {recipe_ingredients}")
            
            recipe_ingredients_lower = [ing.lower() for ing in recipe_ingredients]
            
            # Count matching ingredients with more flexible matching
            matching_count = sum(1 for ing in ingredients 
                               if any(ing in ri.lower() or ri.lower() in ing for ri in recipe_ingredients_lower))
            
            print(f"Matching count: {matching_count}")
            
            if matching_count > 0:
                # Calculate match percentage
                match_percentage = (matching_count / len(ingredients)) * 100
                
                # Find missing ingredients and translate them if needed
                missing_ingredients = [
                    ing for ing in ingredients 
                    if not any(ing in ri.lower() or ri.lower() in ing for ri in recipe_ingredients_lower)
                ]
                
                if g.lang_code == 'it':
                    missing_ingredients = [translate_ingredient(ing, 'it') for ing in missing_ingredients]
                
                recipe_dict = recipe.to_dict()
                recipe_dict['title'] = recipe.get_title(g.lang_code)
                recipe_dict['match_percentage'] = match_percentage
                recipe_dict['missing_ingredients'] = missing_ingredients
                recipe_dict['emoji'] = get_recipe_emoji(recipe.title_en)
                recipe_dict['is_favorite'] = recipe.id in favorites
                
                # Use the correct language version for ingredients and instructions
                if g.lang_code == 'it' and recipe.ingredients_it:
                    recipe_dict['ingredients'] = json.loads(recipe.ingredients_it)
                    recipe_dict['instructions'] = json.loads(recipe.instructions_it) if recipe.instructions_it else recipe_instructions
                else:
                    recipe_dict['ingredients'] = json.loads(recipe.ingredients_en)
                    recipe_dict['instructions'] = json.loads(recipe.instructions_en)
                
                matching_recipes.append(recipe_dict)
        
        # Sort by match percentage
        matching_recipes.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        if not matching_recipes:
            return jsonify({'error': 'No matching recipes found'}), 404
            
        return jsonify(matching_recipes)
        
    except Exception as e:
        print(f"Error in get_recipes: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Error searching recipes: {}'.format(str(e))}), 500

@app.route('/api/recipes/add', methods=['POST'])
def add_recipe():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    
    try:
        new_recipe = Recipe(
            title_en=data['title_en'],
            ingredients_en=json.dumps(data['ingredients_en']),
            instructions_en=json.dumps(data['instructions_en']),
            title_it=data.get('title_it'),
            ingredients_it=json.dumps(data['ingredients_it']) if 'ingredients_it' in data else None,
            instructions_it=json.dumps(data['instructions_it']) if 'instructions_it' in data else None,
            vegetarian=data.get('vegetarian', False),
            vegan=data.get('vegan', False),
            category=data.get('category', 'quick-meals'),
            image_url=data.get('image_url'),
            source_url=data.get('source_url')
        )
        
        db.session.add(new_recipe)
        db.session.commit()
        
        return jsonify({'message': 'Recipe added successfully', 'recipe': new_recipe.to_dict()}), 201
        
    except KeyError as e:
        return jsonify({'error': 'Missing required field: {}'.format(str(e))}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error adding recipe: {}'.format(str(e))}), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    session_id = get_session_id()
    try:
        favorites = Favorite.query.filter_by(session_id=session_id).all()
        favorite_recipes = [favorite.recipe.to_dict() for favorite in favorites]
        return jsonify(favorite_recipes)
    except Exception as e:
        return jsonify({'error': 'Error fetching favorites: {}'.format(str(e))}), 500

@app.route('/api/favorites/<int:recipe_id>', methods=['POST', 'DELETE'])
def manage_favorite(recipe_id):
    session_id = get_session_id()
    
    try:
        if request.method == 'POST':
            # Check if recipe exists
            recipe = Recipe.query.get_or_404(recipe_id)
            
            # Check if already favorited
            existing_favorite = Favorite.query.filter_by(
                recipe_id=recipe_id,
                session_id=session_id
            ).first()
            
            if existing_favorite:
                return jsonify({'message': 'Recipe already in favorites'}), 400
            
            # Add new favorite
            favorite = Favorite(recipe_id=recipe_id, session_id=session_id)
            db.session.add(favorite)
            db.session.commit()
            
            return jsonify({'message': 'Recipe added to favorites'}), 201
            
        elif request.method == 'DELETE':
            # Remove favorite
            favorite = Favorite.query.filter_by(
                recipe_id=recipe_id,
                session_id=session_id
            ).first_or_404()
            
            db.session.delete(favorite)
            db.session.commit()
            
            return jsonify({'message': 'Recipe removed from favorites'}), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error managing favorite: {}'.format(str(e))}), 500

# Recipe categories
RECIPE_CATEGORIES = {
    'italian-traditions': _('Italian Traditions'),
    'healthy': _('Healthy'),
    'quick-meals': _('Quick Meals'),
    'vegetarian': _('Vegetarian'),
    'vegan': _('Vegan'),
    'desserts': _('Desserts')
}

@app.route('/ricettario')
def ricettario():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show more recipes per page
    search_query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '')
    
    # Get current language
    lang = g.get('lang_code', 'en')
    
    # Base query
    query = Recipe.query
    
    # Apply search filter if provided
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Recipe.title_en.ilike(search),
                Recipe.title_it.ilike(search),
                Recipe.ingredients_en.ilike(search),
                Recipe.ingredients_it.ilike(search)
            )
        )
    
    # Apply category filter if provided
    if selected_category == 'vegetarian':
        query = query.filter_by(vegetarian=True)
    elif selected_category == 'vegan':
        query = query.filter_by(vegan=True)
    elif selected_category == 'italian-traditions':
        # Filter for Italian traditional recipes - look for recipes with category='italian-traditions' first,
        # then fallback to recipes that have Italian titles
        query = query.filter(
            db.or_(
                Recipe.category == 'italian-traditions',
                Recipe.title_it.isnot(None)
            )
        )
    elif selected_category:
        # Any other category
        query = query.filter_by(category=selected_category)
    
    # Add consistent sorting to ensure pagination works correctly
    if lang == 'it':
        # Sort by Italian title if available, fall back to English title
        query = query.order_by(
            db.case(
                (Recipe.title_it.isnot(None), Recipe.title_it),
                else_=Recipe.title_en
            ).asc()
        )
    else:
        query = query.order_by(Recipe.title_en.asc())
    
    # Get total count for stats
    total_recipes = query.count()
    
    # Get paginated results
    recipes = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # If page is out of range, redirect to last page
    if page > recipes.pages and recipes.pages > 0:
        return redirect(url_for('ricettario', page=recipes.pages, q=search_query, category=selected_category))
    
    # Group recipes by category for display
    categorized_recipes = {
        'italian-traditions': [],
        'healthy': [],
        'quick-meals': [],
        'vegetarian': [],
        'vegan': [],
        'desserts': []
    }
    
    # Get all recipes for categorization
    all_recipes = Recipe.query.all()
    
    for recipe in all_recipes:
        # Assign recipes to categories based on their attributes
        if recipe.category == 'italian-traditions' or recipe.title_it:
            categorized_recipes['italian-traditions'].append(recipe)
        elif recipe.category:
            if recipe.category in categorized_recipes:
                categorized_recipes[recipe.category].append(recipe)
        if recipe.vegetarian:
            categorized_recipes['vegetarian'].append(recipe)
        if recipe.vegan:
            categorized_recipes['vegan'].append(recipe)
    
    # Create translated category display names for the view
    translated_categories = {}
    for key, value in RECIPE_CATEGORIES.items():
        if key == 'italian-traditions':
            # This category name is already in Italian, use as is
            translated_categories[key] = value
        else:
            # Translate other categories according to the selected language
            translated_categories[key] = _(value)
    
    return render_template(
        'ricettario.html',
        recipes=recipes,
        categorized_recipes=categorized_recipes,
        categories=translated_categories,
        search_query=search_query,
        selected_category=selected_category,
        current_page=page,
        total_recipes=total_recipes
    )

@app.route('/ricetta/<int:id>')
def recipe_detail(id):
    # Get the recipe from database
    recipe = Recipe.query.get_or_404(id)
    
    # Get current language
    lang = g.get('lang_code', 'en')
    
    # Directly use the image_url from the database, not through get_image_url method
    image_url = recipe.image_url
    
    # Get recipe data in correct language
    recipe_data = {
        'id': recipe.id,
        'title': recipe.get_title(lang),
        'ingredients': recipe.get_ingredients(lang),
        'instructions': recipe.get_instructions(lang),
        'image_url': image_url,  # Use the raw URL directly
        'vegetarian': recipe.vegetarian,
        'vegan': recipe.vegan,
        'prep_time': recipe.prep_time,
        'cook_time': recipe.cook_time,
        'category': recipe.category,
        'emoji': get_recipe_emoji(recipe.title_en)
    }
    
    return render_template('ricetta.html', recipe=recipe_data)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host="0.0.0.0", port=port, debug=debug) 