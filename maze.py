import requests
from operator import add


URL = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"
geturl = URL + "/game?token="
UID = "004823094"
headers = {"Content-Type": "application/x-www-form-urlencoded"}


class MazeSolver:

	def __init__(self):
		self.needs_reset = True

	def get_token(self):
		r = requests.post(URL + "/session", data={'uid': UID}, headers=headers)
		if r.status_code == requests.codes.ok:
			data = r.json()
			token = data["token"]
			print("My new token is {}".format(token))
			self.token = token
			
	def get_maze(self):	
		self.get_token()
		r = requests.get(geturl + self.token)
		if r.status_code == requests.codes.ok:
			data = r.json()
			self.maze_size = data["maze_size"]
			self.curr = data["current_location"]
			self.status = data["status"]
			self.completed = data["levels_completed"]
			self.levels = data["total_levels"]
			if self.needs_reset == True:
				self.visited = [[0 for x in range(self.maze_size[0])] for y in range(self.maze_size[1])]
				self.visited[self.curr[1]][self.curr[0]] = 1
				self.needs_reset = False
			return 0

	def print_status(self):
		print("SIZE: = {}. LOC = {}. STATUS = {}. LVLS COMPLETED = {}. TOTAL = {}".format(
			self.maze_size, 
			self.curr,
			self.status,
			self.completed,
			self.levels))
		for i in range(self.maze_size[1]):
			print(self.visited[i])

	def get_direction(self, action):
		if action == "RIGHT":
			return [1, 0]
		elif action == "LEFT":
			return [-1, 0]
		elif action == "DOWN":
			return [0, 1]
		elif action == "UP":
			return [0, -1]

	def post_movement(self, action):
		r = requests.post(geturl + self.token, data={"action": action}, headers=headers)
		if r.status_code == requests.codes.ok:
			data = r.json()
			if data["result"] == "SUCCESS":
				self.curr = list(map(add, self.curr, self.get_direction(action)))
				self.visited[self.curr[1]][self.curr[0]] = 1
				self.print_status()

			elif data["result"] == "WALL":
				wall_location = list(map(add, self.curr, self.get_direction(action)))
				self.visited[wall_location[1]][wall_location[0]] = -1
				print("Hit the wall going {} form {}".format(action, self.curr))
				self.print_status()
				
			elif data["result"] == "END":
				print("Reached destination!")
				self.needs_reset = True

			elif data["result"] == "OUT_OF_BOUNDS":
				print("Out of bounds going {} form {}".format(action, self.curr))

	def solve(self):
		self.get_maze()
		
		self.print_status()
		self.driver()


		
	def driver(self):
		while 1:
			inp = input()
			if inp == "R":
				self.post_movement("RIGHT")
			elif inp == "D":
				self.post_movement("DOWN")
			elif inp == "L":
				self.post_movement("LEFT")
			elif inp == "U":
				self.post_movement("UP")
			elif inp == "MAZE":
				self.get_maze()
				self.print_status()
			



if __name__ == "__main__":
	m = MazeSolver()
	m.solve()
