import csv
import uuid
import mysql.connector
from time import perf_counter
import sys
import os
import math

# if len(sys.argv) < 2:
#   print('Enter File Name')
#   sys.exit()
  
start_time = perf_counter()

# files_directory = './' + sys.argv[1]
# file_names = os.listdir(files_directory)

output = ["name,team\n"]

file = open('./AFL players 2021 raw.txt', 'r', encoding='utf8')
data = file.readlines()

current_name = ''
current_team = ''

for line in data:
  if line[0] == "?":
    current_team = line.replace(line[0],'')
  else :
    line_array = line.split()
    if len(line_array[1]) < 2 and len(line_array[1]) > 0:
      current_name = line_array[2] + " " + line_array[3]
      if not line_array[4].isnumeric():
        current_name = current_name + " " + line_array[4]
    else:
      current_name = line_array[1] + " " + line_array[2]
      if not line_array[3].isnumeric():
        current_name = current_name + " " + line_array[3]
    output.append(current_name.title().strip() + ',' + current_team.strip() + '\n')

write_file = open("./afl_players_2021.csv","w")

write_file.writelines(output)
write_file.close()  


