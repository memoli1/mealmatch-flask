from app import app, db, Recipe

with app.app_context():
    # Find the carbonara recipe
    recipe = Recipe.query.filter_by(title_en='Classic Spaghetti Carbonara').first()
    
    if recipe:
        print(f"Found Carbonara recipe with ID: {recipe.id}")
        print(f"Image URL in database: {recipe.image_url}")
        print(f"Image URL from method: {recipe.get_image_url()}")
    else:
        print("Carbonara recipe not found in database.") 