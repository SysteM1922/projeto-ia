import json
import os
import time
import sys

file = []

try:
	os.rename('highscores.json', 'highscores2.json')
except:
	pass
os.system('python3 server.py &')
os.system('python3 viewer.py &')

for i in range(int(sys.argv[1])):
	time.sleep(1)
	os.system("python3 student.py")

	with open('highscores.json', 'r') as f:
		for line in f:
			file += [json.loads(line)[-1]]
			break
	file[-1][0] = "Score "+str(i+1)

print()
lst = [(i[0],str(i[1])) for i in file]
[print(s[0]+": "+s[1]) for s in sorted(lst, key=lambda x: int(x[0].split()[1]))]

os.remove('highscores.json')
os.rename('highscores2.json', 'highscores.json')
os.system('killall python3')