# -*- coding: utf-8 -*-
from app import app, db, Recipe
import json
import os
import time

def import_recipes():
    # Counter for added/updated recipes
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    try:
        print("Importing recipes from recipes.json...")
        
        # Read the JSON file
        json_path = 'recipes.json'
        if not os.path.exists(json_path):
            print(f"Error: {json_path} file not found")
            return
            
        with open(json_path, 'r', encoding='utf-8') as file:
            recipes_data = json.load(file)
        
        # Ensure we have a list of recipes
        if isinstance(recipes_data, dict) and 'recipes' in recipes_data:
            recipes_data = recipes_data['recipes']
            
        total_recipes = len(recipes_data)
        print(f"Found {total_recipes} recipes in JSON file")
        
        # Process each recipe with a small delay to avoid database locks
        for i, recipe_data in enumerate(recipes_data):
            try:
                # Extract recipe data with defaults
                title = recipe_data.get('title', '').strip()
                title_it = recipe_data.get('title_it', '').strip()

                # Handle ingredients as either array or string
                if isinstance(recipe_data.get('ingredients', []), list):
                    ingredients = recipe_data.get('ingredients', [])
                else:
                    ingredients = recipe_data.get('ingredients', '').split(',')
                    ingredients = [i.strip() for i in ingredients if i.strip()]

                if isinstance(recipe_data.get('ingredients_it', []), list):
                    ingredients_it = recipe_data.get('ingredients_it', [])
                else:
                    ingredients_it = recipe_data.get('ingredients_it', '').split(',')
                    ingredients_it = [i.strip() for i in ingredients_it if i.strip()]

                # Handle instructions as either array or string
                if isinstance(recipe_data.get('instructions', ''), list):
                    instructions = recipe_data.get('instructions', [])
                else:
                    instructions = recipe_data.get('instructions', '').split('\n')
                    instructions = [i.strip() for i in instructions if i.strip()]

                if isinstance(recipe_data.get('instructions_it', ''), list):
                    instructions_it = recipe_data.get('instructions_it', [])
                else:
                    instructions_it = recipe_data.get('instructions_it', '').split('\n')
                    instructions_it = [i.strip() for i in instructions_it if i.strip()]

                vegetarian = recipe_data.get('vegetarian', False)
                vegan = recipe_data.get('vegan', False)
                category = recipe_data.get('category', 'quick-meals')
                
                # If a recipe is vegan, it's also vegetarian
                if vegan and not vegetarian:
                    vegetarian = True
                
                # Italian recipes should be in the italian-traditions category
                if title_it and not category:
                    category = 'italian-traditions'
                    
                image_url = recipe_data.get('image_url', None)
                source_url = recipe_data.get('source_url', None)
                
                # Special debug for carbonara recipe
                if title == 'Classic Spaghetti Carbonara':
                    print(f"CARBONARA IMAGE URL: {image_url}")
                
                # Skip if no title or required fields are missing
                if not title or not ingredients or not instructions:
                    print(f"Skipping invalid recipe: {title}")
                    skipped_count += 1
                    continue
                
                # Check if recipe already exists
                existing_recipe = Recipe.query.filter_by(title_en=title).first()
                if existing_recipe:
                    # Update existing recipe
                    existing_recipe.title_en = title
                    existing_recipe.ingredients_en = json.dumps(ingredients)
                    existing_recipe.instructions_en = json.dumps(instructions)
                    
                    # Update Italian fields if available
                    if title_it:
                        existing_recipe.title_it = title_it
                    if ingredients_it:
                        existing_recipe.ingredients_it = json.dumps(ingredients_it)
                    if instructions_it:
                        existing_recipe.instructions_it = json.dumps(instructions_it)
                    
                    existing_recipe.vegetarian = vegetarian
                    existing_recipe.vegan = vegan
                    existing_recipe.category = category
                    existing_recipe.image_url = image_url
                    existing_recipe.source_url = source_url
                    updated_count += 1
                    print(f"[{i+1}/{total_recipes}] Updated recipe: {title}")
                else:
                    # Create new recipe
                    new_recipe = Recipe(
                        title_en=title,
                        title_it=title_it if title_it else None,
                        ingredients_en=json.dumps(ingredients),
                        ingredients_it=json.dumps(ingredients_it) if ingredients_it else None,
                        instructions_en=json.dumps(instructions),
                        instructions_it=json.dumps(instructions_it) if instructions_it else None,
                        vegetarian=vegetarian,
                        vegan=vegan,
                        category=category,
                        image_url=image_url,
                        source_url=source_url
                    )
                    db.session.add(new_recipe)
                    added_count += 1
                    print(f"[{i+1}/{total_recipes}] Added recipe: {title}")
                
                # Commit every recipe to avoid large transactions
                db.session.commit()
                
                # Small delay to prevent database locks
                time.sleep(0.2)
                
            except Exception as e:
                db.session.rollback()
                print(f"Error processing recipe {i+1}: {str(e)}")
                skipped_count += 1
                time.sleep(0.5)  # Longer delay after an error
                continue
        
        print("\nImport completed:")
        print(f"Added {added_count} new recipes")
        print(f"Updated {updated_count} existing recipes")
        print(f"Skipped {skipped_count} recipes")
        
    except ValueError as e:
        print(f"Error: Invalid JSON format in recipes.json: {str(e)}")
    except Exception as e:
        print(f"Error importing recipes: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass

if __name__ == "__main__":
    with app.app_context():
        import_recipes() 