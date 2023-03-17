import csv
import math
import itertools

player_data_dir = './afl_players_2021.csv'
program_data_dir = './data.txt'
specific_player_data_dir = None #'./brilliance_2022_players.csv'

team_array = [
  'Adelaide Crows',
  'Brisbane Lions',
  'Carlton',
  'Collingwood',
  'Essendon',
  'Fremantle Dockers',
  'Geelong Cats',
  'Giants',
  'Gold Coast Suns',
  'Hawthorn',
  'Melbourne',
  'North Melbourne',
  'Port Adelaide',
  'Richmond',
  'St Kilda',
  'Sydney Swans',
  'West Coast Eagles',
  'Western Bulldogs',
]

team_translate = {
  'Adelaide Crows':'Adelaide Crows',
  'Adelaide':'Adelaide Crows',
  'Brisbane Lions':'Brisbane Lions',
  'Brisbane':'Brisbane Lions',
  'Carlton Blues':'Carlton',
  'Carlton':'Carlton',
  'Collingwood Magpies':'Collingwood',
  'Collingwood':'Collingwood',
  'Essendon Bommers':'Essendon',
  'Essendon':'Essendon',
  'Fremantle Dockers':'Fremantle Dockers',
  'Fremantle':'Fremantle Dockers',
  'Geelong Cats':'Geelong Cats',
  'Geelong':'Geelong Cats',
  'Giants':'Giants',
  'GWS':'Giants',
  'Gold Coast Suns':'Gold Coast Suns',
  'Gold Coast':'Gold Coast Suns',
  'Hawthorn Hawks':'Hawthorn',
  'Hawthorn':'Hawthorn',
  'Melbourne Demons':'Melbourne',
  'Melbourne':'Melbourne',
  'North Melbourne Kangaroos':'North Melbourne',
  'North Melbourne':'North Melbourne',
  'Port Adelaide Power':'Port Adelaide',
  'Port Adelaide':'Port Adelaide',
  'Richmond Tigers':'Richmond',
  'Richmond':'Richmond',
  'St Kilda Saints':'St Kilda',
  'St Kilda':'St Kilda',
  'Sydney Swans':'Sydney Swans',
  'Sydney':'Sydney Swans',
  'West Coast Eagles':'West Coast Eagles',
  'West Coast':'West Coast Eagles',
  'Western Bulldogs':'Western Bulldogs',
}

players_translate = {
  'Jarrad Lyons':'Jarryd Lyons',
  'Nat Fyfe':'Nathan Fyfe',
  'Cam Guthrie':'Cameron Guthrie',
  'Luke Shiels':'Liam Shiels',
  'Bradley Hill':'Brad Hill',
  'Matt Taberner':'Matthew Taberner',
  'Will Powell':'Wil Powell',
  'Alir Alir':'Aliir Aliir',
  'Bradley Close':'Brad Close',
  'Kane Turner':'Kayne Turner',
  'Matthew Owies':'Matt Owies',
  'L Stocker':'Liam Stocker',
  'Lachlan Ash':'Lachie Ash',
  'Trent Cole': 'Tom Cole',
  'M Bontempelli': 'Marcus Bontempelli',
  'S Draper': 'Sam Draper',
  'M Georgiadis': 'Mitch Georgiades'
}


# def get_team_translate (team_name):

specific_player_data = []

if specific_player_data_dir:
  with open(specific_player_data_dir, 'r', encoding='utf8') as file:
    player_data_reader = csv.reader(file)
    for row in player_data_reader:
      specific_player_data.append({'name':row[0],'team':row[1]})

def get_current_team (player_name, player_data):
  for data in player_data:
    if data['name'].strip().lower() == player_name.strip().lower():
      return data['team']
  if specific_player_data:
    for data in specific_player_data:
      if data['name'].strip().lower() == player_name.strip().lower():
        return data['team']
      
  return None

def get_set_length (set_name, program_data):
  count = 0
  flag = False
  for line in program_data:
    if set_name in line:
      flag = True
      continue
    if flag:
      if line[0] != '?':
        count = count + 1
      else:
        return count - 1
  return 0

program_data = []
player_data = []

with open(program_data_dir, 'r', encoding='utf8') as file:
  file_lines = file.readlines()
  for file_line in file_lines:
    temp = file_line.replace('\n', '')
    program_data.append(temp)
    

with open(player_data_dir, 'r', encoding='utf8') as file:
  player_data_reader = csv.reader(file)
  for row in player_data_reader:
    player_data.append({'name':row[0],'team':row[1]})

current_set = ''
current_numbered = ''
current_team = ''
current_program = 'Footy Stars (2022)'
current_sport = 'AFL'
current_brand = 'Select'
current_year = ''
current_code = ''
current_player = ''



output = ["SPORT,YEAR,BRAND,PROGRAM,CARD SET,ATHLETE,TEAM,CARD NUMBER,SEQUENCE\n"]

skip_iter = 0
for i in range(len(program_data)):
  current_player = ''

  if skip_iter > 0:

    skip_iter = skip_iter - 1
    continue

  if i == 0:
    current_year = ''.join(c for c in program_data[i] if not c.isalpha())
    current_program = program_data[i+1].title()

  if current_year in program_data[i]:
    current_set = program_data[i+2]
    for j in itertools.count():
      j = j + 1
      if 'Limited' in program_data[i + j]:
        current_numbered = ''.join(c for c in program_data[i + j] if not c.isalpha())
        skip_iter = j + 1
        break
    continue

  if program_data[i] != '':
    current_code = program_data[i].split()[0]
    current_player = program_data[i].replace(program_data[i].split()[0], '').strip()
    
    if '’' in current_player:
      current_player = current_player.replace('’', "'")

    current_player = current_player.replace('RC', '').strip()
    current_player = current_player.replace('–', '-')
    

    if ',' in current_player:
      temp_team = []
      temp_player = []
      for player in current_player.split(','):
        temp_player.append(player.strip())
        temp_team.append(get_current_team(player, player_data))
      current_player = '/'.join(temp_player)
      current_team = '/'.join(temp_team)
    
    if current_player in team_array or current_player.split('-')[0] in team_array :
      current_team = current_player.split('-')[0]
    elif 'Wild Card' in current_player:
      current_team = team_translate[current_player.replace('Wild Card', '').strip()]
      current_player = 'Wild Card'
    elif 'Header Card' in current_player:
      current_team = 'None'
    elif get_current_team (current_player, player_data) == None:
      if current_player in players_translate:
        if (get_current_team (players_translate[current_player], player_data)) != None:
          current_team = get_current_team (players_translate[current_player], player_data)
          current_player = players_translate[current_player]
      else:
        ## data not accounted for
        print(program_data[i])
    else:
      current_team = get_current_team (current_player, player_data)

  if program_data[i] != '':
    current_set = current_set.replace('–', '-').title().strip()
    output.append(f'{current_sport},{current_year.strip()},{current_brand},{current_program},{current_set},{current_player},{current_team},{current_code},{current_numbered.strip()}\n')

write_file = open("./test.csv","w")
write_file.writelines(output)
write_file.close()