import csv
import uuid
import mysql.connector
from time import perf_counter
import sys
import os

if len(sys.argv) < 2:
  print('Enter Folder Name')
  sys.exit()
  
start_time = perf_counter()
id = uuid.uuid4()
total_count = 0

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="mydatabase" 
)

files_directory = './' + sys.argv[1]
file_names = os.listdir(files_directory)

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS games (id VARCHAR(36), name VARCHAR(255), create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS programs (id VARCHAR(36), name VARCHAR(255), game_id VARCHAR(36), year YEAR, create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (game_id) REFERENCES games(id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS sets (id VARCHAR(36), name VARCHAR(255), program_id VARCHAR(36), numbered VARCHAR(16), create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (program_id) REFERENCES programs(id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS teams (id VARCHAR(36), name VARCHAR(255), game_id VARCHAR(36), create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (game_id) REFERENCES games(id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS players (id VARCHAR(36), name VARCHAR(255), team_id VARCHAR(36), create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (team_id) REFERENCES teams(id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS cards (id VARCHAR(36), player_id VARCHAR(36), set_id VARCHAR(36), card_number VARCHAR(5), search_string VARCHAR(300),create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (player_id) REFERENCES players(id), FOREIGN KEY (set_id) REFERENCES sets(id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS link_players_to_card (id VARCHAR(36), player_id VARCHAR(36), card_id VARCHAR(36), create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (player_id) REFERENCES players(id), FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE)")
mycursor.execute("CREATE TABLE IF NOT EXISTS link_teams_to_player (id VARCHAR(36), team_id VARCHAR(36), player_id VARCHAR(36), create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (id), FOREIGN KEY (team_id) REFERENCES teams(id), FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE)")
mydb.commit()


sets = []

for x, file_name in enumerate(file_names):
  file_start_time = perf_counter()
  cards = []
  current_directory = files_directory + '/' + file_name
  with open(current_directory, 'r', encoding='utf8') as file:
    csvreader = csv.DictReader(file)
    for row in csvreader:

      if row['CARD SET'].strip() not in sets:
        sets.append(row['CARD SET'].strip())

      if {
        'game':row['SPORT'].strip(), 
        'year':row['YEAR'], 
        'program':row['PROGRAM'].strip(), 
        'set':row['CARD SET'].strip(), 
        'player':row['ATHLETE'].strip(), 
        'team':row['TEAM'].strip(), 
        'card_number':row['CARD NUMBER'].strip(), 
        'numbered':row['SEQUENCE'].strip()} not in cards:

        # if entry is "Alex Bowman","NIKKO RC / TOY STATE | Tommy Baldwin Racing | Chevrolet", happens in panini racing
        adjusted_team = row['TEAM']

        if '/' not in row['ATHLETE'] and '/' in row['TEAM']:
          adjusted_team = adjusted_team.replace('/', '|')

        if (len(adjusted_team.split('/')) != len(row['ATHLETE'].split('/'))):
          print('Error Found at:',row['ATHLETE'], '  -  ', adjusted_team)
          sys.exit()

        cards.append({
          'game':row['SPORT'].strip(), 
          'year':row['YEAR'], 
          'program':row['PROGRAM'].strip(), 
          'set':row['CARD SET'].strip(), 
          'player':row['ATHLETE'].strip(), 
          'team':adjusted_team.strip(), 
          'card_number':row['CARD NUMBER'].strip(), 
          'numbered':row['SEQUENCE'].strip(),
          })      

  def get_loading_bar (current_count, target_count):
    output = list('[::::::::::::::::::::]')
    loaded_bars = (current_count/target_count)  * 100 / 5
    for i in range(int(loaded_bars)):
      output[i + 1] = '|'
    output = "  " + str(current_count) + "/" + str(target_count) + "".join(output)
    return output   

  def get_data_by_id (id, target_table):
    team_cursor = mydb.cursor()
    team_cursor.execute("SELECT * FROM " + target_table + " WHERE id=%s", (id, ))
    return team_cursor.fetchall()

  def get_data_by_name (name, target_table):
    temp_cursor = mydb.cursor()
    temp_cursor.execute("SELECT * FROM " + target_table + " WHERE name=%s", (name, ))
    return temp_cursor.fetchall()

  def get_team_in_game (team_name, game_name):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM teams WHERE name=%s", (team_name, ))
    found_teams = cursor.fetchall()
    for found_team in found_teams:
      if (found_team[2] == get_data_by_name(game_name, 'games')[0][0]):
        return found_team
    return None

  def get_program_in_game (program_name, game_name, program_year):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM programs WHERE name=%s", (program_name, ))
    found_programs = cursor.fetchall()
    for found_program in found_programs:
      if (found_program[2] == get_data_by_name(game_name, 'games')[0][0] and str(program_year) == str(found_program[3])):
        return found_program
    return None

  def get_player_in_team (player_name, team_name): 
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM players WHERE name=%s", (player_name, ))
    found_players = cursor.fetchall()
    for found_player in found_players:
      if '|' in team_name:
        cursor = mydb.cursor() 
        cursor.execute("SELECT * FROM link_teams_to_player WHERE player_id=%s", (str(found_player[0]), ))
        found_teams_to_player_links = cursor.fetchall()
        count = 0
        for found_teams_to_player_link in found_teams_to_player_links:
          if get_data_by_id(found_teams_to_player_link[1], 'teams')[0][1] in team_name:
            count = count + 1
        if (count == len(team_name.split('|'))):
          return found_player
      else:
  
        if (found_player[2] == get_data_by_name(team_name, 'teams')[0][0]):
          return found_player
    return None

  def get_set_in_program (set_name, program_name, program_game):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM sets WHERE name=%s", (set_name, ))
    found_sets = cursor.fetchall()
    for found_set in found_sets:
      for found_program in get_data_by_name(program_name, 'programs'):
          if found_program[2] == get_data_by_name(program_game, 'games')[0][0] and found_set[2] == found_program[0]:
            return found_set
    return None

  print('Creating Missing Data...', end='\r')
  # games/programs
  for data in cards:
    current_program = data['program']
    current_game = data['game']
    current_year = data['year']
    if not get_data_by_name(current_game, 'games'):
      cursor = mydb.cursor()
      cursor.execute("INSERT INTO games (id, name) VALUES (%s, %s)", (str(uuid.uuid4()), current_game))
      mydb.commit()
    if not get_program_in_game(current_program, current_game, current_year):
      cursor = mydb.cursor()
      cursor.execute("INSERT INTO programs (id, name, year, game_id) VALUES (%s, %s, %s, %s)", (str(uuid.uuid4()), current_program, current_year, get_data_by_name(current_game, 'games')[0][0]))
      mydb.commit()

  # sets
  for data in cards:
    current_program = data['program']
    current_set = data['set']
    current_numbered = data['numbered']
    current_game = data['game']
    confirmed_program = ''
    if not get_set_in_program (current_set, current_program, current_game):
      # in the instace were two sets share the same name from different programs
      found_programs = get_data_by_name(current_program, 'programs')
      for found_program in found_programs:
        if get_data_by_id(found_program[2], 'games')[0][1] == current_game:
          confirmed_program = found_program
      player_cursor = mydb.cursor()
      player_cursor.execute("INSERT INTO sets (id, name, program_id, numbered) VALUES (%s, %s, %s, %s)", (str(uuid.uuid4()), current_set, confirmed_program[0], current_numbered))
      mydb.commit()

  # teams
  for data in cards:
    current_team = data['team']
    current_game = data['game']
    if '/' in current_team:
      team_array = current_team.split('/')
      team_count = len(team_array)
      for i in range(team_count):
        if '|' in team_array[i]:
          split_team = team_array[i].split('|')
          for team in split_team:
            if not get_team_in_game (team.strip(), current_game):
              cursor = mydb.cursor()
              cursor.execute("INSERT INTO teams (id, name, game_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), team.strip(), get_data_by_name(current_game, 'games')[0][0]))
              mydb.commit()
        else: 
          if not get_team_in_game (team_array[i], current_game):
            cursor = mydb.cursor()
            cursor.execute("INSERT INTO teams (id, name, game_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), team_array[i].strip(), get_data_by_name(current_game, 'games')[0][0]))
            mydb.commit()
    else:
      if '|' in current_team:
          split_team = current_team.split('|')
          for team in split_team:
            if not get_team_in_game (team.strip(), current_game):
              cursor = mydb.cursor()
              cursor.execute("INSERT INTO teams (id, name, game_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), team.strip(), get_data_by_name(current_game, 'games')[0][0]))
              mydb.commit()
      else: 
        if not get_team_in_game (current_team, current_game):
          cursor = mydb.cursor()
          cursor.execute("INSERT INTO teams (id, name, game_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), current_team.strip(), get_data_by_name(current_game, 'games')[0][0]))
          mydb.commit()

  # players
  for data in cards:
    current_player = data['player']
    current_team = data['team']
    if '/' in current_player:
      player_array = current_player.split('/')
      team_array = current_team.split('/')
      player_count = len(team_array)
      for i in range(player_count):
        if not '|' in team_array[i]:
          if not get_player_in_team(player_array[i].strip(), team_array[i].strip()):
            cursor = mydb.cursor()
            cursor.execute("INSERT INTO players (id, name, team_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), player_array[i].strip(), get_data_by_name(team_array[i].strip(), 'teams')[0][0]))
            mydb.commit()
        else:
          if not get_player_in_team(player_array[i].strip(), team_array[i].strip()):
            team_split = team_array[i].split('|')
            player_id = str(uuid.uuid4())
            cursor = mydb.cursor()
            cursor.execute("INSERT INTO players (id, name, team_id) VALUES (%s, %s, %s)", (player_id, player_array[i], None))
            mydb.commit()
            group_id = str(uuid.uuid4())
            for team in team_split:
              cursor = mydb.cursor()
              cursor.execute("INSERT INTO link_teams_to_player (id, team_id, player_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), get_data_by_name(team.strip(), 'teams')[0][0], player_id.strip()))
              mydb.commit()
    else:
      if '|' in current_team:
        team_split= current_team.split('|')
        if not get_player_in_team(current_player, current_team):
          player_id = str(uuid.uuid4())
          cursor = mydb.cursor()
          cursor.execute("INSERT INTO players (id, name, team_id) VALUES (%s, %s, %s)", (player_id, current_player, None))
          mydb.commit()
          group_id = str(uuid.uuid4())
          for team in team_split:
            cursor = mydb.cursor()
            cursor.execute("INSERT INTO link_teams_to_player (id, team_id, player_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), get_data_by_name(team.strip(), 'teams')[0][0], player_id.strip()))
            mydb.commit()
      else:
        if not get_player_in_team(current_player, current_team):
          cursor = mydb.cursor()
          cursor.execute("INSERT INTO players (id, name, team_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), current_player, get_data_by_name(current_team.strip(), 'teams')[0][0]))
          mydb.commit()

  #cards'



  print(file_name, str(x + 1) + '/' + str(len(file_names)) + '                         ')
  card_count = 0

  for i, current_card in enumerate(cards):
    current_game = current_card['game']
    current_year = current_card['year']
    current_program = current_card['program']
    current_set = current_card['set']
    current_player = current_card['player']
    current_team = current_card['team']
    current_card_number = current_card['card_number']
    current_numbered = current_card['numbered']
    
    lol = ','.join(sets)
    current_search_string = f'{current_player} {current_program} {current_year} {current_set} -({lol})'

    print(get_loading_bar(i, len(cards)), end="\r")

    total_count = total_count + 1
    card_count = card_count + 1


    if '/' in current_player:
      card_id = str(uuid.uuid4())
      cursor = mydb.cursor()
      cursor.execute("INSERT INTO cards (id, player_id, set_id, card_number, search_string) VALUES (%s, %s, %s, %s, %s)", (card_id, None, get_set_in_program(current_set, current_program, current_game)[0], current_card_number,current_search_string))
      mydb.commit()

      player_array = current_player.split('/')
      team_array = current_team.split('/')

      for i, player in enumerate(player_array):
        player_name = player
        team_name = team_array[i]
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO link_players_to_card (id, player_id, card_id, search_string) VALUES (%s, %s, %s, %s)", (str(uuid.uuid4()), get_player_in_team(player_name, team_name)[0], card_id,current_search_string))
        mydb.commit()
    else:
      card_id = str(uuid.uuid4())
      cursor = mydb.cursor()
      cursor.execute("INSERT INTO cards (id, player_id, set_id, card_number, search_string) VALUES (%s, %s, %s, %s, %s)", (card_id, get_player_in_team(current_player, current_team)[0], get_set_in_program(current_set, current_program, current_game)[0], current_card_number,current_search_string))
      mydb.commit()

  x = perf_counter() - start_time
  print(str(card_count) + ' cards completed in ' + str(round(perf_counter() - file_start_time, 2)) + 's                 ')
  print('------------------------------------------------')

print(str(total_count) + ' cards completed in ' + str(round(perf_counter() - start_time, 2)) + 's                 ')

