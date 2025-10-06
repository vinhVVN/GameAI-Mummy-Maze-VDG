from collections import deque

class ForwardChecking:
    """
    Thuật toán Backtracking + Forward Checking cho cả SimpleMazeProblem và MazeProblem.
    """

    def __init__(self, problem, max_depth=2000, min_safe_dist=2, debug=False):
        self.problem = problem
        self.maze = problem.maze
        self.max_depth = max_depth
        self.min_safe_dist = min_safe_dist
        self.best_path = None
        self.found = False
        self.debug = debug
        self.is_simple_problem = not hasattr(problem, 'min_dist')  # Phân biệt loại problem

    def solve(self):
        start = self.problem.get_init_state()
        visited = set([start])
        self.best_path = None
        self.found = False
        self._dfs(start, [], visited, 0)
        return self.best_path

    def _dfs(self, state, path, visited, depth):
        if depth > self.max_depth:
            return

        if self.problem.is_goal_state(state):
            self.best_path = path[:]
            self.found = True
            if self.debug:
                print(f"✅ Found goal! Path = {path}")
            return

        try:
            moves = self.problem.get_move(state)
        except Exception as e:
            if self.debug:
                print(f"⚠️ get_move error: {e}")
            moves = []

        for next_state, action, cost in moves:
            # Bỏ qua nếu đã thăm hoặc cost vô hạn
            if cost == float('inf') or next_state in visited:
                continue

            # Forward Checking - ÁP DỤNG CHO CẢ HAI LOẠI PROBLEM
            if not self._forward_check(next_state):
                continue

            visited.add(next_state)
            path.append(action)

            if self.debug:
                print(f"→ Depth {depth}: Move {action} | State = {next_state}")

            self._dfs(next_state, path, visited, depth + 1)
            if self.found:
                return

            path.pop()
            visited.remove(next_state)

    def _forward_check(self, state):
        """Forward checking cho cả SimpleMazeProblem và MazeProblem"""
        
        # LẤY VỊ TRÍ PLAYER PHÙ HỢP VỚI TỪNG LOẠI PROBLEM
        player_pos = self._get_player_position(state)
        
        if player_pos is None:
            if self.debug:
                print(f"⚠️ Không thể xác định player position từ state: {state}")
            return False

        # 1️⃣ Trap check (nếu có)
        trap = getattr(self.problem, 'trap_pos', None)
        if trap and player_pos == trap:
            if self.debug:
                print(f"💀 Player rơi vào bẫy tại {trap}")
            return False

        # 2️⃣ Mummy proximity check (chỉ cho MazeProblem)
        if not self.is_simple_problem and hasattr(self.problem, 'min_dist'):
            try:
                # State format: (player_pos, mummies_pos)
                mummies_pos = state[1] if isinstance(state, tuple) and len(state) == 2 else []
                md = self.problem.min_dist(list(mummies_pos), player_pos)
                
                if md <= self.min_safe_dist:
                    if self.debug:
                        print(f"☠️ Quá gần mummy (dist={md}) tại {player_pos}")
                    return False
            except Exception as e:
                if self.debug:
                    print(f"⚠️ Lỗi kiểm tra mummy: {e}")

        # 3️⃣ Reachability check (BFS) - QUAN TRỌNG NHẤT
        if not self._is_reachable_to_goal(player_pos):
            if self.debug:
                print(f"🚫 Không thể tới goal từ {player_pos}")
            return False

        return True

    def _get_player_position(self, state):
        """Lấy vị trí player từ state, hỗ trợ cả hai định dạng"""
        try:
            if self.is_simple_problem:
                # SimpleMazeProblem: state là (x, y)
                if isinstance(state, tuple) and len(state) == 2:
                    return state
            else:
                # MazeProblem: state là (player_pos, mummies_pos)
                if isinstance(state, tuple) and len(state) == 2:
                    player_pos = state[0]
                    if isinstance(player_pos, tuple) and len(player_pos) == 2:
                        return player_pos
            
            # Fallback: thử parse bất kỳ tuple nào có 2 phần tử
            if isinstance(state, tuple) and len(state) == 2:
                if all(isinstance(x, int) for x in state):
                    return state
            
            return None
            
        except Exception:
            return None

    def _is_reachable_to_goal(self, player_pos):
        """BFS kiểm tra reachability - FIXED VERSION"""
        if not (isinstance(player_pos, tuple) and len(player_pos) == 2):
            return False

        # Lấy goal position
        goal = getattr(self.problem, 'goal_pos', None) or getattr(self.problem, 'goal', None)
        if goal is None:
            # Nếu không có goal, coi như reachable
            return True
            
        if player_pos == goal:
            return True

        maze = self.maze
        try:
            width, height = maze.maze_size
        except Exception:
            # Fallback nếu không lấy được maze size
            width, height = 100, 100  # Giá trị đủ lớn

        visited = set()
        q = deque([player_pos])
        visited.add(player_pos)
        
        # Hướng di chuyển (2 ô vì đi qua walls)
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        while q:
            cx, cy = q.popleft()
            
            for dx, dy in dirs:
                # Vị trí tường cần kiểm tra
                wall_x = cx + dx // 2
                wall_y = cy + dy // 2
                
                # Vị trí tiếp theo
                nx, ny = cx + dx, cy + dy

                # Kiểm tra giới hạn bản đồ
                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                # Kiểm tra tường
                try:
                    if not maze.is_passable(wall_x, wall_y):
                        continue
                except Exception:
                    continue

                npos = (nx, ny)
                if npos in visited:
                    continue
                    
                if npos == goal:
                    return True
                    
                visited.add(npos)
                q.append(npos)

        return False