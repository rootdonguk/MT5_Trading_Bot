"""
🎮 Pygame 기반 실시간 그리드 트레이딩 시각화 시스템
- 더 부드러운 애니메이션
- 인터랙티브 컨트롤
- 실시간 데이터 업데이트
"""

import pygame
import sys
import math
import time
from datetime import datetime, timedelta
from collections import deque
import threading
import queue
import json

# 색상 정의
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 100, 100),
    'GREEN': (100, 255, 100),
    'BLUE': (100, 150, 255),
    'YELLOW': (255, 255, 100),
    'CYAN': (100, 255, 255),
    'MAGENTA': (255, 100, 255),
    'ORANGE': (255, 165, 0),
    'PURPLE': (128, 0, 128),
    'GOLD': (255, 215, 0),
    'SILVER': (192, 192, 192),
    'DARK_GRAY': (64, 64, 64),
    'LIGHT_GRAY': (128, 128, 128),
    'DARK_GREEN': (0, 128, 0),
    'DARK_RED': (128, 0, 0),
}

class PygameGridVisualizer:
    def __init__(self, width=1600, height=1000, symbol="BTCUSD"):
        """Pygame 시각화 초기화"""
        pygame.init()
        
        self.width = width
        self.height = height
        self.symbol = symbol
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"🚀 {symbol} Grid Trading System - Real-time Visualization")
        
        # 폰트 설정
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 데이터 저장
        self.price_history = deque(maxlen=200)
        self.profit_history = deque(maxlen=200)
        self.timestamps = deque(maxlen=200)
        self.grid_levels = []
        self.active_positions = []
        self.current_price = 0
        self.baseline_price = 0
        self.total_profit = 0
        
        # 차트 영역 정의
        self.chart_areas = {
            'price_chart': pygame.Rect(50, 50, 700, 300),
            'profit_chart': pygame.Rect(800, 50, 700, 300),
            'positions': pygame.Rect(50, 400, 700, 250),
            'levels': pygame.Rect(800, 400, 700, 250),
            'status': pygame.Rect(50, 700, 1500, 250)
        }
        
        # 애니메이션 변수
        self.animation_time = 0
        self.last_update = time.time()
        
        # 데이터 큐
        self.data_queue = queue.Queue()
        self.running = True
        
        print("🎮 Pygame 시각화 시스템 초기화 완료!")
    
    def add_data(self, price, profit, baseline, grid_levels, positions):
        """데이터 추가"""
        try:
            data = {
                'timestamp': datetime.now(),
                'price': price,
                'profit': profit,
                'baseline': baseline,
                'grid_levels': grid_levels,
                'positions': positions
            }
            self.data_queue.put_nowait(data)
        except queue.Full:
            pass
    
    def update_data(self):
        """큐에서 데이터 업데이트"""
        updated = False
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                
                self.timestamps.append(data['timestamp'])
                self.price_history.append(data['price'])
                self.profit_history.append(data['profit'])
                self.current_price = data['price']
                self.baseline_price = data['baseline']
                self.total_profit = data['profit']
                self.grid_levels = data['grid_levels']
                self.active_positions = data['positions']
                
                updated = True
            except queue.Empty:
                break
        
        return updated
    
    def draw_background(self):
        """배경 그리기"""
        # 그라데이션 배경
        for y in range(self.height):
            color_ratio = y / self.height
            r = int(10 + color_ratio * 20)
            g = int(10 + color_ratio * 30)
            b = int(20 + color_ratio * 40)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
    
    def draw_chart_border(self, rect, title, color=COLORS['WHITE']):
        """차트 테두리 및 제목 그리기"""
        pygame.draw.rect(self.screen, color, rect, 2)
        
        # 제목 배경
        title_rect = pygame.Rect(rect.x, rect.y - 25, len(title) * 12, 25)
        pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], title_rect)
        
        # 제목 텍스트
        title_surface = self.font_medium.render(title, True, color)
        self.screen.blit(title_surface, (rect.x + 5, rect.y - 22))
    
    def draw_price_chart(self):
        """가격 차트 그리기"""
        rect = self.chart_areas['price_chart']
        self.draw_chart_border(rect, f"📈 {self.symbol} Price & Grid Levels", COLORS['CYAN'])
        
        if len(self.price_history) < 2:
            # 데이터 없음 표시
            text = self.font_medium.render("Waiting for price data...", True, COLORS['WHITE'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            return
        
        # 가격 범위 계산
        prices = list(self.price_history)
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = max_price * 0.01  # 1% 범위
        
        # 여백 추가
        margin = price_range * 0.1
        min_price -= margin
        max_price += margin
        price_range = max_price - min_price
        
        # 가격 라인 그리기
        points = []
        for i, price in enumerate(prices):
            x = rect.x + (i / (len(prices) - 1)) * rect.width
            y = rect.y + rect.height - ((price - min_price) / price_range) * rect.height
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, COLORS['CYAN'], False, points, 3)
        
        # 현재가 표시
        if self.current_price > 0:
            current_y = rect.y + rect.height - ((self.current_price - min_price) / price_range) * rect.height
            pygame.draw.line(self.screen, COLORS['YELLOW'], 
                           (rect.x, current_y), (rect.x + rect.width, current_y), 2)
            
            # 현재가 텍스트
            price_text = f"${self.current_price:,.0f}"
            text_surface = self.font_small.render(price_text, True, COLORS['YELLOW'])
            self.screen.blit(text_surface, (rect.x + rect.width - 100, current_y - 10))
        
        # 기준가 표시
        if self.baseline_price > 0 and min_price <= self.baseline_price <= max_price:
            baseline_y = rect.y + rect.height - ((self.baseline_price - min_price) / price_range) * rect.height
            pygame.draw.line(self.screen, COLORS['GOLD'], 
                           (rect.x, baseline_y), (rect.x + rect.width, baseline_y), 2)
        
        # 그리드 레벨 표시 (현재가 근처만)
        if self.grid_levels and self.current_price > 0:
            for level_data in self.grid_levels[:5]:  # 처음 5개 레벨만
                # 매수 레벨
                if min_price <= level_data['buy_entry'] <= max_price:
                    buy_y = rect.y + rect.height - ((level_data['buy_entry'] - min_price) / price_range) * rect.height
                    pygame.draw.line(self.screen, COLORS['GREEN'], 
                                   (rect.x, buy_y), (rect.x + rect.width, buy_y), 1)
                
                # 매도 레벨
                if min_price <= level_data['sell_entry'] <= max_price:
                    sell_y = rect.y + rect.height - ((level_data['sell_entry'] - min_price) / price_range) * rect.height
                    pygame.draw.line(self.screen, COLORS['RED'], 
                                   (rect.x, sell_y), (rect.x + rect.width, sell_y), 1)
        
        # Y축 라벨
        for i in range(5):
            y_pos = rect.y + (i / 4) * rect.height
            price_val = max_price - (i / 4) * price_range
            label = f"${price_val:,.0f}"
            text_surface = self.font_small.render(label, True, COLORS['WHITE'])
            self.screen.blit(text_surface, (rect.x - 80, y_pos - 8))
    
    def draw_profit_chart(self):
        """수익 차트 그리기"""
        rect = self.chart_areas['profit_chart']
        color = COLORS['GREEN'] if self.total_profit >= 0 else COLORS['RED']
        self.draw_chart_border(rect, f"💰 Profit History (${self.total_profit:+.2f})", color)
        
        if len(self.profit_history) < 2:
            text = self.font_medium.render("Waiting for profit data...", True, COLORS['WHITE'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            return
        
        # 수익 범위 계산
        profits = list(self.profit_history)
        min_profit = min(profits)
        max_profit = max(profits)
        profit_range = max_profit - min_profit
        
        if profit_range == 0:
            profit_range = max(abs(max_profit), abs(min_profit), 100) * 0.1
            min_profit = -profit_range / 2
            max_profit = profit_range / 2
        
        # 여백 추가
        margin = profit_range * 0.1
        min_profit -= margin
        max_profit += margin
        profit_range = max_profit - min_profit
        
        # 0선 그리기
        if min_profit <= 0 <= max_profit:
            zero_y = rect.y + rect.height - ((0 - min_profit) / profit_range) * rect.height
            pygame.draw.line(self.screen, COLORS['WHITE'], 
                           (rect.x, zero_y), (rect.x + rect.width, zero_y), 1)
        
        # 수익 라인 그리기
        points = []
        for i, profit in enumerate(profits):
            x = rect.x + (i / (len(profits) - 1)) * rect.width
            y = rect.y + rect.height - ((profit - min_profit) / profit_range) * rect.height
            points.append((x, y))
        
        if len(points) > 1:
            line_color = COLORS['GREEN'] if profits[-1] >= 0 else COLORS['RED']
            pygame.draw.lines(self.screen, line_color, False, points, 3)
            
            # 영역 채우기
            if min_profit <= 0 <= max_profit:
                zero_y = rect.y + rect.height - ((0 - min_profit) / profit_range) * rect.height
                fill_points = points + [(rect.x + rect.width, zero_y), (rect.x, zero_y)]
                
                # 반투명 색상으로 채우기
                fill_color = (*line_color[:3], 50)  # 알파값 추가
                fill_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.polygon(fill_surface, fill_color, 
                                  [(p[0] - rect.x, p[1] - rect.y) for p in fill_points])
                self.screen.blit(fill_surface, rect)
        
        # Y축 라벨
        for i in range(5):
            y_pos = rect.y + (i / 4) * rect.height
            profit_val = max_profit - (i / 4) * profit_range
            label = f"${profit_val:+.0f}"
            text_surface = self.font_small.render(label, True, COLORS['WHITE'])
            self.screen.blit(text_surface, (rect.x - 60, y_pos - 8))
    
    def draw_positions(self):
        """활성 포지션 표시"""
        rect = self.chart_areas['positions']
        self.draw_chart_border(rect, f"📊 Active Positions ({len(self.active_positions)})", COLORS['BLUE'])
        
        if not self.active_positions:
            text = self.font_medium.render("No Active Positions", True, COLORS['WHITE'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            return
        
        # 포지션별 정보 표시
        y_offset = rect.y + 20
        buy_positions = [p for p in self.active_positions if p['type'] == 'BUY']
        sell_positions = [p for p in self.active_positions if p['type'] == 'SELL']
        
        # 매수 포지션
        if buy_positions:
            buy_profit = sum(p['profit'] for p in buy_positions)
            color = COLORS['GREEN'] if buy_profit >= 0 else COLORS['RED']
            
            text = f"🔵 BUY Positions: {len(buy_positions)} | P&L: ${buy_profit:+.2f}"
            text_surface = self.font_medium.render(text, True, color)
            self.screen.blit(text_surface, (rect.x + 10, y_offset))
            y_offset += 30
            
            # 개별 포지션 (최대 5개)
            for i, pos in enumerate(buy_positions[:5]):
                pos_text = f"  #{pos['ticket']} | Entry: ${pos['entry_price']:.0f} | P&L: ${pos['profit']:+.2f}"
                pos_surface = self.font_small.render(pos_text, True, COLORS['LIGHT_GRAY'])
                self.screen.blit(pos_surface, (rect.x + 20, y_offset))
                y_offset += 20
        
        # 매도 포지션
        if sell_positions:
            sell_profit = sum(p['profit'] for p in sell_positions)
            color = COLORS['GREEN'] if sell_profit >= 0 else COLORS['RED']
            
            text = f"🔴 SELL Positions: {len(sell_positions)} | P&L: ${sell_profit:+.2f}"
            text_surface = self.font_medium.render(text, True, color)
            self.screen.blit(text_surface, (rect.x + 10, y_offset))
            y_offset += 30
            
            # 개별 포지션 (최대 5개)
            for i, pos in enumerate(sell_positions[:5]):
                pos_text = f"  #{pos['ticket']} | Entry: ${pos['entry_price']:.0f} | P&L: ${pos['profit']:+.2f}"
                pos_surface = self.font_small.render(pos_text, True, COLORS['LIGHT_GRAY'])
                self.screen.blit(pos_surface, (rect.x + 20, y_offset))
                y_offset += 20
    
    def draw_grid_levels(self):
        """그리드 레벨 정보 표시"""
        rect = self.chart_areas['levels']
        self.draw_chart_border(rect, "🎯 Grid Levels", COLORS['PURPLE'])
        
        if not self.grid_levels:
            text = self.font_medium.render("No Grid Levels", True, COLORS['WHITE'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            return
        
        # 그리드 레벨 정보 (처음 8개만)
        y_offset = rect.y + 20
        for i, level in enumerate(self.grid_levels[:8]):
            level_text = f"L{i+1} {level['name']}: Buy ${level['buy_entry']:.0f} | Sell ${level['sell_entry']:.0f}"
            
            # 레벨별 색상
            if level['distance_pct'] < 0.05:
                color = COLORS['CYAN']  # 단기
            elif level['distance_pct'] < 0.2:
                color = COLORS['YELLOW']  # 중기
            else:
                color = COLORS['ORANGE']  # 장기
            
            level_surface = self.font_small.render(level_text, True, color)
            self.screen.blit(level_surface, (rect.x + 10, y_offset))
            y_offset += 25
    
    def draw_status_bar(self):
        """상태 바 그리기"""
        rect = self.chart_areas['status']
        self.draw_chart_border(rect, "📊 System Status", COLORS['GOLD'])
        
        # 현재 시간
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_text = f"🕐 {current_time}"
        time_surface = self.font_medium.render(time_text, True, COLORS['WHITE'])
        self.screen.blit(time_surface, (rect.x + 10, rect.y + 20))
        
        # 현재가 정보
        if self.current_price > 0:
            price_text = f"💰 BTC: ${self.current_price:,.2f}"
            price_surface = self.font_medium.render(price_text, True, COLORS['CYAN'])
            self.screen.blit(price_surface, (rect.x + 300, rect.y + 20))
        
        # 기준가 정보
        if self.baseline_price > 0:
            baseline_text = f"🎯 Baseline: ${self.baseline_price:,.2f}"
            baseline_surface = self.font_medium.render(baseline_text, True, COLORS['GOLD'])
            self.screen.blit(baseline_surface, (rect.x + 600, rect.y + 20))
        
        # 총 수익
        profit_color = COLORS['GREEN'] if self.total_profit >= 0 else COLORS['RED']
        profit_text = f"💎 Total P&L: ${self.total_profit:+.2f}"
        profit_surface = self.font_medium.render(profit_text, True, profit_color)
        self.screen.blit(profit_surface, (rect.x + 900, rect.y + 20))
        
        # 포지션 수
        pos_text = f"📊 Positions: {len(self.active_positions)}"
        pos_surface = self.font_medium.render(pos_text, True, COLORS['BLUE'])
        self.screen.blit(pos_surface, (rect.x + 1200, rect.y + 20))
        
        # 애니메이션 효과 (펄스)
        pulse = abs(math.sin(self.animation_time * 2)) * 0.3 + 0.7
        pulse_color = (int(COLORS['GOLD'][0] * pulse), 
                      int(COLORS['GOLD'][1] * pulse), 
                      int(COLORS['GOLD'][2] * pulse))
        
        status_text = "🚀 GRID SYSTEM ACTIVE"
        status_surface = self.font_large.render(status_text, True, pulse_color)
        self.screen.blit(status_surface, (rect.x + 10, rect.y + 60))
        
        # 시스템 정보
        info_lines = [
            "🎮 Controls: ESC to exit, SPACE to pause",
            "📈 Real-time grid trading visualization",
            "💡 Multi-level unlimited profit system"
        ]
        
        for i, line in enumerate(info_lines):
            info_surface = self.font_small.render(line, True, COLORS['LIGHT_GRAY'])
            self.screen.blit(info_surface, (rect.x + 10, rect.y + 100 + i * 20))
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    # 일시정지 기능 (향후 구현)
                    pass
        
        return True
    
    def run(self):
        """메인 실행 루프"""
        clock = pygame.time.Clock()
        
        print("🎮 Pygame 시각화 시작!")
        print("🎮 Controls:")
        print("  - ESC: 종료")
        print("  - SPACE: 일시정지 (향후 구현)")
        
        while self.running:
            # 이벤트 처리
            if not self.handle_events():
                break
            
            # 데이터 업데이트
            self.update_data()
            
            # 애니메이션 시간 업데이트
            current_time = time.time()
            self.animation_time += current_time - self.last_update
            self.last_update = current_time
            
            # 화면 그리기
            self.draw_background()
            self.draw_price_chart()
            self.draw_profit_chart()
            self.draw_positions()
            self.draw_grid_levels()
            self.draw_status_bar()
            
            # 화면 업데이트
            pygame.display.flip()
            clock.tick(30)  # 30 FPS
        
        pygame.quit()
        print("🎮 Pygame 시각화 종료")

# 테스트용 함수
def test_visualizer():
    """시각화 테스트"""
    import random
    
    viz = PygameGridVisualizer()
    
    # 테스트 데이터 생성 스레드
    def generate_test_data():
        base_price = 70000
        profit = 0
        
        # 가짜 그리드 레벨 생성
        grid_levels = []
        for i in range(10):
            distance_pct = 0.01 * (i + 1)
            distance = base_price * distance_pct
            grid_levels.append({
                'name': f'Level{i+1}',
                'distance_pct': distance_pct,
                'buy_entry': base_price - distance,
                'sell_entry': base_price + distance,
                'buy_profit': distance * 0.01,
                'sell_profit': distance * 0.01
            })
        
        while viz.running:
            # 랜덤 가격 변동
            base_price += random.uniform(-500, 500)
            profit += random.uniform(-10, 10)
            
            # 가짜 포지션 생성
            positions = []
            if random.random() > 0.7:  # 30% 확률로 포지션 생성
                for _ in range(random.randint(1, 3)):
                    pos_type = random.choice(['BUY', 'SELL'])
                    entry_price = base_price + random.uniform(-1000, 1000)
                    current_profit = random.uniform(-50, 50)
                    
                    positions.append({
                        'ticket': random.randint(100000, 999999),
                        'type': pos_type,
                        'entry_price': entry_price,
                        'current_price': base_price,
                        'volume': 0.01,
                        'profit': current_profit
                    })
            
            # 데이터 추가
            viz.add_data(base_price, profit, 70000, grid_levels, positions)
            
            time.sleep(1)  # 1초마다 업데이트
    
    # 데이터 생성 스레드 시작
    data_thread = threading.Thread(target=generate_test_data, daemon=True)
    data_thread.start()
    
    # 시각화 실행
    viz.run()

if __name__ == "__main__":
    test_visualizer()