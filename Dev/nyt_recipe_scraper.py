"""
nyt_recipe_scraper.py navigates through all available search results pages when no search term or filter is applied.

All valid recipe urls are collected. The urls are then fed to nyt_recipe_converter.py to convert all recipes into text files.

This should download all available NYT cooking recipies.
"""

"""
NOTES
- Identifying recipe urls
	- Each recipe card contains a link to the associated recipe or if it is a collection, a link to the collection
	- Recipe links are always formatted like href="/recipes/RECIPE_NUMBER-RECIPE_NAME"
"""

import urllib.request

_recipe_numbers = []
_search_url = "https://cooking.nytimes.com/search?page=***" # *** to be replaced with the search page number


def get_search_page(page_number):
	full_url = _search_url.replace("***", str (page_number))	
	
	with urllib.request.urlopen(full_url) as html_obj:
		html_data = html_obj.read().decode('utf-8')

		return html_data


def extract_recipe_numbers(html_data):
	recipe_strings = html_data.split("href=\"/recipes/")
	global _recipe_numbers

	for i in recipe_strings:
		i = i.split("-")
		
		try: # using exceptions to identify integers and ignore recipe numbers that are duplicated
			recipe_number = int (i[0]) # if there is an integer in the 1st substring it will be cast
			
			try: # need to reverse the logic of the .index() method to raise an exception when the element is present
				_recipe_numbers.index(recipe_number) # see if the number is already in the list
				raise Exception
			
			except:
				pass
			
			_recipe_numbers.append(recipe_number) # if the substring is an integer and it does not exist in the global list, append it

		except:
			pass

	return


def scrape_recipe_numbers():
	page_number = 1
	attempts = 0

	while True:
		print(f"Scraping search page No. {page_number}")

		last_length = len(_recipe_numbers)
		html_data = get_search_page(page_number)
		extract_recipe_numbers(html_data)

		print(f"Scraped {len(_recipe_numbers)} recipes\n")

		if len(_recipe_numbers) == last_length: # no change to the list means we are out of results, try 5 times
			attempts += 1
			print(f"Did not add any unique recipes {attempts} times. Trying again.")

			if attempts >= 4:
				print("Tried too many times. Stopping.")
				break
		
		else:
			attempts = 0

		page_number += 1

	return


def get_recipe_numbers():

	return _recipe_numbers


scrape_recipe_numbers()