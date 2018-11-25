import requests
from operator import add
import time


URL = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"
geturl = URL + "/game?token="
UID = "004823094"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
OPP_DIRECTION = {
	"UP": 	"DOWN",
	"DOWN": "UP",
	"RIGHT":"LEFT",
	"LEFT":	"RIGHT"
}
DIRECTIONS = ["RIGHT", "DOWN", "LEFT", "UP"]


class MazeSolver:

	def __init__(self):
		self.needs_reset = True
		self.status = "PLAYING"
		self.justpopped = False

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
		# for i in range(self.maze_size[1]):
		# 	print(self.visited[i])

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
		# print("Sending post request with action = {}".format(action))
		r = requests.post(geturl + self.token, data={"action": action}, headers=headers)
		if r.status_code == requests.codes.ok:
			data = r.json()
			if data["result"] == "SUCCESS":
				self.curr = list(map(add, self.curr, self.get_direction(action)))
				self.visited[self.curr[1]][self.curr[0]] = 1
				# self.print_status()
				return "SUCCESS"

			elif data["result"] == "WALL":
				wall_location = list(map(add, self.curr, self.get_direction(action)))
				self.visited[wall_location[1]][wall_location[0]] = -1
				print("Hit the wall going {} form {}".format(action, self.curr))
				# self.print_status()
				return "WALL"

			elif data["result"] == "END":
				print("Reached destination!")
				self.needs_reset = True
				return "END"

			elif data["result"] == "OUT_OF_BOUNDS":
				print("Out of bounds going {} form {}".format(action, self.curr))
				return "OUT_OF_BOUNDS"
			else:
				print("CONNECTION ERROR on MOVEMENT POST")
				self.print_status()
				exit()
		else:
			print("CONNECTION ERROR on MOVEMENT POST")
			self.print_status()
			exit()


	def generate_next_step(self, loc):
		for direct in DIRECTIONS:
			step = self.get_direction(direct)
			candidate = list(map(add, self.curr, step))
			# print("NEXT claim is {}. Candidate = {}.".format(direct, candidate))
			if 0 <= candidate[1] < self.maze_size[1] and 0 <= candidate[0] < self.maze_size[0]:
				if self.visited[candidate[1]][candidate[0]] == 0:
					# print("I RETURN {}".format(direct))
					return direct
		return None

	def solve(self):
		# self.print_status()
		# self.driver()
		while self.status != "FINISHED":
			self.get_maze()
			self.print_status()
			self.solve_maze()

		print("Congratulations! You've passed all levels!")

	def solve_maze(self):
		self.path = []
		next_step = self.generate_next_step(self.curr)
		if next_step == None:
			exit("No next step found on startup.")
		result = self.post_movement(next_step)

		while result != "END":
			# time.sleep(0.05)
			if result == "SUCCESS":
				if not self.justpopped:
					self.path.append(next_step)
				self.justpopped = False
				next_step = self.generate_next_step(self.curr)
			elif result == "WALL":
				next_step = self.generate_next_step(self.curr)
				

			if next_step == None:
				# print("NEED TO BACKTRACK")
				last_move = self.path.pop()
				self.justpopped = True
				# print("Popped {}. Will go {}.".format(last_move, OPP_DIRECTION[last_move]))
				next_step = OPP_DIRECTION[last_move]

			result = self.post_movement(next_step)

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
