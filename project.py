# importing all the librarires
import tkinter as tk
from PIL import Image, ImageTk
import requests
import io
import os

# making a function for the search button
def search():
    # in the search button i want a slider for all the search results available
    # the reason im using global variable is to avaiod any error that a mealcanvaslist is not defined
    # so i defined it as none outside the function and now using that variable in the fuction
    global mealcanvaslist
    # storing user's searched text in a variable
    search_text = search_entry.get()

    # so when user clicks the search again it clears the previous widgets in result canvas
    for widget in result_canvas.winfo_children():
        widget.destroy()

    if search_text:
        # using api link for searching meals by name
        api_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={search_text}"
        # requesting the link and storing data got from api in a variable 
        response = requests.get(api_url)
        # after getting data from the website, the data will be converted into json format
        data = response.json()
        # storing all the results in meals
        meals = data.get("meals", [])

        if meals:
            # displaying all the meals that are available and calling the dispay all meals function
            display_all_meals(meals)
        else:
            # display a message if no meals were found
            result_label = tk.Label(result_canvas, text="No meals found", bg="#FFF1C1")
            result_label.pack()
    else:
        # displaying a message if the user did not type anything and pressesd search with empty entry
        result_label = tk.Label(result_canvas, text="Please enter a meal name", bg="#FFF1C1")
        result_label.pack()

    # updating the scrollbar the canvas configuration for scrolling
    result_canvas.update_idletasks()
    mealcanvaslist.configure(scrollregion=mealcanvaslist.bbox("all"))

# this function is for displaying all the meals search result as a button in a scollbar
def display_all_meals(meals):
    global mealcanvaslist  # Use the global variable

    # Clear previous details in recipe_canvas2 and result frame
    for widget in recipe_canvas2.winfo_children():
        widget.destroy()

    # creating a canvas for the scrollable area with a fixed height, because whatever doesn't fit in the height can be scrolled to see it
    mealcanvaslist = tk.Canvas(result_canvas)
    mealcanvaslist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0,0))

    # creating a frame inside the mealcanvaslist to hold the box frames
    # its also a box wrapper but im calling i meal wrapper
    # basically the wrapper will hold all the buttons of al meals available
    # and then i will scroll the mealwrapper only without scrolling individual child
    # thats why im making the mealwrapper a parent to avoid scrolling each indivdual child but to move all the childfren
    # or to move all the buttons as a group
    mealwrapper = tk.Frame(mealcanvaslist, bg="#FFF1C1")
    mealcanvaslist.create_window((0, 0), window=mealwrapper, anchor=tk.NW)
    # displaying all the search results as a button in a layout which is 3 buttons per column
    row = 0
    col = 0
    for meal_data in meals:
        # Extract relevant information from the API response
        meal_name = meal_data.get("strMeal", "")
        meal_image_url = meal_data.get("strMealThumb", "")

        # Create a button containing both image and text with a max-width
        # each button will have 2 things, image and name of the respective meal and when u click any button it will call a function to show the recipe
        btn = tk.Button(mealwrapper, text=meal_name, font=("Helvetica", 10, "bold"), command=lambda m=meal_data: display_meal_details(m), wraplength=100, bg="#FFDACB", fg="#F45800")
        # requesting api to get image
        img_data = requests.get(meal_image_url).content
        image = Image.open(io.BytesIO(img_data)).resize((100, 100), Image.BICUBIC)
        photo_image = ImageTk.PhotoImage(image)
        btn.config(image=photo_image, compound=tk.TOP)
        btn.image = photo_image
        btn.grid(row=row, column=col, padx=10, pady=10)
        # each new button will be added to the next column
        if col < 3 :
            btn.grid(padx=10)
        # column increased by 1 for the next button
        col += 1
        # if column is equal to 3 which is the 4th column then it will increase the row by 1 and make column 0
        if col == 3:
            col = 0
            row += 1
            btn.grid(padx=10)

    # Adding horizontal scrollbars to the canvas
    scrollbar_y = tk.Scrollbar(result_canvas, command=mealcanvaslist.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    mealcanvaslist.configure(yscrollcommand=scrollbar_y.set)

# this function is made to display the recipe of the respective meal of the button user clicks on
def display_meal_details(meal_data):
    # clearing the previous search details in recipe_canvas2
    for widget in recipe_canvas2.winfo_children():
        widget.destroy()

    # Display meal image
    img_data = requests.get(meal_data["strMealThumb"]).content
    image = Image.open(io.BytesIO(img_data)).resize((150, 150), Image.BICUBIC)
    photo_image = ImageTk.PhotoImage(image)
    image_label = tk.Label(recipe_canvas2, image=photo_image)
    image_label.image = photo_image
    image_label.pack(pady=5)

    # Display meal name
    name_label = tk.Label(recipe_canvas2, text=meal_data["strMeal"], font=("Helvetica", 16, "bold"), bg="#FFF1C1", fg="#F45800")
    name_label.pack(pady=10)

    # requesting the api for the recipe of the meal
    recipe_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_data['idMeal']}"
    # storing the response of api in  variable
    recipe_response = requests.get(recipe_url)
    # converting in json file
    recipe_data = recipe_response.json()
    # [0] for getting only the first element in the list for displaying the recipe of the respective meal
    recipe = recipe_data.get("meals", [])[0]
    # displaying the recipe in a scrollable text widget
    recipe_text = tk.Text(recipe_canvas2, wrap=tk.WORD, height=10, width=80, font=("Helvetica", 10), bg="#1F0D02", fg="#FFFFFF")
    # getting the value associated with the key "strInstructions" from the recipe dictionary. If the key is not present, it returns an empty string.
    recipe_text.insert(tk.END, recipe.get("strInstructions", ""))
    # the recipe text cannot be edited by the user
    recipe_text.config(state=tk.DISABLED)
    recipe_text.pack()
    scrollbar_y = tk.Scrollbar(recipe_canvas2, command=recipe_text.yview)
    scrollbar_y.pack()
    recipe_text.configure(yscrollcommand=scrollbar_y.set)

root = tk.Tk()
root.title("Meal Recipe GUI")
root.geometry("800x400")
root.resizable(0, 0)

# Setting up a bg image on the root window
bg_image_path = os.path.join(os.path.dirname(__file__), "cookingbg.png")
original_bg_image = Image.open(bg_image_path)
resized_bg_image = ImageTk.PhotoImage(original_bg_image.resize((800, 400), Image.BICUBIC))
bg_label = tk.Label(root, image=resized_bg_image)
bg_label.place(relwidth=1, relheight=1)

# Frames inside root
canvas1 = tk.Canvas(root, highlightthickness=0, highlightbackground=None, height=100, bg="#FFF1C1")
canvas1.pack(side=tk.LEFT, padx=10)
recipe_canvas2 = tk.Canvas(root, highlightthickness=0, highlightbackground="#ffffff", bg="#FFF1C1")
recipe_canvas2.pack(side=tk.LEFT, padx=10)

# Children of frame 1

# Child one SEARCH
search_canvas = tk.Canvas(canvas1, highlightthickness=0, highlightbackground="#ffffff", bg="#FFF1C1")
search_canvas.pack(side="top", pady=(0,0))
# children of search
search_label = tk.Label(search_canvas, text="Search for a meal:", bg="#FFF1C1")
search_label.grid(row=0, column=0, padx=5, pady=5)
search_entry = tk.Entry(search_canvas, width=30)
search_entry.grid(row=0, column=1, padx=5, pady=5)
search_button = tk.Button(search_canvas, text="Search", command=search, bg="#FF8E4E")
search_button.grid(row=1, columnspan=2, padx=5, pady=5)

# Child two RESULT
result_canvas = tk.Canvas(canvas1, highlightthickness=0, highlightbackground="#ffffff")
result_canvas.pack(side="top", pady=(0,0))



# this is an empty variable which is put to scroll the mealwrapper later on in the result 
mealcanvaslist = None

root.mainloop()
