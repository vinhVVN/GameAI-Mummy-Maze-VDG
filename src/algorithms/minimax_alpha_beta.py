from src.logger import Logger
import time

class MinimaxAlphaBeta:
    def __init__(self, problem, logger=None, max_limit=50):
        self.problem = problem
        self.logger = logger
        self.max_limit = max_limit  # Cap để tránh infinite

    def solve(self):
        start = time.perf_counter()
        best_path = []
        best_value = float('-inf')
        for limit in range(1, self.max_limit + 1):
            self.nodes_explored = 0
            value, path = self.alpha_beta_search(self.problem.get_init_state(), limit)
            self.logger.log(f"Depth limit {limit}: value {value}, path length {len(path)}, nodes {self.nodes_explored}")
            if value > best_value:
                best_value = value
                best_path = path
            if value == float('inf'):  # Found win full path
                end = time.perf_counter()
                return {"path":best_path, "nodes_expanded":self.nodes_explored,
                "time_taken": end-start, "path_length": len(best_path)}
                
        self.logger.log("No full win path found; returning best from deepest")
        end = time.perf_counter()
        return {"path":best_path, "nodes_expanded":self.nodes_explored,
                "time_taken": end-start, "path_length": len(best_path)}

    def alpha_beta_search(self, state, limit):
        value, path = self.max_value(state, float('-inf'), float('inf'), depth=0, limit=limit)
        return value, path

    def max_value(self, state, alpha, beta, depth, limit):
        self.nodes_explored += 1
        if self.problem.terminal_test(state, depth, limit):  # Adapt with limit
            return self.problem.utility(state), []

        v = float('-inf')
        best_path = []
        for action in self.problem.actions(state, is_max=True):
            next_state = self.problem.result(state, action, is_max=True)
            min_v, min_path = self.min_value(next_state, alpha, beta, depth + 1, limit)
            if min_v > v:
                v = min_v
                best_path = [action] + min_path
            if v >= beta:
                return v, best_path
            alpha = max(alpha, v)
        return v, best_path

    def min_value(self, state, alpha, beta, depth, limit):
        self.nodes_explored += 1
        if self.problem.terminal_test(state, depth, limit):
            return self.problem.utility(state), []

        v = float('inf')
        best_path = []
        for action in self.problem.actions(state, is_max=False):  # Chỉ 1
            next_state = self.problem.result(state, action, is_max=False)
            max_v, max_path = self.max_value(next_state, alpha, beta, depth + 1, limit)
            if max_v < v:
                v = max_v
                best_path = max_path
            if v <= alpha:
                return v, best_path
            beta = min(beta, v)
        return v, best_path