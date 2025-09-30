# font_fixer.py - Sửa lỗi font và tải đúng font
import pygame
import requests
import os

def download_noto_font():
    """Tải font Noto Sans hỗ trợ tiếng Việt"""
    # URL ĐÚNG của font Noto Sans
    font_url = "https://github.com/notofonts/notofonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
    font_path = "NotoSans-Regular.ttf"
    
    if not os.path.exists(font_path):
        try:
            print("Đang tải font tiếng Việt...")
            response = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(response.content)
            print("Tải font thành công!")
            return font_path
        except Exception as e:
            print(f"Không thể tải font online: {e}")
            print("Sử dụng font hệ thống...")
            return None
    else:
        print("Font đã tồn tại!")
        return font_path

def create_vietnamese_fonts():
    """Tạo các font hỗ trợ tiếng Việt"""
    font_path = download_noto_font()
    
    if font_path and os.path.exists(font_path):
        try:
            # Sử dụng Noto Sans - SỬA LỖI CHÍNH TẢ: Font chứ không phải font
            font_title = pygame.font.Font(font_path, 36)
            font_category = pygame.font.Font(font_path, 24)
            font_name = pygame.font.Font(font_path, 20)
            font_desc = pygame.font.Font(font_path, 16)
            print("Đang sử dụng font Noto Sans")
            return font_title, font_category, font_name, font_desc
        except Exception as e:
            print(f"Lỗi khi tạo font từ file: {e}")
    
    # Fallback: sử dụng font hệ thống
    try:
        font_title = pygame.font.SysFont("arial", 36)
        font_category = pygame.font.SysFont("arial", 24)
        font_name = pygame.font.SysFont("arial", 20)
        font_desc = pygame.font.SysFont("arial", 16)
        print("Đang sử dụng font Arial hệ thống")
        return font_title, font_category, font_name, font_desc
    except:
        # Cuối cùng: font mặc định
        print("Sử dụng font mặc định")
        return (
            pygame.font.Font(None, 36),
            pygame.font.Font(None, 24),
            pygame.font.Font(None, 20),
            pygame.font.Font(None, 16)
        )

if __name__ == "__main__":
    pygame.init()
    fonts = create_vietnamese_fonts()
    print("Khởi tạo font thành công!")