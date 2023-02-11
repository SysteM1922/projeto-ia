from collections import defaultdict, deque
import math
import time
import heapq

with open('levels.txt') as f:
	levels = f.read()
levels = levels.splitlines()
levels = [l.split()[1] for l in levels]

def default_check_goal(level, size):
	return 'A' in level[size-1::size]

def default_heuristic(level, size):
	i = level.index('A')
	return size - i%size - 2 + sum(1 for idx in range(i+2, (i//size+1)*size) if level[idx] != 'o')

def search(level, size, check_goal = default_check_goal, heuristic = default_heuristic):

	openset = []

	came_from = {}

	g_score = defaultdict(lambda: float('inf'))

	g_score[level] = 0
	
	heapq.heappush(openset, (heuristic(level, size), level))

	while openset:
		current = heapq.heappop(openset)[1]
		if check_goal(current, size):
			return reconstruct_path(current, size, came_from)
		for neighbor in neighbors(current, size):
			tentative_g_score = g_score[current] + 1
			if tentative_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = tentative_g_score
				heapq.heappush(openset, (g_score[neighbor] + heuristic(neighbor, size), neighbor))

	return None

def reconstruct_path(current, size, came_from):
	path = deque([])
	while current in came_from:
		path.appendleft(current)
		current = came_from[current]
	return path

def neighbors(level, size):

	cars = defaultdict(list)
	{cars[level[i]].append((i%size, i//size)) for i in range(size**2) if level[i] not in 'ox'}

	for c in cars.values():
		if c[0][1] == c[-1][1]:
			if c[0][0] > 0 and level[c[0][1]*size+c[0][0]-1] == 'o':
				new = list(level)
				new[c[0][1]*size+c[0][0]-1]=level[c[0][1]*size+c[0][0]]
				new[c[0][1]*size+c[-1][0]]='o'
				yield ''.join(new)
			if c[-1][0] < size-1 and level[c[0][1]*size+c[-1][0]+1] == 'o':
				new = list(level)
				new[c[0][1]*size+c[-1][0]+1]=level[c[0][1]*size+c[0][0]]
				new[c[0][1]*size+c[0][0]]='o'
				yield ''.join(new)
		else:
			if c[0][1] > 0 and level[(c[0][1]-1)*size+c[0][0]] == 'o':
				new = list(level)
				new[(c[0][1]-1)*size+c[0][0]]=level[c[0][1]*size+c[0][0]]
				new[c[-1][1]*size+c[0][0]]='o'
				yield ''.join(new)
			if c[-1][1] < size-1 and level[(c[-1][1]+1)*size+c[0][0]] == 'o':
				new = list(level)
				new[(c[-1][1]+1)*size+c[0][0]]=level[c[0][1]*size+c[0][0]]
				new[c[0][1]*size+c[0][0]]='o'
				yield ''.join(new)

def main():
	start=time.perf_counter()
	for l in range(len(levels)):
		st2=time.perf_counter()
		search(levels[l], int(math.sqrt(len(levels[l]))))
		"""print(l,":",time.perf_counter()-st2)
		levels2 = ["\n".join([l[i:i+int(math.sqrt(len(l)))] for i in range(0, len(l), int(math.sqrt(len(l))))]) for l in search(level, int(math.sqrt(len(level))))]
		for level2 in levels2:
			print(level2)
			print("\n")"""
	print("total : ",time.perf_counter()-start)
if __name__ == '__main__':
	main()

