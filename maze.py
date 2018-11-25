import requests

URL = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"
geturl = URL + "/game?token="
UID = "004823094"
headers = {"Content-Type": "application/x-www-form-urlencoded"}

class MazeSolver:

	def __init__(self):
		pass

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
			return 0

	def post_movement(self, action):
		r = requests.post(geturl + self.token, data={"action": action}, headers=headers)
		if r.status_code == requests.codes.ok:
			data = r.json()
			return data["result"]

	def solve(self):
		self.get_maze()
		print("SIZE: = {}. LOC = {}. STATUS = {}. LVLS COMPLETED = {}".format(
			self.maze_size, 
			self.curr,
			self.status,
			self.completed)
		)



if __name__ == "__main__":
	m = MazeSolver()
	m.solve()


