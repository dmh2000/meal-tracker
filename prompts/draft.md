create a  progrssive single page web app that logs food, calories, meals on a daily basis. 

# Users
- 
# Front End
- it will support multiple users with id and password
- when a user logs in, the app will remember the user so it won't have to login again unless it is logged out
- it will support 6 meals per day
  - breakfast
  - morning snack
  - lunch
  - afternoon snack
  - dinner
  - evening snack
- the landing page will show buttons for opening pages for each of the 6 daily meal types
- the landing page will show the total calories for the current date
- user logging
  - 
- meals  
  - the meal and food item data is global to all users.
  - meals are logged based on the local date
  - the the meal pages will show the total calories for that meal
  - the meal pages allow entering any number of food items
  - every meal will have a unique name
  - data entry
    - the user can select food items from a list
    - the user can enter new food items along with their calorie count
    - the user can select existing meals content from a list. only existing meals that have a description will be shown in the list
     - if the user selects an existing meal the app will populate the current meal items from that data
  - the user will be able to specify a name  for a meal or leave it blank
  - if the user names a meal, it is stored with the name. 
  - there will be a save button for the meals
  - the user can come back and modify any meal for the current day. 
  - the user cannot modify meals for previous days
- the front end is created using Vite with tyoescript, react and tailwind css 

# Web Server
- the web app will be served by a python web server using flask
- the web server will have a command line argument for the listening port
- the web server will be separate from the database api sever

# Database API
- the database API will be served by a python web server using flash and sqlite3
- the database API server will have a command line for the listening port
- the database API server will support methods as required by the front end functionality
- file @db/schema.sql is a proposed scheme. it is probably incomplete so update date it as necessary to support the required operations.