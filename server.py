from flask import Flask, render_template, redirect, request, session, flash
import re, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
from flask.ext.bcrypt import Bcrypt
from mysqlconnection import MySQLConnector
app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector('bad_day')
app.secret_key = 'abc123doremi'

# note: can assign variables and run SQL checks up here that happen for all webpages, can't call Session from up here.



@app.route('/')
def index():
	# destroys the session['profile'] in the event that the user came from a profile page so as to reduce clutter in the session
	try:
		session['profile']
		session.pop['profile']
	except: 
		# Harmless variable assignment to complete the try/except statement. Couldn't do an if statement because if the session profile didn't exist, it would crash the program
		pass
	# Note: Set it so that it's consistent across time zones later
	# sets variables for today and yesterday
	date = str(datetime.date.today())
	yesterday = str(datetime.date.today() - datetime.timedelta(days = 1))

	session['date'] = date
	# Data for the carousel.
	session['carousel'] = mysql.fetch("SELECT stories.story, stories.thumbs_up, stories.id, stories.thumbs_down, users.user_name FROM stories LEFT JOIN users ON stories.user_id = users.id order by stories.updated_at DESC LIMIT 3")
	# Determines if the daily winner has been found for yesterday yet
	yesterday_winner = mysql.fetch("SELECT days_have_winners.story_id, stories.story FROM days_have_winners LEFT JOIN stories ON stories.id = days_have_winners.story_id WHERE stories.created_at = '{}'".format(yesterday))
	if not yesterday_winner:
		yesterday_contestants = mysql.fetch("SELECT id, user_id, thumbs_up FROM stories WHERE created_at = '{}'".format(yesterday))
		# avoids errors if there were no posts yesterday
		if yesterday_contestants:
			# determines the winner
			yardstick = {'thumbs_up': 0, 'id': 0}
			for item in yesterday_contestants:
				# compares the number of thumbs_up in item to the yardstick
				if yardstick['thumbs_up'] < item['thumbs_up']:
					yardstick = item
			#assigns new winner based on the yardstick 
			mysql.run_mysql_query("INSERT INTO days_have_winners (story_id, user_id, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(yardstick['id'], yardstick['user_id'])) 
			# assigns the new item in the days_have_winners table value to the yesterday_winner variable
			yesterday_winner = mysql.fetch("SELECT days_have_winners.story_id, stories.story, FROM days_have_winners  LEFT JOIN stories ON stories.id = days_have_winners.story_id WHERE stories.created_at = '{}'".format(yesterday))
	# either way, assign this data to the session
	session['winner'] = yesterday_winner
	return render_template('index.html')



# Logs the user in
@app.route('/login', methods = ['POST'])
def login():
	# Prevents users from writing apostrophes and quotation marks in the e-mail address 
	if "'" in request.form['email'] or '"' in request.form['email']:
		flash('Invalid e-mail. Please try again.')
		return redirect('/') 
	# Checks to see if the email exists in the database
	query = mysql.fetch("SELECT password, user_name FROM users WHERE email = '{}'".format(request.form['email']))
	# Checks to see if the query returned anything. 
	if not query:
		# Flashes error if there isn't anything in the query.
		flash('Sorry, that e-mail is not in the system. Please try again.')
	# Continues check, sees if the given e-mail matches
	elif not bcrypt.check_password_hash(query[0]['password'], request.form['password']):
		flash('Sorry, that password does not match.')

	# If e-mail and password work out, log in the user.
	else:
		# as long as session['name'] exists, the user is logged in
		session['name'] = query[0]['user_name']
	# Regardless it redirects back to the home page.
	return redirect('/view')

# Takes user to message board page
@app.route('/view')
def view():
	# destroys the session['profile'] in the event that the user came from a profile page so as to reduce clutter in the session
	try:
		session['profile']
		session.pop['profile']
	except: 
		# Harmless variable assignment to complete the try/except statement. Couldn't do an if statement because if the session profile didn't exist, it would crash the program
		session['date'] = 0
	# Note: Set it so that it's consistent across time zones
	date = str(datetime.date.today())
	session['date'] = date
	# Data for the Vents
	session['vents'] = mysql.fetch("SELECT stories.story, stories.thumbs_up, stories.id, stories.thumbs_down, users.user_name FROM stories LEFT JOIN users ON stories.user_id = users.id WHERE stories.created_at = '{}' order by stories.updated_at".format(date))	
	# Displays most recent winner 
	session['winner'] = mysql.fetch("SELECT stories.story, stories.created_at, stories.thumbs_up, stories.thumbs_down, users.user_name FROM days_have_winners LEFT JOIN stories ON stories.id = days_have_winners.story_id LEFT JOIN users ON users.id = stories.user_id ORDER BY days_have_winners.updated_at desc LIMIT 1")
	return render_template('view.html')

# opens the About page
@app.route('/about')
def about():
	return render_template('about.html')

# Registration Page
@app.route('/registration')
def registration():
	return render_template('register.html')

# Registers the user
@app.route('/register', methods = ['POST'])
def register():

	errors = []
	# Is the name long enough?
	if (len(request.form['username']) <= 2):
		errors.append("Your username needs to be at least 3 characters long.")
	# Only letters, numbers and certain characters allowed in the username
	if not re.match(r'^[a-zA-Z0-9\.\+_-]*$', request.form['username']):
		errors.append("Your username can only contain letters, numbers, underscores and hyphens.")
	# Is the email long enough? Is it a valid format?
	if not re.match(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$', request.form['email']):
		errors.append("Your email is invalid.")
	#Is the password long enough?
	if (len(request.form['password']) <8):
		errors.append("Your password isn't long enough.")
	# Does the password confirmation match?
	if not(request.form['confirm'] == request.form['password']):
		errors.append("Your passwords need to match.")
	# If there are errors, reports them to the user
	if errors:
		# prevents display errors when there is only one error
		errors.append('')
		flash(errors)
		return redirect('/registration')

	# If there are no errors, log the user in and redirect them to the main page

	#Check out if the user name or email is already in the system.
	else: 
		query = mysql.fetch("SELECT email, user_name FROM users WHERE email = '{}'".format(request.form['email']))
		if query:
			errors.append("That username or email is already taken. Please choose another.")
			errors.append('')
			flash(errors)
			return redirect('/registration')
		# User doesn't exist, create them, redirect to the index
		else:
			flash('Welcome to the site!')
			pw_hash = bcrypt.generate_password_hash(request.form['password'])
			mysql.run_mysql_query("INSERT INTO users (user_name, email, password, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(request.form['username'], request.form['email'], pw_hash))
			session['name'] = request.form['username']
			return redirect('/view')

# logs out the user
@app.route('/logout')
def logout():
	# sees if the session['name'] is filled in
	if session['name']:
		session.clear()
		flash('Successfully logged out. See you soon!')
		return redirect('/')

# User posts vent
@app.route('/publish', methods = ['POST'])
def publish():
	# Checks to make sure user is logged in
	# If user is not logged in, display error message
	if not session['name']:
		flash('Sorry, you have to be logged in to post.')
	# If the user is logged in, continue.
	else:
	# Stores Vent in a form that can be modified
		vent = request.form['vent']
	# Checks length of Vent
		# Vents can't be longer than 200 characters
		if (len(vent) >= 200):
			flash("Sorry, your Vent can't be longer than 200 characters.")

		# Prevents empty Vents from being posted
		elif (len(vent) <= 0):
			flash("Sorry, you can't submit an empty Vent.")

		# If they are logged in and the Vent is an appropriate length, check for an invalid name in the session. 
		else:
			# Makes sure that the session name matches up with a user_name and gathers the user id
			user = mysql.fetch("SELECT id FROM users WHERE user_name = '{}'".format(session['name']))

			# If there isn't a user, it needs to flash an error message
			if not user:
				flash("Sorry, that user doesn't exist. Please log out and try logging in again.")

			# Users can only vent once per day. A check needs to be run to ensure that they haven't already posted. 
			# Pulls vent data where user and today's date are the same
			else:
				# quickly redefine user variable to one that's more easily parsable
				user = user[0]['id']
				# see if the user has already posted today
				dupes = mysql.fetch("SELECT id FROM stories WHERE user_id = '{}' AND created_at = '{}'".format(user, session['date']))
				# flash error if they have already posted today
				if dupes:
					flash('Sorry, you already posted today. You can post again tomorrow.')
				else:
				# Quickly sanitize the vent against apostrophes and quotation marks
					if "'" in vent:
						vent = vent.replace("'", "''")
				# Otherwise, everything is OK. Add the Vent to the database.
					mysql.run_mysql_query("INSERT INTO stories (story, user_id, thumbs_up, thumbs_down, created_at, updated_at) VALUES ('{}', '{}', 0, 0, '{}', NOW())".format(vent, user, session['date']))
	# returns user to the main page
	return redirect('/view')

@app.route('/vote', methods = ['POST'])
def vote():
	# Makes sure someone isn't trying to vote on their own
	if session['name'] == request.form['user']:
		flash("Sorry, you can't vote on your own Vent.")

	# User isn't trying to vote on their own, passes them along
	else:
		# Makes sure the user hasn't already voted on that Vent
		# Pulls data from the users_have_votes table where the user and the vent ID match the current one
		vote_data = mysql.fetch("SELECT id FROM users WHERE user_name = '{}'".format(session['name']))
		vote_check = mysql.fetch("SELECT * FROM users_have_votes WHERE user_id = '{}' AND story_id = '{}'".format(vote_data[0]['id'], request.form['vent']))
		# If the data exists, then they've already voted on that Vent.
		if vote_check:
			flash('Sorry, you already voted on that one. Thanks for the enthusiasm!')
			return redirect('/')
		# If the user hasn't already voted on this Vent, the users_have_votes table is updated to reflect the new vote
		else:
			mysql.run_mysql_query("INSERT INTO users_have_votes (user_id, story_id) VALUES ('{}', '{}')".format(vote_data[0]['id'], request.form['vent']))
		# Voted Better Than
		if request.form['vote'] == 'better':
			score = mysql.fetch("SELECT thumbs_up FROM stories WHERE id = '{}'".format(request.form['vent']))
			score = score[0]['thumbs_up']
			score = score + 1
			mysql.run_mysql_query("UPDATE stories SET thumbs_up = '{}' WHERE id = '{}'".format(score, request.form['vent']))
		# Voted Worse Than
		else:
			score = mysql.fetch("SELECT thumbs_down FROM stories WHERE id = '{}'".format(request.form['vent']))
			score = score[0]['thumbs_down']
			score = score + 1
			mysql.run_mysql_query("UPDATE stories SET thumbs_down = '{}' WHERE id = '{}'".format(score, request.form['vent']))

	#returns to the main page
	return redirect('/view')

# Adds Vent to a user's favorite 
@app.route('/favorite', methods = ['POST'])
def fave():
	# Pulls the user ID of the current user
	user_id = mysql.fetch("SELECT id FROM users WHERE user_name = '{}'".format(session['name']))
	# Set user_id to simpler form
	user_id = user_id[0]['id']
	# Checks to see if the Vent is already in the user's favorite list
	duplicates = mysql.fetch("SELECT * FROM users_have_favorites WHERE user_id = '{}' AND story_id = '{}'".format(user_id, request.form['vent']))
	if duplicates: 
		flash('You already have that in your favorites.')

	else: 
		# Adds the favorite to the database
		mysql.run_mysql_query("INSERT INTO users_have_favorites (user_id, story_id, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(user_id, request.form['vent']))
		# Flashes a success message
		flash("Favorite added.")
	return redirect('/view')

# Shows you a user profile
@app.route('/profile/<name>')
def show_profile(name):
	# checks to see if that name exists in the system
	bouncer = mysql.fetch("SELECT user_name FROM users WHERE user_name = '{}'".format(name))

	# if the name isn't in the database, the user is immediately redirected to the home page.
	if not bouncer:
		flash("Sorry, that user doesn't exit. Please try again.")
		return redirect('/')

	# stores name on the profile in the session
	session['profile'] = name

	# Pulls user ID
	user_id = mysql.fetch("SELECT id FROM users WHERE user_name = '{}'".format(name))
	# Pulls user's Vents, stores them in the session
	vent_list = mysql.fetch("SELECT story, thumbs_up, thumbs_down, created_at FROM stories WHERE user_id = '{}'".format(user_id[0]['id']))
	session['vent_list'] = vent_list
	# Pulls the stories id of the user's favorite vents
	fave_id = mysql.fetch("SELECT story_id FROM users_have_favorites WHERE user_id = '{}'".format(user_id[0]['id']))
	# creates a list to put the found items into
	fave_list = []
	# iterates and runs sql queries, since there will be mulitple numbers
	for item in fave_id:
		fave_list.append(mysql.fetch("SELECT story, thumbs_up, thumbs_down, created_at FROM stories WHERE id = '{}'".format(item['story_id'])))
	# stores fave_list in the session
	session['fave_list'] = fave_list
	return render_template('/profile.html')

# Opens page that shows all user profiles
@app.route('/show_users')
def show_users():
	# Searches database for the names of all users
	directory = mysql.fetch("SELECT user_name FROM users")
	# Strips the names from the directory variable, stashes the results in the session
	user_list = []
	for key in directory:
		user_list.append(key['user_name'])
	session['directory'] = user_list 
	# Redirects to user list page
	return render_template('/user_list.html')

# Opens page that lets the user search through Vents
@app.route('/search')
def search_home():

	# Clears old search results if the page is refreshed or the user navigates back later
	try: 
		session['search_happened'] == True

	except:
		session['search_happened'] = False

	if session['search_happened'] == False:
		session['search'] = "Fresh"

	else: 
		session['search_happened'] = False

	# brings in user names for the form
	session['possible_users'] = mysql.fetch("SELECT user_name FROM users ORDER BY user_name")
	# brings in dates that have posts on them
	all_dates = mysql.fetch("SELECT created_at FROM stories")
	dates = []
	for item in all_dates:
		# prevents duplicates
		if not item in dates:
			dates.append(item)
	session['dates'] = dates
	# pulls up dates that have winners
	winners_data = mysql.fetch("SELECT days_have_winners.story_id, stories.created_at FROM days_have_winners LEFT JOIN stories ON stories.id = days_have_winners.story_id ORDER BY days_have_winners.story_id desc")
	# variable for storing list of dates that have winners
	winners = []
	# stores winner dates in winners array
	for item in winners_data:
		winners.append(item['created_at'])

	session['winner-dates'] = winners

	return render_template('/search.html')

# Runs user's queries for vents on Search page
@app.route('/search_params', methods = ['POST'])
def search_params():
	date = request.form['date'] + " 00:00:00"
	keyword = "%" + request.form['keyword'] + "%"
	user = request.form['user']

	# runs the search if there is enough data to run it
	# keyword, no user or date
	if len(keyword) > 2 and len(user) == 0 and len(date) == 9:
		session['search'] = mysql.fetch("SELECT stories.story, stories.thumbs_up, stories.id, stories.thumbs_down, users.user_name, stories.created_at FROM stories LEFT JOIN users ON stories.user_id = users.id WHERE stories.story LIKE '{}' ORDER BY stories.updated_at desc".format(keyword))
	# no user, date or keyword
	elif len(keyword) == 2 and len(user) == 0 and len(date) == 9:
		session['search'] = "Please enter a search parameter."
	# user, no date, optional keyword
	elif len(date) == 9 and len(user) > 0:
		session['search'] = mysql.fetch("SELECT stories.story, stories.thumbs_up, stories.id, stories.thumbs_down, users.user_name, stories.created_at FROM stories LEFT JOIN users ON stories.user_id = users.id WHERE stories.story LIKE '{}' AND users.user_name = '{}' ORDER BY stories.updated_at desc".format(keyword, user))
	# date, no user, optional keyword
	elif len(date) > 9 and len(user) == 0: 
		session['search'] = mysql.fetch("SELECT stories.story, stories.thumbs_up, stories.id, stories.thumbs_down, users.user_name, stories.created_at FROM stories LEFT JOIN users ON stories.user_id = users.id WHERE stories.story LIKE '{}' AND stories.created_at = '{}' ORDER BY stories.updated_at desc".format(keyword, date))
	# date, user, optional keyword
	else: 
		session['search'] = mysql.fetch("SELECT stories.story, stories.thumbs_up, stories.id, stories.thumbs_down, users.user_name, stories.created_at FROM stories LEFT JOIN users ON stories.user_id = users.id WHERE stories.story LIKE '{}' AND users.user_name = '{}' AND stories.created_at = '{}' ORDER BY stories.updated_at desc".format(keyword, user, date))

	# checks for an empty query result, adds an error message
	if len(session['search']) == 0:
		session['search'] = "fail"

	# helps page tell difference between a refresh and a new search
	session['search_happened'] = True

	return redirect('/search')

# pulls up the desired Winner
@app.route('/search_winners', methods = ["POST"])
def search_winners():
	# stores the requested date
	date = request.form['date']
	session['search'] = mysql.fetch("SELECT stories.updated_at, stories.story, stories.thumbs_up, users.user_name, days_have_winners.story_id, days_have_winners.user_id, stories.thumbs_down, stories.created_at FROM stories LEFT JOIN users ON stories.user_id = users.id LEFT JOIN days_have_winners ON stories.user_id = days_have_winners.user_id WHERE stories.created_at = '{}' AND days_have_winners.story_id = stories.id ORDER BY stories.updated_at".format(date))
	# helps page tell difference between a refresh and a new search
	session['search_happened'] = True
	return redirect('/search')
	
app.run(debug = True)