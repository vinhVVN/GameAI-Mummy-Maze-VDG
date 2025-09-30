import pygame
import os
import threading
import time
from src.settings import SOUNDS_PATH

class SoundManager:
    """Quản lý âm thanh hiệu ứng trong game"""
    
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.volume = 0.7
        self.sound_duration = 0.5  # Giới hạn độ dài âm thanh 0.5 giây
        self.active_channels = {}  # Theo dõi các kênh âm thanh đang phát
        
        # Khởi tạo pygame mixer nếu chưa có
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.load_sounds()
        except pygame.error as e:
            print(f"Lỗi khởi tạo âm thanh: {e}")
            self.enabled = False
    
    def load_sounds(self):
        """Load tất cả âm thanh hiệu ứng"""
        sound_files = {
            'human_move': 'human_move.mp3',
            'monster_move': 'monster_move.mp3',
            'click': 'click.mp3',
            'move': 'move.mp3',
            'lose': 'lose.mp3'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join(SOUNDS_PATH, filename)
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {sound_name}")
                else:
                    print(f"Cảnh báo: Không tìm thấy file âm thanh {sound_path}")
            except pygame.error as e:
                print(f"Lỗi khi load âm thanh {filename}: {e}")
    
    def play_sound(self, sound_name, duration_limit=None):
        """Phát âm thanh theo tên với giới hạn thời gian"""
        if not self.enabled:
            return
            
        if sound_name in self.sounds:
            try:
                # Dừng âm thanh cùng loại nếu đang phát
                if sound_name in self.active_channels:
                    channel = self.active_channels[sound_name]
                    if channel and channel.get_busy():
                        channel.stop()
                
                # Phát âm thanh mới
                channel = self.sounds[sound_name].play()
                if channel:
                    self.active_channels[sound_name] = channel
                    
                    # Tạo timer để dừng âm thanh sau thời gian giới hạn
                    limit_time = duration_limit or self.sound_duration
                    timer = threading.Timer(limit_time, self._stop_sound_after_delay, 
                                          args=(sound_name, channel))
                    timer.start()
                    
            except pygame.error as e:
                print(f"Lỗi khi phát âm thanh {sound_name}: {e}")
        else:
            print(f"Không tìm thấy âm thanh: {sound_name}")
    
    def _stop_sound_after_delay(self, sound_name, channel):
        """Dừng âm thanh sau khoảng thời gian delay"""
        try:
            if channel and channel.get_busy():
                channel.stop()
            # Xóa khỏi active_channels
            if sound_name in self.active_channels:
                del self.active_channels[sound_name]
        except:
            pass
    
    def play_human_move(self):
        """Phát âm thanh khi con người di chuyển (0.5 giây)"""
        self.play_sound('human_move', 0.5)
    
    def play_monster_move(self):
        """Phát âm thanh khi quái vật di chuyển (0.5 giây)"""
        self.play_sound('monster_move', 0.5)
    
    def set_volume(self, volume):
        """Đặt âm lượng cho tất cả âm thanh hiệu ứng (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def toggle_sound(self):
        """Bật/tắt âm thanh"""
        self.enabled = not self.enabled
        return self.enabled
    
    def stop_all_sounds(self):
        """Dừng tất cả âm thanh đang phát"""
        try:
            # Dừng tất cả channels đang hoạt động
            for sound_name, channel in self.active_channels.items():
                if channel and channel.get_busy():
                    channel.stop()
            self.active_channels.clear()
            
            # Dừng tất cả âm thanh còn lại
            for sound in self.sounds.values():
                sound.stop()
        except:
            pass
    
    def set_sound_duration(self, duration):
        """Đặt thời gian giới hạn cho âm thanh (giây)"""
        self.sound_duration = max(0.1, min(5.0, duration))  # Giới hạn từ 0.1 đến 5 giây

# Tạo instance global để sử dụng trong toàn bộ game
sound_manager = SoundManager()