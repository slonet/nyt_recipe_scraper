"""
nyt_recipe_converter.py downloads the HTML for the page for a specified recipe number.
Search for the recipe you want and grab the recipe number out of the URL.

Search here: https://cooking.nytimes.com/search
Recipe URL: https://cooking.nytimes.com/recipes/"RECIPE_NUMBER"-"RECIPE NAME"

nyt_recipe_converter.py then extracts the title, description, ingredients list, 
and the preparation steps from the HTML.

the recipe is output as a text file.
"""

"""
NOTES:
- HTML file area of interest
	- Beginning of useful info always after <script type="application/ld+json">
	- End of useful info always after ,"isAccessibleForFree":
- Recipe title
	- Defined as "name":"RECIPE TITLE"


"""

### TODO:
# Fix steps parsing when there is a video link on the page

import urllib.request

_recipe_url = "https://cooking.nytimes.com/recipes/***" # *** to be replaced by the recipe number
_max_fails = 20


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

		return html_data


def strip_content(html_data):
	stripped_html_data = html_data.split("<script type=\"application/ld+json\">")[1]
	stripped_html_data = stripped_html_data.split(",\"isAccessibleForFree\":")[0]

	return stripped_html_data


def get_recipe_title(html_data):
	recipe_title = html_data.split("\"@type\":\"Recipe\",\"name\":\"")[1].split("\",\"")[0]

	return recipe_title


def get_recipe_description(html_data):
	recipe_description = html_data.split("\"description\":\"")[1].split("\",\"")[0]

	return recipe_description


def get_recipe_rating(html_data):
	rating_value = 0
	num_ratings = 0
	
	try:
		rating_string = html_data.split("\"aggregateRating\":{")[1].split("},")[0]
		rating_value = int (rating_string.split("\"ratingValue\":")[1].split(",\"")[0])
		num_ratings = int (rating_string.split("\"ratingCount\":")[1])
	
	except:
		pass

	recipe_rating = f"Rating: {rating_value}/5 based on {num_ratings} reviews."

	return recipe_rating


def get_recipe_ingredients(html_data):
	ingredients_string = html_data.split("\"recipeIngredient\":[")[1]
	ingredients_string = ingredients_string.split("],\"recipeInstructions\"")[0]

	recipe_ingredients = ingredients_string.strip("\"").split("\",\"") # creates a list of ingredients

	ind = 0

	for i in recipe_ingredients:
		recipe_ingredients[ind] = "- " + i
		ind += 1

	return recipe_ingredients


def parse_howtosection(steps_string):
	raw_sections = steps_string.split("{\"@context\":\"http://schema.org\",\"@type\":\"HowToSection\",\"name\":\"")
	raw_sections.pop(0) # 1st element is always empty

	parsed_sections = []

	for section in raw_sections: # makes a 2D list of sections. each section contains steps. 1st element is the section title.
		section = section.replace(":\",\"itemListElement\":[", "")
		section = section.replace("\"},", "")
		section = section.replace("\"}", "")
		section = section.replace("]},", "")

		parsed_sections.append(section.split("{\"@context\":\"http://schema.org\",\"@type\":\"HowToStep\",\"text\":\""))

	step_count = 1

	for section in parsed_sections:
		ind = 1
		num_steps = len(section)

		while ind < num_steps:
			section[ind] = f"\t{step_count}. " + section[ind] # add a tab and the step number to each step
			ind += 1
			step_count += 1

	steps = []

	for section in parsed_sections:
		section[0] = "\n" + section[0] # add a new line at every section header
		
		for step in section:
			steps.append(step) # flatten the list to 1D

	return steps


def parse_howtosteps(steps_string):
	steps_string = steps_string.replace("{\"@context\":\"http://schema.org\",\"@type\":\"HowToStep\",\"text\":\"", "")

	recipe_steps = steps_string.split("\"},") # creates a list of steps

	ind = 0

	for i in recipe_steps: # add step numbers
		recipe_steps[ind] = f"{ind + 1}. " + i
		ind += 1

	return recipe_steps


def get_recipe_steps(html_data):
	steps_string = html_data.split("\"recipeInstructions\":[")[1].strip("\"}]")
	recipe_steps = []

	try:
		steps_string.index("\"@type\":\"HowToSection\"") # if this string is present, we have a HowToSection formatted page
		recipe_steps = parse_howtosection(steps_string)

	except: # if it's not present we have a HowToSteps formatted page 
		recipe_steps = parse_howtosteps(steps_string)
		

	return recipe_steps


def generate_recipe_file(html_data):
	recipe_title = get_recipe_title(html_data)
	recipe_description = get_recipe_description(html_data)
	recipe_ingredients = get_recipe_ingredients(html_data)
	recipe_steps = get_recipe_steps(html_data)

	file_name = recipe_title.replace(" ", "") + ".txt"

	with open(file_name, 'w', encoding='utf-8') as file:
		file.write(recipe_title + "\n\n")
		file.write(recipe_description + "\n\n\n")

		for i in recipe_ingredients:
			file.write(i + "\n")

		file.write("\n\n")

		for i in recipe_steps:
			file.write(i + "\n\n")

	print("\nGenerated the recipe file: " + file_name)


def scrape_recipes():
	page_number = 1
	fails = 0
	successes = 0

	while True:
		try:
			html_data = get_html_data(page_number)
			generate_recipe_file(html_data)
			
			fails = 0
			successes += 1

			print(f"Scraped {successes} recipes.\n")


		except:
			raise
			#fails += 1
			#print(f"Failed to get recipe page {fails} times.")

			#if fails >= _max_fails:
				#print("Maximum number of failed attempts. Stopping.")
				#break

		page_number += 1


recipe_number = get_recipe_number()
html_data = get_html_data(recipe_number)
stripped_html_data = strip_content(html_data)
print(get_recipe_title(stripped_html_data) + "\n\n")
print(get_recipe_description(stripped_html_data) + "\n\n")
print(get_recipe_rating(stripped_html_data) + "\n\n")
#print(get_recipe_ingredients(stripped_html_data))
steps = get_recipe_steps(stripped_html_data)

with open("steps_list.txt", 'w', encoding='utf-8') as file:
	for step in steps:
		file.write(step + "\n")

with open("stripped_html_data.txt", 'w', encoding='utf-8') as file:
	file.write(stripped_html_data)