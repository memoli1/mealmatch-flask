#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to reset the database, import recipes, and start the app.
"""
import os
import time
import subprocess
import sys
from app import app, db, Recipe

def reset_database():
    print("Resetting database...")
    try:
        # Delete old database files
        for db_file in ['recipes.db', 'instance/recipes.db', 'app.db', 'instance/app.db']:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"Removed database file: {db_file}")
        
        # Remove migrations folder
        if os.path.exists('migrations'):
            import shutil
            shutil.rmtree('migrations')
            print("Removed migrations folder.")
        
        # Create new database
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False
    return True

def import_recipes():
    print("Importing recipes...")
    # Run the import_recipes.py script
    result = subprocess.run([sys.executable, 'import_recipes.py'], 
                            capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)
    
    # Check if we have recipes
    with app.app_context():
        recipe_count = Recipe.query.count()
        print(f"Database contains {recipe_count} recipes.")
    
    return recipe_count > 0

def run_app():
    print("Starting Flask application...")
    # Run the app with a different port and no debug to prevent reloading
    os.environ['FLASK_RUN_PORT'] = '5002'
    os.environ['FLASK_DEBUG'] = '0'
    subprocess.run([sys.executable, 'app.py'])

if __name__ == "__main__":
    # Kill any existing Flask processes
    if sys.platform == 'darwin' or sys.platform.startswith('linux'):
        os.system('pkill -f "python3 app.py"')
    elif sys.platform == 'win32':
        os.system('taskkill /f /im python.exe')
    
    time.sleep(1)  # Wait for processes to terminate
    
    if reset_database():
        import_recipes()
        run_app()
    else:
        print("Failed to reset database. Aborting.")
        sys.exit(1) 