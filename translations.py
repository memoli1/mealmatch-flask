# -*- coding: utf-8 -*-
"""
This module contains translations for ingredients between English and Italian.
"""

# Unit translations
UNIT_TRANSLATIONS = {
    'ml': 'ml',
    'l': 'l',
    'g': 'g',
    'kg': 'kg',
    'tbsp': 'cucchiaio',
    'tsp': 'cucchiaino',
    'cup': 'tazza',
    'piece': 'pezzo',
    'pieces': 'pezzi',
    'slice': 'fetta',
    'slices': 'fette',
    'clove': 'spicchio',
    'cloves': 'spicchi',
    'bunch': 'mazzo',
    'pinch': 'pizzico',
    'dash': 'goccio',
    'to taste': 'quanto basta'
}

# Ingredient translations (English to Italian and vice versa)
INGREDIENT_TRANSLATIONS = {
    # Proteins
    'chicken': 'pollo',
    'beef': 'manzo',
    'pork': 'maiale',
    'fish': 'pesce',
    'shrimp': 'gamberi',
    'eggs': 'uova',
    'tofu': 'tofu',
    'lentils': 'lenticchie',
    'beans': 'fagioli',
    'chickpeas': 'ceci',
    'chicken breast': 'petto di pollo',
    
    # Grains and Starches
    'rice': 'riso',
    'pasta': 'pasta',
    'quinoa': 'quinoa',
    'bread': 'pane',
    'flour': 'farina',
    'potatoes': 'patate',
    'sweet potatoes': 'patate dolci',
    'corn': 'mais',
    'oats': 'avena',
    'jasmine rice': 'riso basmati',
    
    # Vegetables
    'tomatoes': 'pomodori',
    'onion': 'cipolla',
    'garlic': 'aglio',
    'carrot': 'carota',
    'potato': 'patata',
    'lettuce': 'lattuga',
    'spinach': 'spinaci',
    'mushroom': 'funghi',
    'pepper': 'peperone',
    'bell pepper': 'peperone',
    'bell peppers': 'peperoni',
    'eggplant': 'melanzana',
    'zucchini': 'zucchine',
    'broccoli': 'broccoli',
    'cauliflower': 'cavolfiore',
    'cabbage': 'cavolo',
    'celery': 'sedano',
    'cucumber': 'cetriolo',
    'asparagus': 'asparagi',
    'artichoke': 'carciofo',
    'fennel': 'finocchio',
    'leek': 'porro',
    'bamboo shoots': 'germogli di bambù',
    
    # Fruits
    'apple': 'mela',
    'lemon': 'limone',
    'orange': 'arancia',
    'banana': 'banana',
    'strawberry': 'fragola',
    'blueberry': 'mirtillo',
    'peach': 'pesca',
    'pear': 'pera',
    'grape': 'uva',
    'cherry': 'ciliegia',
    'coconut': 'cocco',
    
    # Dairy
    'cheese': 'formaggio',
    'milk': 'latte',
    'butter': 'burro',
    'cream': 'panna',
    'yogurt': 'yogurt',
    'parmesan': 'parmigiano',
    'mozzarella': 'mozzarella',
    'coconut milk': 'latte di cocco',
    
    # Herbs and Spices
    'basil': 'basilico',
    'oregano': 'origano',
    'rosemary': 'rosmarino',
    'thyme': 'timo',
    'sage': 'salvia',
    'parsley': 'prezzemolo',
    'mint': 'menta',
    'cinnamon': 'cannella',
    'nutmeg': 'noce moscata',
    'ginger': 'zenzero',
    'turmeric': 'curcuma',
    'cumin': 'cumino',
    'coriander': 'coriandolo',
    'thai basil': 'basilico thailandese',
    'green curry paste': 'pasta di curry verde',
    
    # Other common ingredients
    'olive oil': 'olio d\'oliva',
    'salt': 'sale',
    'pepper': 'pepe',
    'sugar': 'zucchero',
    'palm sugar': 'zucchero di palma',
    'honey': 'miele',
    'vinegar': 'aceto',
    'soy sauce': 'salsa di soia',
    'fish sauce': 'salsa di pesce',
    'mustard': 'senape',
    'ketchup': 'ketchup',
    'mayonnaise': 'maionese',
    'pesto': 'pesto',
    'tomato sauce': 'salsa di pomodoro',
    'chicken broth': 'brodo di pollo',
    'vegetable broth': 'brodo vegetale',
    'wine': 'vino',
    'beer': 'birra',
    'nuts': 'frutta secca',
    'almonds': 'mandorle',
    'walnuts': 'noci',
    'hazelnuts': 'nocciole',
    'peanuts': 'arachidi',
    'seeds': 'semi',
    'sunflower seeds': 'semi di girasole',
    'pumpkin seeds': 'semi di zucca',
    'sesame seeds': 'semi di sesamo'
}

# Create reverse translation dictionary (Italian to English)
REVERSE_TRANSLATIONS = {v: k for k, v in INGREDIENT_TRANSLATIONS.items()}

def translate_ingredient_with_quantity(ingredient_text, target_lang='en'):
    """
    Translate an ingredient with its quantity and unit to the target language.
    Example: "400ml coconut milk" -> "400ml latte di cocco"
    """
    print(f"Translating ingredient with quantity: {ingredient_text} to {target_lang}")
    
    if not ingredient_text:
        return ingredient_text
        
    # Split the ingredient text into parts
    parts = ingredient_text.split()
    print(f"Parts: {parts}")
    
    # Try to find quantity and unit
    quantity = None
    unit = None
    ingredient = []
    
    for part in parts:
        # Check if part is a number or contains a number
        if any(c.isdigit() for c in part):
            quantity = part
            print(f"Found quantity: {quantity}")
        # Check if part is a unit
        elif part.lower() in UNIT_TRANSLATIONS:
            unit = part.lower()
            print(f"Found unit: {unit}")
        else:
            ingredient.append(part)
    
    # Join the ingredient parts
    ingredient_text = ' '.join(ingredient)
    print(f"Looking for ingredient: {ingredient_text}")
    
    # Try to find the ingredient in the translations
    translated_ingredient = None
    for key in INGREDIENT_TRANSLATIONS:
        if key.lower() in ingredient_text.lower():
            print(f"Found matching key: {key}")
            if target_lang == 'it':
                translated_ingredient = INGREDIENT_TRANSLATIONS[key]
            else:
                translated_ingredient = key
            break
    
    # If no translation found, use the original text
    if translated_ingredient is None:
        print("No translation found, using original")
        translated_ingredient = ingredient_text
    
    # Reconstruct the string
    result = []
    if quantity:
        result.append(quantity)
    if unit:
        if target_lang == 'it':
            result.append(UNIT_TRANSLATIONS.get(unit, unit))
        else:
            result.append(unit)
    result.append(translated_ingredient)
    
    final_result = ' '.join(result)
    print(f"Final translation: {final_result}")
    return final_result

def translate_ingredient(ingredient, target_lang='en'):
    """Translate an ingredient to or from English"""
    print(f"Translating ingredient: {ingredient} to {target_lang}")
    
    if not ingredient:
        return ingredient
        
    ingredient = ingredient.lower().strip()
    
    # Try to find the ingredient in the translations
    for key in INGREDIENT_TRANSLATIONS:
        if key.lower() in ingredient.lower():
            print(f"Found matching key: {key}")
            if target_lang == 'it':
                return INGREDIENT_TRANSLATIONS[key]
            else:
                return key
    
    # If no translation found, return the original
    print("No translation found, using original")
    return ingredient 