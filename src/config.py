# config.py
import pygame

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_PANEL_BG = (50, 50, 60)

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
MAZE_PANEL_WIDTH = 800
CONTROL_PANEL_WIDTH = SCREEN_WIDTH - MAZE_PANEL_WIDTH
MAZE_COORD_X = 50
MAZE_COORD_Y = 50

# Game settings
FPS = 60
IMAGES_PATH = "images"

class GameConfig:
    WAIT_DURATION = 1000
    DEFAULT_PLAYER_ALGO = "BFS"
    DEFAULT_MUMMY_ALGO = "classic"
    
    # Map configurations
    MAP_CONFIGS = {
        "map6_1.txt": {"player": (1, 1), "mummies": [(5, 9)]},
        "map6_2.txt": {"player": (1, 11), "mummies": [(3, 3)]},
        "map6_3.txt": {"player": (1, 11), "mummies": [(3, 3)]},
        "map6_4.txt": {"player": (1, 11), "mummies": [(3, 3)]},
        "map6_5.txt": {"player": (1, 11), "mummies": [(9, 9)]},
        "map8_1.txt": {"player": (1, 15), "mummies": [(15, 11), (3, 3)]}
    }
    
    # Algorithm categories for popup
    ALGORITHM_CATEGORIES = {
        "TÌM KIẾM KHÔNG CÓ THÔNG TIN": [
            ("BFS", "Tìm đường ngắn nhất bằng cách duyệt theo chiều rộng", (34, 139, 34)),
            ("DFS", "Tìm đường bằng cách duyệt theo chiều sâu", (0, 191, 255)),
            ("IDS", "Tìm kiếm theo chiều sâu lặp", (70, 130, 180)),
        ],
        "TÌM KIẾM CÓ THÔNG TIN": [
            ("AStart", "Tìm đường thông minh kết hợp chi phí và heuristic", (255, 165, 0)),
            ("Greedy", "Tìm đường dựa trên heuristic", (255, 215, 0)),
            ("UCS", "Tìm đường với chi phí tích lũy nhỏ nhất", (100, 149, 237)),
        ],
        "THUẬT TOÁN TỐI ƯU": [
            ("Hill climbing"," sẽ không bao giờ đi xuống", (255, 215, 0)),
            ("SA", "Tìm kiếm mô phỏng luyện kim", (199, 21, 133)),
            ("Beam", "Tìm đường theo chiều rộng nhưng giới hạn lựa chọn", (139, 69, 19)),
        ],
        "TÌM KIẾM TRONG MÔI TRƯỜNG PHỨC TẠP":[
            ("Non_infor","Không có thông tin gì",(199, 21, 0)),
            ("PO_search", "Tìm kiếm mù một phần", (144, 74, 24))
        ],
        "CSP: Constraint Satisfaction Problem " :[
            ("Forward Checking", "Giống như backtracking nhưng kiểm tra lại tập giá trị sau mỗi lần đi", (144, 69, 19))
        ]
    }