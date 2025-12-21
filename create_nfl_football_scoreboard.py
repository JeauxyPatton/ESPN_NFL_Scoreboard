import numpy as np
import requests
import json
import pytz
from datetime import datetime, timedelta, timezone
import calendar
import tkinter as tk
from PIL import ImageTk, Image


def get_first_sunday_of_month(year, month):
    """
    Returns the datetime object for the first Sunday of a given month and year.

    Args:
        year (int): The year (e.g., 2025).
        month (int): The month (1-12).

    Returns:
        datetime.date: A datetime.date object representing the first Sunday,
                      or None if an invalid year/month is provided.
    """
    try:
        # Get the weekday of the first day of the month (Monday is 0, Sunday is 6)
        # and the number of days in the month
        first_day_weekday, num_days = calendar.monthrange(year, month)

        # Calculate how many days from the 1st of the month to reach the first Sunday
        # If the 1st is Sunday (6), then the first Sunday is the 1st.
        # Otherwise, calculate the offset.
        days_until_first_sunday = (6 - first_day_weekday + 7) % 7

        # The day of the month for the first Sunday
        first_sunday_day = 1 + days_until_first_sunday

        # Create the datetime object for the first Sunday
        first_sunday_datetime = datetime(year, month, first_sunday_day,6,0,0,tzinfo=timezone.utc)
        return first_sunday_datetime

    except ValueError:
        return None  # Handle invalid year or month input

def parse_nested_dict(d):
	for key, value in d.items():
		if isinstance(value, dict):
			print(f"Entering nested dict for key: {key}")
			parse_nested_dict(value)
			print(f"Exiting nested dict for key: {key}")
		else:
			print(f"Key: {key}, Value: {value}")

def count_weeks_between_dates(start_date, end_date):
	time_difference = end_date - start_date
	total_days = time_difference.days
	number_of_weeks = total_days // 7
	return number_of_weeks

def convert_utc_to_et(utc_time):
	et = pytz.timezone('US/Eastern')
	et_time = utc_time.astimezone(et)
	return et_time

def on_frame_configure(event):
	canvas.configure(scrollregion=canvas.bbox("all"))

def on_mouse_wheel(event):
	if event.delta > 0 or event.num == 4:
		canvas.yview_scroll(-1, "units")
	else:
		canvas.yview_scroll(1, "units")

def get_wind_direction_text(wind_direction):
	if wind_direction != None:
		if wind_direction < 25:
			wind_dir = 'N'
		elif wind_direction < 65:
			wind_dir = 'NE'
		elif wind_direction < 115:
			wind_dir = 'E'
		elif wind_direction < 155:
			wind_dir = 'SE'
		elif wind_direction < 200:
			wind_dir = 'S'
		elif wind_direction < 245:
			wind_dir = 'SW'
		elif wind_direction < 295:
			wind_dir = 'W'
		elif wind_direction < 340:
			wind_dir = 'NW'
		elif wind_direction < 361:
			wind_dir = 'N'
	else:
		wind_dir = 'U'
	return wind_dir

def games_date_sort_key(game):
	return game.start_date

def games_alpha_sort_key(game):
	return game.home_team.name

def games_qtr_sort_key(game):
	game_info = game["competitions"][0]
	status_info = game_info["status"]
	qtr = status_info["period"]
	if qtr == None:
		qtr = 2
	elif 'OT' in str(qtr):
		qtr = 5
	return qtr

def games_minsleft_sort_key(game):
	game_info = game["competitions"][0]
	status_info = game_info["status"]
	clock = status_info["displayClock"]
	#print(clock)
	game_time_str = clock
	game_min_time_str, game_sec_time_str = game_time_str.split(":")
	game_time_int = int(game_min_time_str + game_sec_time_str)
	return game_time_int

def sort_live_games(scoreboard_games):
	scoreboard_games.sort(key=games_qtr_sort_key, reverse=True)
	qtr_games_list = []
	for game in scoreboard_games:
		game_info = game["competitions"][0]
		status_info = game_info["status"]
		game_qtr = status_info["period"]
		if game_qtr not in qtr_games_list:
			qtr_games_list.append(game_qtr)

	scoreboard_games_sorted = []
	for qtr in qtr_games_list:
		games_in_each_qtr = []
		for game in scoreboard_games:
			game_info = game["competitions"][0]
			status_info = game_info["status"]
			game_qtr = status_info["period"]
			if qtr == game_qtr:
				games_in_each_qtr.append(game)
		games_in_each_qtr.sort(key=games_minsleft_sort_key)
		for game_sorted_by_qtr in games_in_each_qtr:
			scoreboard_games_sorted.append(game_sorted_by_qtr)
	return scoreboard_games_sorted

def make_weather(weather, is_it_night):
	condition = weather["displayValue"]
	numbers_count = 0
	for char in condition:
		if char.isdigit():
			numbers_count += 1
	if numbers_count > 0:
		condition = weather["conditionId"]
		numbers_count2 = 0
		for char in condition:
			if char.isdigit():
				numbers_count2 += 1
		if numbers_count2 > 0:
			condition = 'Unknown'

	weather_desc = condition
	if weather_desc in ['Fair', 'Mostly clear', 'Mostly Clear', 'Mostly Sunny',
		'Mostly sunny', 'Fog', 'Foggy']:
		if is_it_night == False:
			weather_icon_path = weather_icon_dir + 'fair.png'
		else: 
			weather_icon_path = weather_icon_dir + 'fair_night.png'
	elif weather_desc == 'Clear' or weather_desc == 'Sunny':
		if is_it_night == False:
			weather_icon_path = weather_icon_dir + 'sunny.png'
		else:
			weather_icon_path = weather_icon_dir + 'clear_night.png'
	elif weather_desc in ['Cloudy', 'Partly Cloudy', 'Partly cloudy', 'Mostly cloudy',
		'Mostly Cloudy', 'Intermittent clouds', 'Intermittent Clouds', 'Clouds', 'Cloud']:
		if is_it_night == False:
			weather_icon_path = weather_icon_dir + 'cloudy_day.png'
		else: 
			weather_icon_path = weather_icon_dir + 'cloudy_night.png'
	elif weather_desc in ['Light Rain', 'Light rain', 'Drizzle', 'Light Rain Shower', 'Light Rain Showers',
		'Light rain shower', 'Light rain showers']:
		if is_it_night == False:
			weather_icon_path = weather_icon_dir + 'light_rain.png'
		else: 
			weather_icon_path = weather_icon_dir + 'light_rain_night.png'
	elif weather_desc == 'Overcast':
		weather_icon_path = weather_icon_dir + 'overcast.png'
	elif weather_desc in ['Rain', 'Rain Shower', 'Rain Showers', 'Showers', 'Rain shower', 'Rain showers']:
		weather_icon_path = weather_icon_dir + 'rainy.png'
	elif weather_desc in ['Heavy Rain Shower', 'Heavy Rain', 'Heavy rain', 'Heavy rain shower',
		'Heavy rain showers', 'Heavy Rain Showers']:
		weather_icon_path = weather_icon_dir + 'heavy_rain.png'
	elif weather_desc in ['Thunderstorm', 'Thunderstorms', 'Storms', 'Stormy', 'Thunder storms', 
		'Thunder storm', 'Thunder Storm', 'Thunder Storms']:
		weather_icon_path = weather_icon_dir + 'thunderstorm.png'
		weather_desc = 'Thunderstorms'
	elif weather_desc == 'Unknown':
		weather_icon_path = weather_icon_dir + 'missing_V2.png'
	else:
		if is_it_night == False:
			weather_icon_path = weather_icon_dir + 'sunny.png'
		else: 
			weather_icon_path = weather_icon_dir + 'clear_night.png'

	return weather_desc, weather_icon_path


def refresh_canvas(canvas):
	update_scoreboard(canvas)
	canvas.after(60000, refresh_canvas, canvas)

def update_scoreboard(canvas):
	current_datetime = datetime.now(timezone.utc)
	if current_datetime > datetime_fall_timechange and current_datetime <= datetime(current_datetime.year+1,3,1,0,0,0,tzinfo=timezone.utc):
		ET_offset = 5
	else:
		ET_offset = 4
	current_datetime_str = (current_datetime - timedelta(hours=ET_offset)).strftime("%A %B %-d, %Y at %-I:%M:%S %p ET")

	print("The current time is " + current_datetime_str)
	first_game_of_season = datetime(2025, 9, 3, 0, 0, 0, tzinfo=timezone.utc)
	now_date = datetime.now(timezone.utc)
	nfl_week = count_weeks_between_dates(first_game_of_season, now_date) + 1
	year = now_date.year
	url = "https://cdn.espn.com/core/nfl/schedule?xhr=1&year=" + str(year) + "&week=" + str(nfl_week)

	try:
		response = requests.get(url)
		response.raise_for_status()
		#print(response.text)
	except requests.exceptions.RequestException as e:
		print("Error making request: " + str(e))

	json_data = response.json()
	schedule = json_data["content"]["schedule"]

	# # #save temporary json file
	output_file_path = '/mnt/c/Users/bjig2/Documents/Football/test_nfl_data_V2.json'
	try:
		with open(output_file_path, 'w') as f:
			json.dump(json_data, f, indent=4)
		print(f"Data successfully saved to {output_file_path}")
	except IOError as e:
		print(f"Error writing to file: {e}")


	with open(output_file_path, 'r') as data_file:
		json_data = json.load(data_file)
	
	schedule = json_data["content"]["schedule"]

	completed_games = []
	upcoming_games = []
	current_scoreboard = []

	for game_date in schedule:
		game_day = datetime.strptime(game_date, "%Y%m%d")
		games = schedule[game_date]["games"]
		for game in games:
			kickoff_time = game["date"]
			kickoff_time_obj = datetime.strptime(kickoff_time, "%Y-%m-%dT%H:%MZ")
			kickoff_time_obj = kickoff_time_obj.replace(tzinfo=timezone.utc)
			game_info = game["competitions"][0]
			status_info = game_info["status"]
			game_status = status_info["type"]["description"]
			if kickoff_time_obj > current_datetime:
				upcoming_games.append(game)
			else:
				if game_status == "Final":
					completed_games.append(game)
				else:
					current_scoreboard.append(game)

	if schedule == []:
		print("No games were found.")
		pass
	else:
		print("Clearing the canvas.")
		canvas.delete("all")
		content_frame = tk.Frame(canvas, bg=standard_bg_color)
		canvas.create_window((0,0), window=content_frame, anchor=tk.NW)
		content_frame.bind("<Configure>", on_frame_configure)
		canvas.bind_all("<MouseWheel>", on_mouse_wheel)
		canvas.bind_all("<Button-4>", on_mouse_wheel)
		canvas.bind_all("<Button-5>", on_mouse_wheel)
		content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		#print("Adding date label")
		label_date = tk.Label(content_frame, text= current_datetime_str,
			font=(universal_font, 16, "bold"), bg=standard_bg_color, fg=universal_font_color,
			anchor='w')
		label_date.pack(fill=tk.X, pady=10, padx=100)
		if current_scoreboard != []:
			football_image = Image.open(football_dir)
			football = ImageTk.PhotoImage(football_image.resize((26, 26), Image.LANCZOS))
			label_inprog = tk.Label(content_frame, text = " Games in progress:", font=(universal_font, 16, "bold"),
				anchor='w', bg=standard_bg_color, fg=universal_font_color)
			label_inprog.pack(fill=tk.X)

			current_scoreboard_sorted = sort_live_games(current_scoreboard)

			for game in current_scoreboard_sorted:
				game_info = game["competitions"][0]
				kickoff_time = game["date"]
				kickoff_time_obj = datetime.strptime(kickoff_time, "%Y-%m-%dT%H:%M%z")
				status_info = game_info["status"]
				game_qtr = status_info["period"]
				home_team_info = game_info["competitors"][0]
				home_score = home_team_info["score"]
				home_team_name_short = home_team_info["team"]["displayName"]
				home_team_id = home_team_info["id"]

				away_team_info = game_info["competitors"][1]
				away_score = away_team_info["score"]
				away_team_name_short = away_team_info["team"]["displayName"]
				away_team_id = away_team_info["id"]

				game_info = game["competitions"][0]
				tv_channel = game_info["broadcast"]
				status_info = game_info["status"]
				qtr = status_info["period"]
				clock = status_info["displayClock"]
				clock_text_line = "Q" + str(qtr) + " " + clock
				if qtr == 5:
					clock_text_line = "OT" + " " + clock
				score_text_line = away_team_name_short + " " + str(away_score) + \
					" - " + str(home_score) + " " + home_team_name_short
				
				venue_info = game_info["venue"]
				game_state = venue_info["address"]["state"]
				if game_state in alaska_tz_states:
					local_offset = -10
				elif game_state in hawaii_tz_states:
					local_offset = -11
				elif game_state in pacific_tz_states:
					local_offset = -8
				elif game_state in mountain_tz_states:
					local_offset = -7
				elif game_state in central_tz_states:
					local_offset = -6
				elif game_state in eastern_tz_states:
					local_offset = -5
				#print("The local time offset is: " + str(local_offset))

				#kickoff_time_obj = kickoff_time_obj(tzinfo=timezone.utc)
				start_datetime = kickoff_time_obj
				if kickoff_time_obj > datetime_fall_timechange and kickoff_time_obj <= datetime(current_datetime.year+1,3,1,0,0,0,tzinfo=timezone.utc):
						ET_offset = -5
				else:
					ET_offset = -4
					local_offset += 1
				adjusted_start_datetime = start_datetime + timedelta(hours=ET_offset)
				adjusted_local_starttime = start_datetime + timedelta(hours=local_offset)

				utc_sundown_time = datetime(start_datetime.year, start_datetime.month, start_datetime.day,
					21, 0, 0, tzinfo=timezone.utc)
				if start_datetime.hour < 14:
					utc_sundown_time = utc_sundown_time - timedelta(hours=24)
				local_sundown_time = utc_sundown_time + timedelta(hours=(abs(local_offset)-5))

				if start_datetime >= local_sundown_time:
					is_it_night = True
				else:
					is_it_night = False
				char_limit = 50

				if game_status != "Final":
					if "situation" in game_info:
						situation = game_info["situation"]
						if "possession" in situation:
							team_in_possession = situation["possession"]
							if team_in_possession == home_team_id:
								possession = 'home'
							elif team_in_possession == away_team_id:
								possession = 'away'
						else:
							possession = 'none'
						if "downDistanceText" in situation:
							down_and_distance = situation["downDistanceText"]
						else:
							down_and_distance = ''
						if "lastPlay" in situation:
							last_play = situation["lastPlay"]
							last_play_text = last_play["text"]
							if len(last_play_text) > char_limit:
								new_last_play = ""
								is_break_needed = False
								for i, letter in enumerate(last_play_text):
									if i % char_limit == 0 and new_last_play != "":
										if letter == " ":
											new_last_play += "\n		          "
											is_break_needed = False
										else:
											is_break_needed = True
									elif is_break_needed == True and letter == " ":
										new_last_play += "\n		           "
										is_break_needed = False
									new_last_play +=letter

							else:
								new_last_play = last_play_text
						else:
							last_play_text = " Missing"
					else:
						situation = None
						possession = 'none'
					home_team_points = home_team_info["score"]
					home_team_record = home_team_info["records"][0]["summary"]
					away_team_points = away_team_info["score"]
					away_team_record = away_team_info["records"][0]["summary"]

					venue_name = venue_info["fullName"]
					indoor_var = venue_info["indoor"]
					if indoor_var == True:
						indoor_text = " (Indoors)"
						add_weather = False
					else:
						indoor_text = ""
						if "weather" in game:
							add_weather = True
						else:
							add_weather = False

					if add_weather == True:
						weather = game["weather"]
						if "temperature" in weather:
							weather_temp = weather["temperature"]
						else:
							weather_temp = 'Missing'

						weather_desc, weather_icon_path = make_weather(weather, is_it_night)

						weather_icon = Image.open(weather_icon_path)
						weather_img = ImageTk.PhotoImage(weather_icon.resize((26, 26), Image.LANCZOS))
						if weather_desc == 'Unknown':
							label_weather = tk.Label(content_frame, text= '		Weather Missing', anchor = 'nw',
								font=(universal_font, 12), bg=standard_bg_color, fg=universal_font_color, image = weather_img, compound=tk.RIGHT)
						else:
							label_weather = tk.Label(content_frame, text= '		' + str(weather_temp) + '°F, ' + weather_desc 
								+ ' ', anchor = 'nw', 
								font=(universal_font, 12), bg=standard_bg_color, fg=universal_font_color, image = weather_img, compound=tk.RIGHT)
						label_weather.image = weather_img
					
					current_total_pts = away_team_points + home_team_points

					char_limit = 50
					away_team_name_length = len(away_team_name_short)
					home_team_name_length = len(home_team_name_short)
					num_away_spaces = char_limit - (away_team_name_length + 5)
					num_home_spaces = char_limit - (home_team_name_length + 0)

					if possession == 'away':
						#num_away_spaces += -15
						label_awayteam = tk.Label(content_frame, text = "    " + away_team_name_short + 
							" (" + away_team_record + ") " +num_away_spaces*" " + str(away_team_points) + 
							"	(" + tv_channel + ")", bg=standard_bg_color, fg=universal_font_color, 
							anchor='nw', image = football, font=(universal_font, 14, "bold"),
							compound=tk.LEFT)
						label_awayteam.pack(fill=tk.X)
						label_awayteam.image = football
					else:
						if possession != 'home':
							num_away_spaces += -3
						num_away_spaces += 2
						label_awayteam = tk.Label(content_frame, text = "         " +
							away_team_name_short + " (" + away_team_record + ") " + num_away_spaces*" " +
							str(away_team_points) + "	(" + tv_channel + ")", 
							anchor='nw', font=(universal_font, 14, "bold"), bg=standard_bg_color, 
							fg=universal_font_color)
						label_awayteam.pack(fill=tk.X)
					if possession == 'home':
						label_hometeam = tk.Label(content_frame, text = "  @ " +
							home_team_name_short + " (" + home_team_record + ") " + num_home_spaces*" " +
							str(home_team_points), bg=standard_bg_color, anchor='nw', 
							fg=universal_font_color, image = football, font=(universal_font, 14, "bold"), 
							compound=tk.LEFT)
						label_hometeam.pack(fill=tk.X)
						label_hometeam.image = football
					else:
						label_hometeam = tk.Label(content_frame, text = "    @ " +
							home_team_name_short + " (" + home_team_record + ") " + num_home_spaces*" " + 
							str(home_team_points), bg=standard_bg_color, fg=universal_font_color,
							anchor='nw', font=(universal_font, 14, "bold"))
						label_hometeam.pack(fill=tk.X)
					if situation != None:
						if '& Goal' in down_and_distance:
							label_qtr = tk.Label(content_frame, text = '	' + clock_text_line +', ' + down_and_distance,
								anchor='w', bg=standard_bg_color, fg='red', font=(universal_font, 14, 'bold'))
						else:
							label_qtr = tk.Label(content_frame, text = '	' + clock_text_line + ', ' + down_and_distance,
								anchor='w', bg=standard_bg_color, fg=universal_font_color, font=(universal_font, 14))
							label_qtr.pack(fill=tk.X)
							label_lastplay = tk.Label(content_frame, text = '		Last play: ' + new_last_play, anchor='nw', 
								bg=standard_bg_color, fg=universal_font_color, font=(universal_font, 12))
							label_lastplay.pack(fill=tk.X)
					else:
						label_qtr = tk.Label(content_frame, text = '	' + clock_text_line,
							anchor='w', bg=standard_bg_color, fg=universal_font_color, font=(universal_font, 14))
						label_qtr.pack(fill=tk.X)

					label_venue = tk.Label(content_frame, text = '		' + venue_name + indoor_text, anchor='nw', 
						bg=standard_bg_color, fg=universal_font_color, font=(universal_font, 12))
					label_venue.pack(fill=tk.X)
					if add_weather == True:
						label_weather.pack(fill=tk.X)
				else:
					completed_games.append(game)
					#print("   " + score_text_line + "\n")
		
		else:
			label_inprog = tk.Label(content_frame, text = "There are no games currently in progress", font=(universal_font, 16, "bold"),
				anchor='w', bg=standard_bg_color, fg=universal_font_color)
			label_inprog.pack(fill=tk.X)
		if completed_games != []:
			label_line = tk.Label(content_frame, text="______________________________________________________" +
				"______________________________________________", bg=standard_bg_color, anchor='nw',
				font=(universal_font, 14), fg=universal_font_color)
			label_line.pack(fill=tk.X)
			label_final_str = tk.Label(content_frame, text=" Final scores:", font=(universal_font, 16, "bold"), 
				anchor = 'w', bg=standard_bg_color, fg=universal_font_color)
			label_final_str.pack(fill=tk.X)
			for game in completed_games:
				game_info = game["competitions"][0]
				home_team_info = game_info["competitors"][0]
				#parse_nested_dict(home_team_info)
				home_score = home_team_info["score"]
				home_team_name = home_team_info["team"]["displayName"]
				away_team_info = game_info["competitors"][1]
				#parse_nested_dict(away_team_info)
				away_score = away_team_info["score"]
				away_team_name = away_team_info["team"]["displayName"]
				final_score_text_line = "	" + away_team_name + " " + str(away_score) + \
						" @ " + str(home_score) + " " + home_team_name
				label_game_finalscore = tk.Label(content_frame, text = final_score_text_line, 
					font=(universal_font, 14, "bold") ,anchor='w', bg=standard_bg_color, fg=universal_font_color)
				label_game_finalscore.pack(fill=tk.X)

		if upcoming_games != []:
			label_line = tk.Label(content_frame, text="______________________________________________________" +
				"______________________________________________", bg=standard_bg_color, anchor='nw',
				font=(universal_font, 14), fg=universal_font_color)
			label_line.pack(fill=tk.X)
			label_upcoming_str = tk.Label(content_frame, text=" Upcoming games:", font=(universal_font, 16, "bold"), 
				anchor = 'w', bg=standard_bg_color, fg=universal_font_color)
			label_upcoming_str.pack(fill=tk.X)
			for game in upcoming_games:
				game_info = game["competitions"][0]
				kickoff_time = game["date"]
				kickoff_time_obj = datetime.strptime(kickoff_time, "%Y-%m-%dT%H:%M%z")
				#kickoff_time_obj_et = convert_utc_to_et(kickoff_time_obj)
				kickoff_time_obj_et = kickoff_time_obj - timedelta(hours=5)
				kickoff_time_et_str = kickoff_time_obj_et.strftime("%H:%M")

				tv_channel = game_info["broadcast"]
				venue_info = game_info["venue"]
				if "odds" in game_info:
					add_betting_info = True
					betting_info = game_info["odds"][0]

					if "moneyline" in betting_info:
						home_ML = betting_info["moneyline"]["home"]["close"]["odds"]
					else:
						home_ML = None
					if "overUnder" in betting_info:
						over_under = str(betting_info["overUnder"])
					else:
						over_under = None
					if "details" in betting_info:
						point_spread = betting_info["details"]

					if home_ML != None:
						betting_line = '[' + home_ML + ']'
					else:
						betting_line = '' 
				else:
					add_betting_info = False
				
				venue_name = venue_info["fullName"]
				indoor_var = venue_info["indoor"]
				if indoor_var == True:
					indoor_text = " (Indoors)"
					add_weather = False
				else:
					indoor_text = ""
					if "weather" in game:
						add_weather = True
					else:
						add_weather = False

				home_team_info = game_info["competitors"][0]
				home_team_name_short = home_team_info["team"]["displayName"]
				home_team_id = home_team_info["id"]

				away_team_info = game_info["competitors"][1]
				away_team_name_short = away_team_info["team"]["displayName"]
				away_team_id = away_team_info["id"]
				
				game_state = venue_info["address"]["state"]
				if game_state in alaska_tz_states:
					local_offset = -10
				elif game_state in hawaii_tz_states:
					local_offset = -11
				elif game_state in pacific_tz_states:
					local_offset = -8
				elif game_state in mountain_tz_states:
					local_offset = -7
				elif game_state in central_tz_states:
					local_offset = -6
				elif game_state in eastern_tz_states:
					local_offset = -5

				start_datetime = kickoff_time_obj
				if kickoff_time_obj > datetime_fall_timechange and kickoff_time_obj <= datetime(current_datetime.year+1,3,1,0,0,0,tzinfo=timezone.utc):
						ET_offset = -5
				else:
					ET_offset = -4
					local_offset += 1
				adjusted_start_datetime = start_datetime + timedelta(hours=ET_offset)
				adjusted_local_starttime = start_datetime + timedelta(hours=local_offset)

				utc_sundown_time = datetime(start_datetime.year, start_datetime.month, start_datetime.day,
					21, 0, 0, tzinfo=timezone.utc)
				if start_datetime.hour < 14:
					utc_sundown_time = utc_sundown_time - timedelta(hours=24)
				local_sundown_time = utc_sundown_time + timedelta(hours=(abs(local_offset)-5))

				if start_datetime >= local_sundown_time:
					is_it_night = True
				else:
					is_it_night = False

				current_datetime_ET = current_datetime + timedelta(hours=ET_offset)
				if adjusted_start_datetime.day == current_datetime_ET.day:
					adjusted_start_datetime_text = adjusted_start_datetime.strftime("%-I:%M %p ET")
				else:
					adjusted_start_datetime_text = adjusted_start_datetime.strftime("%a. %b. %-d - %-I:%M %p ET")
				
				if add_betting_info == True:
					label_game_teams = tk.Label(content_frame, text = " " + away_team_name_short + 
						"  @  " + home_team_name_short + " " + betting_line + " - " + 
						adjusted_start_datetime_text, anchor='w', fg=universal_font_color, font=(universal_font, 14), bg=standard_bg_color)						
				else:
					label_game_teams = tk.Label(content_frame, text = " " + away_team_name_short + 
							"  @  " + home_team_name_short + " - " + adjusted_start_datetime_text, 
							anchor='w', fg=universal_font_color, font=(universal_font, 14), bg=standard_bg_color)
				label_game_teams.pack(fill=tk.X)
				
				tv_image = Image.open(tv_dir)
				tv = ImageTk.PhotoImage(tv_image.resize((26, 26), Image.LANCZOS))
				
				if tv_channel != None:
					label_channel = tk.Label(content_frame, text= ': ' + tv_channel, anchor = 'w', 
						image = tv, compound=tk.LEFT, font=(universal_font, 13), bg=standard_bg_color, 
						fg=universal_font_color)
					label_channel.image = tv
					label_channel.pack(fill=tk.X, padx=30)
				
				if add_betting_info == True:
					label_betting_info_line = tk.Label(content_frame, text= '		' + point_spread + ', O/U: ' +
						over_under, anchor = 'w', fg=universal_font_color, 
						font=(universal_font, 12), bg=standard_bg_color)
					label_betting_info_line.pack(fill=tk.X)

				label_venue_name = tk.Label(content_frame, text= '		' + venue_name, 
					anchor = 'w', fg=universal_font_color, font=(universal_font, 12), bg=standard_bg_color)
				label_venue_name.pack(fill=tk.X)

				if add_weather == True:
					weather = game["weather"]
					if "temperature" in weather:
						weather_temp = weather["temperature"]
					else:
						weather_temp = 'Missing'
					weather_desc, weather_icon_path = make_weather(weather, is_it_night)
					weather_icon = Image.open(weather_icon_path)
					weather_img = ImageTk.PhotoImage(weather_icon.resize((26, 26), Image.LANCZOS))
					if weather_desc == 'Unknown':
						label_weather = tk.Label(content_frame, text= '		Weather Missing', anchor = 'nw',
							font=(universal_font, 12), bg=standard_bg_color, fg=universal_font_color, image = weather_img, compound=tk.RIGHT)
					else:
						label_weather = tk.Label(content_frame, text= '		' + str(weather_temp) + '°F, ' + weather_desc 
							+ ' ', anchor = 'nw', 
							font=(universal_font, 12), bg=standard_bg_color, fg=universal_font_color, image = weather_img, compound=tk.RIGHT)
					label_weather.image = weather_img
				else:
					dome_icon = Image.open(dome_icon_path)
					dome_img = ImageTk.PhotoImage(dome_icon.resize((26, 26), Image.LANCZOS))
					label_weather = tk.Label(content_frame, text= '		Indoors ', anchor = 'w',
						font=(universal_font, 12), fg=universal_font_color, bg=standard_bg_color, image = dome_img, compound=tk.RIGHT)
					label_weather.image = dome_img
				
				label_weather.pack(fill=tk.X)


alaska_tz_states = ['AK']
hawaii_tz_states = ['HI']
pacific_tz_states = ['WA','OR','CA','NV']
mountain_tz_states = ['MT','ID','UT','WY','CO','NM']
central_tz_states = ['ND','SD','NE','KS','OK','TX','MN','IA','MO','AR','LA','WI','IL','TN','MS','AL'] 
eastern_tz_states = ['MI','IN','KY','GA','FL','ME','VT','NH','MA','RI','CT','NY','OH','WV','PA',
	'NJ','DE','MD','DC','VA','NC','SC']

base_dir = '/mnt/c/Users/bjig2/Documents/Football/'
access_token_tier2 = 'px4V/SPCN5bNopg47ayPEj53vCiKC9h7h4qozyav3++VyiyV+PDdlGF8P3BS7x5p'
#gather weather icons for weather types

#gather team logos, compound into team names

current_datetime = datetime.now(timezone.utc)
datetime_yesterday = current_datetime - timedelta(hours=24)
datetime_tomorrow = current_datetime + timedelta(hours=24)
datetime_twodays = current_datetime + timedelta(hours=48)
datetime_threedays = current_datetime + timedelta(hours=72)
datetime_fourdays = current_datetime + timedelta(hours=96)

datetime_fall_timechange = get_first_sunday_of_month(current_datetime.year, 11)
universal_font = 'Lucida Console'
standard_bg_color = 'black'
universal_font_color = 'white'
football_dir = base_dir + 'football_V3.png'
tv_dir = base_dir + 'tv_V2.png'
weather_icon_dir = base_dir + 'Weather_Icons/'
dome_icon_path = weather_icon_dir + 'dome.png'

#Create the application window
print('Creating application window.')
rootapp = tk.Tk()
rootapp.title('NFL Scoreboard')
rootapp.geometry("950x1000")
rootapp.configure(bg=standard_bg_color)
rootapp.overrideredirect(False)
scrollbar = tk.Scrollbar(rootapp, orient='vertical')
scrollbar.pack(side='right', fill='y')
canvas = tk.Canvas(rootapp, bg=standard_bg_color, yscrollcommand=scrollbar.set)

scrollbar.config(command=canvas.yview)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#Start the refresh cycle
refresh_canvas(canvas)

rootapp.mainloop()
