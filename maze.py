import requests
from operator import add
import logging
from pprint import pformat


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
		logging.basicConfig(filename='maze.log', level=logging.DEBUG, filemode='w')
		urllib3_logger = logging.getLogger('urllib3')
		urllib3_logger.setLevel(logging.CRITICAL)
		# for key in logging.Logger.manager.loggerDict:
		# 	print(key)


	def get_token(self):
		r = requests.post(URL + "/session", data={'uid': UID}, headers=headers)
		if r.status_code == requests.codes.ok:
			data = r.json()
			token = data["token"]
			logging.debug("My token is {}".format(token))
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
		# print("SIZE: = {}. LOC = {}. STATUS = {}. LVLS COMPLETED = {}. TOTAL = {}".format(
		# 	self.maze_size, 
		# 	self.curr,
		# 	self.status,
		# 	self.completed,
		# 	self.levels))
		# for i in range(self.maze_size[1]):
		# 	print(self.visited[i])
		logging.debug("SIZE: = {}. LOC = {}. STATUS = {}. LVLS COMPLETED = {}. TOTAL = {}".format(
			self.maze_size, 
			self.curr,
			self.status,
			self.completed,
			self.levels))
		logging.debug(pformat(self.visited))

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
				return "SUCCESS"

			elif data["result"] == "WALL":
				wall_location = list(map(add, self.curr, self.get_direction(action)))
				self.visited[wall_location[1]][wall_location[0]] = -1
				# logging.debug("Hit the wall going {} form {}".format(action, self.curr))
				return "WALL"

			elif data["result"] == "END":
				logging.debug("Reached destination!")
				self.curr = list(map(add, self.curr, self.get_direction(action)))
				self.visited[self.curr[1]][self.curr[0]] = "X"
				self.needs_reset = True
				return "END"

			elif data["result"] == "OUT_OF_BOUNDS":
				logging.debug("Out of bounds going {} form {}".format(action, self.curr))
				return "OUT_OF_BOUNDS"
			else:
				logging.debug("Timeout. Try again.")
				exit()
		else:
			logging.debug("CONNECTION ERROR on MOVEMENT POST")
			self.print_status()
			exit()


	def generate_next_step(self, loc):
		for direct in DIRECTIONS:
			step = self.get_direction(direct)
			candidate = list(map(add, self.curr, step))
			if 0 <= candidate[1] < self.maze_size[1] and 0 <= candidate[0] < self.maze_size[0]:
				if self.visited[candidate[1]][candidate[0]] == 0:
					return direct
		return None

	def solve(self):
		while 1:
			self.get_maze()
			if self.status == "FINISHED":
				print("Congratulations! You've passed all levels!")
				return
			self.solve_maze()
			self.print_status()

		

	def solve_maze(self):
		self.path = []
		next_step = self.generate_next_step(self.curr)
		if next_step == None:
			exit("No next step found on startup.")
		result = self.post_movement(next_step)
		logging.debug(pformat(self.visited))
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

	# Use this function in main to manually solve puzzles
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
