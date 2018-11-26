# UPE-Coding-Challenge-2018

This repo contains my solution for UPE Induction Coding Challenge in Fall 2018.

The specification can be found here: https://gist.github.com/austinguo550/381d5e30d825b90900ef60fa39a806f4.


## Solution overview

The main engine for the solution is the class **`MazeSolver`**.
### Important attributes

#### `self.visited`:
Maze with visited spots marked 1, non-visited marked 0, walls marked -1, and, at the end, destination marked with X. 

#### `self.path`:		
List of steps I made from the initial location. Used to backtrack.

#### `self.curr`:
Current location in the maze.

Other attributes are simply utilities to keep track of status, maze size, etc.

### Idea 
To pick a next step, I call `generate_next_step(self, loc)` method
which returns next not yet visited spot I should go to (that share a side with loc).
The spots are chosen starting from RIGHT going clockwise,
and the first not yet visited is returned. If there are no available spots, this method returns `None`.

With every new step, I update `self.path` correspondingly, appending it with the direction. Once there are no unvisited spots that I can go to from particular location, I have to backtrack.
Thus, I go in the opposite direction of the last entry in `self.path`, 
making sure I go back. I pop that last entry. Then I continue execution. 

Such implementation makes sure I will eventually visit 
all spots I can possibly visit from the initial location.

### Some other functions

#### `solve()`:
method that is called after the creation of the class. Calls 
`solve_maze()` for each maze to solve.

#### `get_maze()`, `get_token()`:
helper functions to talk to API and get data from the server;

#### `post_movement(action)`:
Makes a POST request with specified *action*. 
Correspondingly updates `self.visited` and `self.curr`.