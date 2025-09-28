import pygame
import sys
import os

pygame.init()
screen = pygame.display.set_mode((800, 650))
pygame.display.set_caption("Chọn Thuật Toán Tìm Đường")

# Load font
BASE_DIR = os.path.dirname(__file__)
FONT_PATH = os.path.join(BASE_DIR, "NotoSans-Regular.ttf")

if os.path.exists(FONT_PATH):
    # Điều chỉnh kích thước font nhỏ hơn cho gọn gàng
    font_title = pygame.font.Font(FONT_PATH, 28)      # Giảm từ 36 -> 28
    font_category = pygame.font.Font(FONT_PATH, 20)   # Giảm từ 24 -> 20  
    font_name = pygame.font.Font(FONT_PATH, 18)       # Giảm từ 20 -> 18
    font_desc = pygame.font.Font(FONT_PATH, 14)       # Giảm từ 16 -> 14
else:
    font_title = pygame.font.SysFont("Arial", 28)
    font_category = pygame.font.SysFont("Arial", 20)
    font_name = pygame.font.SysFont("Arial", 18)
    font_desc = pygame.font.SysFont("Arial", 14)

# Danh sách thuật toán với tiếng Việt có dấu đầy đủ
algorithm_categories = {
    "TÌM KIẾM KHÔNG CÓ THÔNG TIN": [
        ("Breadth-First Search", "Tìm đường ngắn nhất bằng cách duyệt theo chiều rộng", (34, 139, 34)),
        ("Depth-First Search", "Tìm đường bằng cách duyệt theo chiều sâu", (0, 191, 255)),
        ("Uniform Cost Search", "Tìm đường với chi phí tích lũy nhỏ nhất", (70, 130, 180)),
    ],
    "TÌM KIẾM CÓ THÔNG TIN": [
        ("A* (A-Star)", "Tìm đường thông minh kết hợp chi phí và heuristic", (255, 165, 0)),
        ("Greedy Best-First", "Tìm đường dựa trên heuristic", (255, 215, 0)),
        ("Beam Search", "Tìm đường theo chiều rộng nhưng giới hạn lựa chọn", (139, 69, 19)),
    ],
    "TÌM KIẾM CÓ RÀNG BUỘC": [
        ("Backtracking", "Quay lui khi gặp chướng ngại vật", (124, 252, 0)),
        ("Forward Checking", "Kiểm tra ràng buộc trước khi gán giá trị", (50, 205, 50)),
    ],
    "THUẬT TOÁN TỐI ƯU": [
        ("Simulated Annealing", "Tìm kiếm mô phỏng luyện kim", (199, 21, 133)),
        ("Genetic Algorithm", "Thuật toán di truyền tối ưu đường đi", (106, 90, 205)),
        ("Ant Colony Optimization", "Tối ưu đàn kiến tìm đường", (210, 105, 30)),
    ],
    "HỌC MÁY & AI": [
        ("Q-Learning", "Học tăng cường để tìm đường tối ưu", (30, 144, 255)),
        ("Deep Q-Network (DQN)", "Kết hợp Q-Learning với neural network", (65, 105, 225)),
    ],
    "MÔI TRƯỜNG ĐẶC BIỆT": [
        ("Partial Observation Search", "Quan sát từng phần mê cung", (148, 0, 211)),
        ("D* Lite", "Tìm đường động cho môi trường thay đổi", (220, 20, 60)),
        ("Bidirectional Search", "Tìm kiếm hai chiều từ start và goal", (75, 0, 130)),
    ]
}

selected_algo = None
scroll_offset = 0
scroll_dragging = False
scroll_start_y = 0

def draw_scrollbar(popup_rect, content_height, visible_height):
    global scroll_offset
    
    scroll_area_height = popup_rect.height - 100
    if content_height > visible_height:
        scrollbar_height = max(30, (visible_height / content_height) * scroll_area_height)
        scroll_ratio = scroll_offset / (content_height - visible_height)
        scrollbar_y = popup_rect.y + 100 + (scroll_area_height - scrollbar_height) * scroll_ratio
        
        scrollbar_rect = pygame.Rect(popup_rect.right - 15, scrollbar_y, 8, scrollbar_height)
        pygame.draw.rect(screen, (180, 180, 180), scrollbar_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 120, 120), scrollbar_rect, 1, border_radius=4)
        return scrollbar_rect
    return None

def draw_popup():
    global scroll_offset
    
    popup_rect = pygame.Rect(40, 20, 720, 610)  # Điều chỉnh kích thước popup
    
    # Vẽ nền popup
    pygame.draw.rect(screen, (245, 245, 245), popup_rect, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), popup_rect, 2, border_radius=10)
    
    # Tiêu đề chính
    title_text = "CHỌN THUẬT TOÁN TÌM ĐƯỜNG"
    title = font_title.render(title_text, True, (0, 102, 204))
    screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.y + 15))

    # Tính toán tổng chiều cao nội dung (giảm khoảng cách)
    content_height = 0
    for category, algorithms_list in algorithm_categories.items():
        content_height += 35  # Giảm từ 40 -> 35
        content_height += len(algorithms_list) * 55  # Giảm từ 65 -> 55
    
    visible_height = popup_rect.height - 90  # Giảm từ 100 -> 90
    max_scroll = max(0, content_height - visible_height)
    scroll_offset = max(0, min(scroll_offset, max_scroll))
    
    scrollbar_rect = draw_scrollbar(popup_rect, content_height, visible_height)

    # Tạo surface cho nội dung cuộn
    content_surface = pygame.Surface((popup_rect.width - 35, visible_height))  # Giảm padding
    content_surface.fill((245, 245, 245))
    
    btn_list = []
    current_y = -scroll_offset
    
    for category, algorithms_list in algorithm_categories.items():
        if current_y + 35 > 0 and current_y < visible_height:
            # Category background nhỏ gọn hơn
            category_bg = pygame.Rect(5, current_y, popup_rect.width - 45, 30)  # Giảm chiều cao
            pygame.draw.rect(content_surface, (210, 225, 240), category_bg, border_radius=4)
            pygame.draw.rect(content_surface, (80, 130, 180), category_bg, 1, border_radius=4)
            
            category_text = font_category.render(category, True, (0, 70, 140))
            content_surface.blit(category_text, (10, current_y + 6))  # Căn chỉnh vị trí text
        
        current_y += 35  # Giảm khoảng cách giữa các category
        
        for name, desc, color in algorithms_list:
            if current_y + 55 > 0 and current_y < visible_height:
                # Algorithm background nhỏ gọn
                algo_bg = pygame.Rect(8, current_y, popup_rect.width - 55, 50)  # Giảm chiều cao
                if selected_algo == name:
                    pygame.draw.rect(content_surface, (255, 250, 200), algo_bg, border_radius=6)
                else:
                    pygame.draw.rect(content_surface, (255, 255, 255), algo_bg, border_radius=6)
                pygame.draw.rect(content_surface, (210, 210, 210), algo_bg, 1, border_radius=6)

                # Tên thuật toán - căn trái
                name_text = font_name.render(name, True, (0, 90, 0))
                content_surface.blit(name_text, (12, current_y + 5))

                # Mô tả - ngắn gọn hơn, 2 dòng nếu cần
                desc_lines = []
                if len(desc) > 50:  # Cắt mô tả nếu quá dài
                    words = desc.split()
                    line1 = ' '.join(words[:len(words)//2])
                    line2 = ' '.join(words[len(words)//2:])
                    desc_lines = [line1, line2]
                else:
                    desc_lines = [desc]
                
                for i, line in enumerate(desc_lines):
                    desc_text = font_desc.render(line, True, (70, 70, 70))
                    content_surface.blit(desc_text, (12, current_y + 25 + i*15))

                # Nút chọn nhỏ gọn hơn
                btn = pygame.Rect(popup_rect.width - 140, current_y + 8, 80, 32)  # Nút nhỏ hơn
                mouse_pos = pygame.mouse.get_pos()
                adjusted_mouse_pos = (mouse_pos[0] - popup_rect.x - 20, mouse_pos[1] - popup_rect.y - 90)
                
                btn_color = color
                if btn.collidepoint(adjusted_mouse_pos):
                    btn_color = tuple(min(c + 20, 255) for c in color)  # Hiệu ứng hover nhẹ hơn
                
                pygame.draw.rect(content_surface, btn_color, btn, border_radius=6)
                pygame.draw.rect(content_surface, (255, 255, 255), btn, 1, border_radius=6)
                
                label = font_desc.render("CHỌN", True, (255, 255, 255))  # Font nhỏ hơn cho nút
                label_rect = label.get_rect(center=btn.center)
                content_surface.blit(label, label_rect)

                real_btn = pygame.Rect(popup_rect.x + 20 + btn.x, popup_rect.y + 90 + btn.y, btn.width, btn.height)
                btn_list.append((real_btn, name))
            
            current_y += 55  # Giảm khoảng cách giữa các algorithm
    
    screen.blit(content_surface, (popup_rect.x + 20, popup_rect.y + 80))  # Điều chỉnh vị trí
    
    # Hiển thị thuật toán đã chọn - gọn gàng hơn
    if selected_algo:
        selected_bg = pygame.Rect(popup_rect.x + 20, popup_rect.y + 540, popup_rect.width - 40, 40)
        pygame.draw.rect(screen, (230, 240, 255), selected_bg, border_radius=6)
        pygame.draw.rect(screen, (80, 130, 200), selected_bg, 1, border_radius=6)
        
        selected_text = f"ĐÃ CHỌN: {selected_algo}"
        # Cắt tên nếu quá dài
        if len(selected_text) > 40:
            selected_text = selected_text[:37] + "..."
        selected_surface = font_category.render(selected_text, True, (0, 0, 150))
        screen.blit(selected_surface, (popup_rect.centerx - selected_surface.get_width()//2, popup_rect.y + 550))
    
    return btn_list, scrollbar_rect

# Main loop
running = True
btns = []
scrollbar_rect = None

while running:
    screen.fill((250, 250, 250))  # Màu nền sáng hơn
    btns, scrollbar_rect = draw_popup()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for btn, name in btns:
                    if btn.collidepoint(event.pos):
                        selected_algo = name
                        print(f"Đã chọn: {name}")
                
                if scrollbar_rect and scrollbar_rect.collidepoint(event.pos):
                    scroll_dragging = True
                    scroll_start_y = event.pos[1]
            
            elif event.button == 4:  # Cuộn lên
                scroll_offset = max(0, scroll_offset - 30)  # Cuộn ít hơn
            elif event.button == 5:  # Cuộn xuống
                content_height = sum(35 + len(algorithms) * 55 for algorithms in algorithm_categories.values())
                visible_height = 520
                max_scroll = max(0, content_height - visible_height)
                scroll_offset = min(max_scroll, scroll_offset + 30)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                scroll_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if scroll_dragging and scrollbar_rect:
                content_height = sum(35 + len(algorithms) * 55 for algorithms in algorithm_categories.values())
                visible_height = 520
                max_scroll = max(0, content_height - visible_height)
                
                delta_y = event.pos[1] - scroll_start_y
                scroll_area_height = 520 - 30
                scroll_ratio = delta_y / scroll_area_height
                scroll_offset = max(0, min(max_scroll, scroll_offset + scroll_ratio * content_height))
                scroll_start_y = event.pos[1]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                scroll_offset = max(0, scroll_offset - 30)
            elif event.key == pygame.K_DOWN:
                content_height = sum(35 + len(algorithms) * 55 for algorithms in algorithm_categories.values())
                visible_height = 520
                max_scroll = max(0, content_height - visible_height)
                scroll_offset = min(max_scroll, scroll_offset + 30)

    pygame.display.flip()

pygame.quit()
sys.exit()