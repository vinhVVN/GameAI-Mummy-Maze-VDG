# algorithm_manager.py
from src.mazeproblem import MazeProblem, SimpleMazeProblem
from src.algorithms.bfs import BFS
from src.algorithms.ucs import UCS
from src.algorithms.ids import IDS
from src.algorithms.greedy import Greedy
from src.algorithms.dfs import DFS
from src.algorithms.AStart import AStar
from src.algorithms.beam import Beam
from src.algorithms.simulated_annealing import Simulated_Annealing

class AlgorithmManager:
    @staticmethod
    def solve(problem, algorithm_name, **kwargs):
        algorithms = {
            "BFS": BFS,
            "UCS": UCS,
            "IDS": lambda prob: IDS(prob, max_depth=kwargs.get('max_depth', 100)),
            "Greedy": Greedy,
            "DFS": DFS,
            "AStart": AStar,
            "Beam": Beam,
            "SA": Simulated_Annealing
        }
        
        if algorithm_name not in algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
            
        return algorithms[algorithm_name](problem)
    
    @staticmethod
    def create_problem(maze, player_pos, goal_pos, mummy_positions=None, trap_pos=None, algorithm_type="simple"):
        if algorithm_type in ["BFS", "IDS", "DFS"]:
            return SimpleMazeProblem(maze, player_pos, goal_pos)
        else:
            initial_state = player_pos, tuple(sorted(mummy_positions)) if mummy_positions else player_pos
            return MazeProblem(maze, initial_state, goal_pos, trap_pos)