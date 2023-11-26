"""
nyt_recipe_scraper.py downloads the HTML for the page for a specified recipe number.
Search for the recipe you want and grab the recipe number out of the URL.

Search here: https://cooking.nytimes.com/search
Recipe URL: https://cooking.nytimes.com/recipes/"RECIPE_NUMBER"-"RECIPE NAME"

nyt_recipe_scraper.py then extracts the title, description, ingredients list, 
and the preparation steps from the HTML.

the recipe is output as a text file.
"""

### TODO:
# Fix steps parsing when there is a video link on the page

import urllib.request

_recipe_url = "https://cooking.nytimes.com/recipes/***" # *** to be replaced by the recipe number


def get_recipe_number():
	recipe_number = 0

	try:
		user_input = input("Please enter the recipe number\n> ")
		recipe_number = int (user_input) # if we cannot cast to an int, exception will be caught

	except:
		print("\nIncorrect number format...")
		get_recipe_number() # Keep trying to get the input right forever

	return recipe_number


def get_html_data(recipe_number):
	full_url = _recipe_url.replace("***", str (recipe_number))	
	
	with urllib.request.urlopen(full_url) as html_obj:
		html_data = html_obj.read().decode('utf-8')
		updated_url = html_obj.url

		return html_data, updated_url


def get_recipe_title(html_data):
	recipe_title = html_data.split("title>")[1].replace(" Recipe - NYT Cooking</", "")

	return recipe_title


def get_recipe_description(html_data):
	recipe_description = html_data.split("name=\"description\" content=\"")[1]
	recipe_description = recipe_description.split("><meta name=\"robots\"")[0]
	recipe_description = recipe_description.split("\"/><link rel=\"shortcut icon\"")[0]

	return recipe_description


def get_recipe_ingredients(html_data):
	ingredients_string = html_data.split("\"recipeIngredient\":[")[1]
	ingredients_string = ingredients_string.split("],\"recipeInstructions\"")[0]

	recipe_ingredients = ingredients_string.strip("\"").split("\",\"") # creates a list of ingredients

	ind = 0
	for i in recipe_ingredients:
		recipe_ingredients[ind] = "- " + i
		ind += 1

	return recipe_ingredients


def get_recipe_steps(html_data):
	steps_string = html_data.split("\"recipeInstructions\":[")[1]
	steps_string = steps_string.split("],\"isAccessibleForFree\":")[0].replace("{\"@context\":\"http://schema.org\",\"@type\":\"HowToStep\",\"text\":\"", "")
	steps_string = steps_string.strip("\"}")

	recipe_steps = steps_string.split("\"},") # creates a list of steps

	ind = 0
	for i in recipe_steps: # add step numbers
		recipe_steps[ind] = f"{ind + 1}. " + i
		ind += 1

	return recipe_steps


def generate_recipe_file(html_data):
	recipe_title = get_recipe_title(html_data)
	recipe_description = get_recipe_description(html_data)
	recipe_ingredients = get_recipe_ingredients(html_data)
	recipe_steps = get_recipe_steps(html_data)

	file_name = recipe_title.replace(" ", "") + ".txt"

	with open(file_name, 'w') as file:
		file.write(recipe_title + "\n\n")
		file.write(recipe_description + "\n\n\n")

		for i in recipe_ingredients:
			file.write(i + "\n")

		file.write("\n\n")

		for i in recipe_steps:
			file.write(i + "\n\n")

	print("\nGenerated the recipe file: " + file_name)


recipe_number = get_recipe_number()
html_data = get_html_data(recipe_number)[0]
generate_recipe_file(html_data)