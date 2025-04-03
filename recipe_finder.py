import tkinter as tk
from tkinter import ttk, messagebox, font
import json
from typing import List, Dict, Tuple

class RecipeFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Finder")
        self.root.geometry("800x700")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TLabelframe', font=('Helvetica', 10, 'bold'))
        self.style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'))
        
        # Create custom fonts
        self.title_font = font.Font(family='Helvetica', size=12, weight='bold')
        self.recipe_font = font.Font(family='Helvetica', size=11, weight='bold')
        self.ingredient_font = font.Font(family='Helvetica', size=10)
        self.instruction_font = font.Font(family='Helvetica', size=10)
        
        # Load recipes from JSON file
        try:
            with open('recipes.json', 'r') as file:
                self.recipes = json.load(file)['recipes']
        except FileNotFoundError:
            messagebox.showerror("Error", "Recipes file not found!")
            self.recipes = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Recipe Finder", font=self.title_font)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Ingredients input
        ttk.Label(main_frame, text="Enter ingredients (comma-separated):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ingredients_entry = ttk.Entry(main_frame, width=50, font=self.ingredient_font)
        self.ingredients_entry.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=tk.W, pady=10)
        
        # Search button
        search_button = ttk.Button(button_frame, text="Find Recipes", command=self.find_recipes)
        search_button.grid(row=0, column=0, padx=(0, 10))
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_results)
        clear_button.grid(row=0, column=1)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Matching Recipes", padding="15")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create a text widget for displaying results
        self.results_text = tk.Text(results_frame, height=25, width=80, wrap=tk.WORD, 
                                  font=self.instruction_font, padx=10, pady=10)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text['yscrollcommand'] = scrollbar.set
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.ingredients_entry.delete(0, tk.END)
    
    def find_recipes(self):
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Get user input
        user_ingredients = [ing.strip().lower() for ing in self.ingredients_entry.get().split(',')]
        
        if not user_ingredients:
            messagebox.showwarning("Warning", "Please enter at least one ingredient!")
            return
        
        # Find matching recipes
        matching_recipes = []
        for recipe in self.recipes:
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
        
        if not matching_recipes:
            self.results_text.insert(tk.END, "No recipes found with the given ingredients.")
            return
        
        # Display results
        for i, (recipe, match_percentage, missing) in enumerate(matching_recipes):
            # Add extra spacing between recipes
            if i > 0:
                self.results_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
            
            # Highlight top matches
            if match_percentage >= 80:
                self.results_text.insert(tk.END, "⭐ ", "highlight")
            
            # Recipe name with custom font
            self.results_text.insert(tk.END, f"Recipe: {recipe['name']}\n", "recipe")
            self.results_text.insert(tk.END, f"Match Score: {match_percentage:.1f}%\n", "score")
            
            # Ingredients
            self.results_text.insert(tk.END, "Ingredients:\n", "label")
            self.results_text.insert(tk.END, f"{', '.join(recipe['ingredients'])}\n\n")
            
            # Missing ingredients
            if missing:
                self.results_text.insert(tk.END, "Missing Ingredients:\n", "label")
                self.results_text.insert(tk.END, f"{', '.join(missing)}\n\n")
            
            # Instructions
            self.results_text.insert(tk.END, "Instructions:\n", "label")
            self.results_text.insert(tk.END, f"{recipe['instructions']}\n")
        
        # Configure text tags for styling
        self.results_text.tag_configure("recipe", font=self.recipe_font)
        self.results_text.tag_configure("score", foreground="blue")
        self.results_text.tag_configure("label", font=self.recipe_font)
        self.results_text.tag_configure("highlight", foreground="gold")

def main():
    root = tk.Tk()
    app = RecipeFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main() 