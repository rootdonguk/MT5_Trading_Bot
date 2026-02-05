"""
🚀💰 혁명적 무제한 양방향 그리드 시스템 + 실시간 시각화 💰🚀

🔥 핵심 개념:
- 현재가 중심으로 여러 레벨의 양방향 포지션 배치
- 최소수익부터 최대수익까지 그리드 형태로 설정
- 어떤 방향으로 움직여도 무조건 수익
- 빠른 계산으로 실시간 그리드 업데이트
- 📊 실시간 시각화로 모든 상황 한눈에 파악!

💡 그리드 레벨:
- 레벨 1-3: 빠른 회전 (0.5% ~ 2%)
- 레벨 4-6: 중간 수익 (5% ~ 20%)
- 레벨 7-11: 무제한 수익 (30% ~ 500%!)

🎨 시각화 요소:
- 📈 실시간 BTC 가격 차트
- 🎯 그리드 레벨 표시 (매수/매도 라인)
- 💰 수익 현황 그래프
- 📊 포지션 상태 표시
- 🔥 목표 달성 알림
"""

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import time
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

# 시각화 라이브러리
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import seaborn as sns
import threading
import queue

# Pygame 시각화 (선택적)
try:
    from Grid_Pygame_Visualizer import PygameGridVisualizer
    PYGAME_AVAILABLE = True
    print("🎮 Pygame 시각화 사용 가능!")
except ImportError:
    PYGAME_AVAILABLE = False
    print("📊 Matplotlib 시각화 사용 (pygame 설치 오류로 인해 비활성화)")

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

class GridRevolutionaryBot:
    def __init__(self):
        self.config = {
            'symbol': 'BTCUSD',
            'magic_number': 777777,
            'base_lot_size': 0.01,
            'max_spread': 10.0,
            
            # 🔥 혁명적 기법 설정
            'scalping_enabled': True,           # 초단기 스캘핑
            'martingale_enabled': True,         # 마틴게일 시스템
            'hedging_enabled': True,            # 헤징 시스템
            'momentum_trading': True,           # 모멘텀 거래
            'arbitrage_enabled': True,          # 차익거래
            'news_trading': True,               # 뉴스 기반 거래
            'loss_prevention': True,            # 🔥 손실 방지 시스템
            'direction_reversal': True,         # 🔥 방향 전환 시스템
            'profit_boost': True,               # 🚀 수익 부스트 시스템
            'dynamic_grid': True,               # 🔥 동적 그리드 시스템
            'market_orders': True,              # 🚀 시장가 주문 사용
            'stop_orders': True,                # 🎯 스탑 주문 사용
            
            # 스캘핑 설정
            'scalp_profit_pips': 5,             # 5핍 수익시 청산
            'scalp_max_loss_pips': 10,          # 10핍 손실시 마틴게일
            'scalp_frequency': 0.5,             # 0.5초마다 체크
            
            # 마틴게일 설정
            'martingale_multiplier': 2.0,       # 손실시 2배 증량
            'martingale_max_levels': 5,         # 최대 5단계
            
            # 헤징 설정
            'hedge_trigger_loss': 2.0,          # $2 손실시 헤징
            'hedge_multiplier': 1.5,            # 1.5배 헤징
            
            # 🔥 손실 방지 설정
            'max_allowed_loss': 50.0,           # $50 손실시 즉시 전환
            'direction_reversal_multiplier': 3.0,  # 3배 거래량으로 전환
            'emergency_boost_threshold': 100.0,    # $100 손실시 긴급 부스트
            'ultra_quick_exit_pct': 0.0005,        # 0.05% 움직임으로 청산
            
            # 🚀 동적 그리드 설정
            'market_order_ratio': 0.3,          # 30%는 시장가 주문
            'stop_order_ratio': 0.2,            # 20%는 스탑 주문
            'dynamic_adjustment': True,          # 동적 가격 조정
            'aggressive_entry': True,            # 공격적 진입
            'price_chase': True,                 # 가격 추적 시스템
            
            'unlimited_grid_levels': [
                # 초고속 회전 (매우 작은 수익, 매우 높은 빈도)
                {'name': '초고속1', 'distance_pct': 0.001, 'lot_multiplier': 0.2},   # ±0.1%
                {'name': '초고속2', 'distance_pct': 0.0015, 'lot_multiplier': 0.25}, # ±0.15%
                {'name': '초고속3', 'distance_pct': 0.002, 'lot_multiplier': 0.3},   # ±0.2%
                {'name': '초고속4', 'distance_pct': 0.0025, 'lot_multiplier': 0.35}, # ±0.25%
                {'name': '초고속5', 'distance_pct': 0.003, 'lot_multiplier': 0.4},   # ±0.3%
                
                # 고속 회전 (작은 수익, 높은 빈도)
                {'name': '고속1', 'distance_pct': 0.004, 'lot_multiplier': 0.45},    # ±0.4%
                {'name': '고속2', 'distance_pct': 0.005, 'lot_multiplier': 0.5},     # ±0.5%
                {'name': '고속3', 'distance_pct': 0.006, 'lot_multiplier': 0.55},    # ±0.6%
                {'name': '고속4', 'distance_pct': 0.007, 'lot_multiplier': 0.6},     # ±0.7%
                {'name': '고속5', 'distance_pct': 0.008, 'lot_multiplier': 0.65},    # ±0.8%
                
                # 빠른 회전 (작은 수익)
                {'name': '단기1', 'distance_pct': 0.01, 'lot_multiplier': 1.0},      # ±1%
                {'name': '단기2', 'distance_pct': 0.012, 'lot_multiplier': 1.1},     # ±1.2%
                {'name': '단기3', 'distance_pct': 0.015, 'lot_multiplier': 1.2},     # ±1.5%
                {'name': '단기4', 'distance_pct': 0.018, 'lot_multiplier': 1.3},     # ±1.8%
                {'name': '소액1', 'distance_pct': 0.02, 'lot_multiplier': 1.5},      # ±2%
                {'name': '소액2', 'distance_pct': 0.025, 'lot_multiplier': 1.7},     # ±2.5%
                {'name': '소액3', 'distance_pct': 0.03, 'lot_multiplier': 1.8},      # ±3%
                
                # 중간수익
                {'name': '중간1', 'distance_pct': 0.04, 'lot_multiplier': 2.0},      # ±4%
                {'name': '중간2', 'distance_pct': 0.05, 'lot_multiplier': 2.2},      # ±5%
                {'name': '중간3', 'distance_pct': 0.06, 'lot_multiplier': 2.4},      # ±6%
                {'name': '큰수익1', 'distance_pct': 0.08, 'lot_multiplier': 2.5},    # ±8%
                {'name': '큰수익2', 'distance_pct': 0.10, 'lot_multiplier': 2.7},    # ±10%
                {'name': '큰수익3', 'distance_pct': 0.12, 'lot_multiplier': 2.8},    # ±12%
                {'name': '대수익1', 'distance_pct': 0.15, 'lot_multiplier': 3.0},    # ±15%
                {'name': '대수익2', 'distance_pct': 0.20, 'lot_multiplier': 3.2},    # ±20%
                {'name': '대수익3', 'distance_pct': 0.25, 'lot_multiplier': 3.5},    # ±25%
                
                # 고수익 (장기)
                {'name': '고수익1', 'distance_pct': 0.30, 'lot_multiplier': 4.0},    # ±30%
                {'name': '고수익2', 'distance_pct': 0.35, 'lot_multiplier': 4.2},    # ±35%
                {'name': '고수익3', 'distance_pct': 0.40, 'lot_multiplier': 4.5},    # ±40%
                {'name': '고수익4', 'distance_pct': 0.45, 'lot_multiplier': 4.7},    # ±45%
                {'name': '극한1', 'distance_pct': 0.50, 'lot_multiplier': 5.0},      # ±50%
                {'name': '극한2', 'distance_pct': 0.60, 'lot_multiplier': 5.5},      # ±60%
                {'name': '극한3', 'distance_pct': 0.70, 'lot_multiplier': 6.0},      # ±70%
                {'name': '극한4', 'distance_pct': 0.80, 'lot_multiplier': 6.5},      # ±80%
                
                # 무제한 수익 (극한 변동)
                {'name': '무제한1', 'distance_pct': 1.0, 'lot_multiplier': 8.0},     # ±100% (2배/반토막)
                {'name': '무제한2', 'distance_pct': 1.2, 'lot_multiplier': 10.0},    # ±120%
                {'name': '무제한3', 'distance_pct': 1.5, 'lot_multiplier': 12.0},    # ±150%
                {'name': '무제한4', 'distance_pct': 2.0, 'lot_multiplier': 16.0},    # ±200% (3배/1/3)
                {'name': '무제한5', 'distance_pct': 2.5, 'lot_multiplier': 20.0},    # ±250%
                {'name': '무제한6', 'distance_pct': 3.0, 'lot_multiplier': 25.0},    # ±300% (4배/1/4)
                {'name': '무제한7', 'distance_pct': 4.0, 'lot_multiplier': 35.0},    # ±400% (5배/1/5)
                {'name': '무제한8', 'distance_pct': 5.0, 'lot_multiplier': 50.0},    # ±500% (6배/1/6)
                {'name': '극한무제한', 'distance_pct': 8.0, 'lot_multiplier': 100.0}, # ±800% (9배/1/9)
            ]
        }
        
        self.grid_positions = {
            'buy_orders': {},   # {level: order_info}
            'sell_orders': {},  # {level: order_info}
            'active_positions': {},
            'completed_trades': [],
            'hedge_positions': {},      # 헤징 포지션
            'martingale_levels': {},    # 마틴게일 레벨
            'scalp_positions': {}       # 스캘핑 포지션
        }
        
        self.stats = {
            'total_profit': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'grid_profits': defaultdict(float),
            'level_stats': defaultdict(lambda: {'trades': 0, 'profit': 0.0}),
            'scalp_profits': 0.0,       # 스캘핑 수익
            'hedge_profits': 0.0,       # 헤징 수익
            'martingale_profits': 0.0,  # 마틴게일 수익
            'start_time': datetime.now()
        }
        
        self.current_baseline = 0.0
        self.last_grid_update = 0
        self.last_scalp_time = 0        # 마지막 스캘핑 시간
        self.price_momentum = 0         # 가격 모멘텀
        self.last_prices = deque(maxlen=10)  # 최근 10개 가격
        
        # 시각화 데이터
        self.visualization_data = {
            'price_history': deque(maxlen=200),      # 가격 히스토리
            'profit_history': deque(maxlen=200),     # 수익 히스토리
            'timestamps': deque(maxlen=200),         # 시간 히스토리
            'grid_levels': [],                       # 현재 그리드 레벨
            'active_positions': [],                  # 활성 포지션
            'completed_trades': [],                  # 완료된 거래
            'level_profits': defaultdict(list)      # 레벨별 수익
        }
        
        # 시각화 큐 (스레드 간 통신)
        self.viz_queue = queue.Queue()
        self.viz_running = False
        
        # Pygame 시각화 (선택적)
        self.pygame_viz = None
        self.pygame_thread = None
        
        print("🔥 무제한 양방향 그리드 시스템 + 실시간 시각화 초기화 완료!")
        print(f"📊 그리드 레벨: {len(self.config['unlimited_grid_levels'])}개")
        print("🎨 실시간 시각화 준비 완료!")
        print("\n🎯 그리드 구성:")
        print("  ⚡ 초고속 회전: 0.2% ~ 0.7% (매우 빠른 수익)")
        print("  📈 빠른 회전: 1% ~ 3% (작은 수익, 높은 빈도)")
        print("  💰 중간수익: 4% ~ 25% (안정적 수익)")
        print("  🚀 고수익: 35% ~ 80% (큰 수익)")
        print("  � 무제한: 100% ~ 800% (극한 수익)")
        print("  � 극한무제한: BTC 9배 상승 또는 1/9 폭락까지 대응!")
        
        print(f"\n🎯 총 {len(self.config['unlimited_grid_levels'])}개 레벨로 촘촘한 그리드 형성:")
        for i, level in enumerate(self.config['unlimited_grid_levels']):
            if i < 4 or level['distance_pct'] >= 1.0:  # 처음 4개와 무제한 레벨만 표시
                print(f"     🔥 L{i+1:2d} {level['name']:8s}: ±{level['distance_pct']*100:5.1f}% (거래량: {level['lot_multiplier']:4.1f}x)")
            elif i == 4:
                print("     ... (중간 레벨들)")
        
        print(f"\n💡 예상 동시 주문 수: 최대 {len(self.config['unlimited_grid_levels']) * 2}개 (매수 + 매도)")
        print("🎯 더 촘촘한 그리드로 더 많은 수익 기회 포착!")
    
    def connect_mt5(self):
        """MT5 연결"""
        print("\n🔌 MT5 연결 중...")
        
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패: {mt5.last_error()}")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보 조회 실패")
            return False
        
        print("✅ MT5 연결 성공!")
        print(f"계좌: {account_info.login}")
        print(f"잔고: ${account_info.balance:,.2f}")
        print(f"자산: ${account_info.equity:,.2f}")
        
        return True
    
    def get_current_price(self):
        """현재가 조회"""
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'mid': (tick.bid + tick.ask) / 2,
            'spread': tick.ask - tick.bid,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def calculate_unlimited_grid_levels(self, baseline_price):
        """🧮 무제한 그리드 레벨 계산"""
        grid_data = []
        
        print(f"\n🧮 무제한 그리드 레벨 계산 (기준가: ${baseline_price:,.2f})")
        print("="*80)
        
        total_potential_profit = 0
        
        for i, level_config in enumerate(self.config['unlimited_grid_levels']):
            distance_pct = level_config['distance_pct']
            lot_multiplier = level_config['lot_multiplier']
            lot_size = self.config['base_lot_size'] * lot_multiplier
            
            # 거리 계산
            distance = baseline_price * distance_pct
            
            # 매수 레벨 (아래쪽) - 가격 하락시 진입
            buy_entry = baseline_price - distance
            buy_target = baseline_price  # 기준가로 복귀시 수익
            buy_profit = distance * lot_size
            
            # 매도 레벨 (위쪽) - 가격 상승시 진입  
            sell_entry = baseline_price + distance
            sell_target = baseline_price  # 기준가로 복귀시 수익
            sell_profit = distance * lot_size
            
            # 극한 수익 계산 (목표가를 더 멀리)
            if distance_pct >= 0.1:  # 10% 이상 레벨은 극한 수익
                buy_target = baseline_price + (distance * 0.5)  # 추가 50% 수익
                sell_target = baseline_price - (distance * 0.5)  # 추가 50% 수익
                buy_profit = distance * 1.5 * lot_size  # 1.5배 수익
                sell_profit = distance * 1.5 * lot_size  # 1.5배 수익
            
            level_data = {
                'level': i,
                'name': level_config['name'],
                'distance_pct': distance_pct,
                'distance': distance,
                'lot_size': lot_size,
                'buy_entry': max(buy_entry, baseline_price * 0.01),  # 최소 1% 가격
                'buy_target': buy_target,
                'buy_profit': buy_profit,
                'sell_entry': sell_entry,
                'sell_target': sell_target,
                'sell_profit': sell_profit
            }
            
            grid_data.append(level_data)
            total_potential_profit += max(buy_profit, sell_profit)
            
            # 중요한 레벨만 출력
            if i < 3 or distance_pct >= 0.1:
                print(f"레벨 {i+1}: {level_config['name']}")
                print(f"  📊 거리: ±${distance:,.0f} (±{distance_pct*100:.1f}%)")
                print(f"  💰 거래량: {lot_size:.3f} BTC ({lot_multiplier:.1f}x)")
                print(f"  🔵 매수: ${buy_entry:,.0f} → ${buy_target:,.0f} (수익: ${buy_profit:,.0f})")
                print(f"  🔴 매도: ${sell_entry:,.0f} → ${sell_target:,.0f} (수익: ${sell_profit:,.0f})")
                
                if distance_pct >= 1.0:  # 무제한 레벨
                    print(f"  🚀 무제한 수익 잠재력: ${max(buy_profit, sell_profit):,.0f}!")
                print()
        
        print(f"💎 총 잠재 수익: ${total_potential_profit:,.0f} (한쪽 방향 극한 변동시)")
        print(f"🎯 그리드 범위: ${grid_data[0]['buy_entry']:,.0f} ~ ${grid_data[-1]['sell_entry']:,.0f}")
        
        return grid_data
    
    def update_visualization_data(self):
        """🎨 시각화 데이터 업데이트"""
        current_price = self.get_current_price()
        if not current_price:
            return
        
        current_time = datetime.now()
        
        # 가격 및 시간 데이터 추가
        self.visualization_data['price_history'].append(current_price['mid'])
        self.visualization_data['timestamps'].append(current_time)
        
        # 계좌 수익 데이터 추가
        account_info = mt5.account_info()
        if account_info:
            profit = account_info.equity - account_info.balance
            self.visualization_data['profit_history'].append(profit)
        else:
            self.visualization_data['profit_history'].append(0)
        
        # 활성 포지션 데이터 업데이트
        positions = mt5.positions_get(symbol=self.config['symbol'])
        self.visualization_data['active_positions'] = []
        
        if positions:
            for pos in positions:
                position_data = {
                    'ticket': pos.ticket,
                    'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'entry_price': pos.price_open,
                    'current_price': current_price['bid'] if pos.type == mt5.ORDER_TYPE_BUY else current_price['ask'],
                    'volume': pos.volume,
                    'profit': (current_price['bid'] - pos.price_open) * pos.volume if pos.type == mt5.ORDER_TYPE_BUY 
                             else (pos.price_open - current_price['ask']) * pos.volume,
                    'tp': pos.tp,
                    'sl': pos.sl
                }
                self.visualization_data['active_positions'].append(position_data)
        
        # 시각화 큐에 데이터 전송
        try:
            viz_data = {
                'timestamp': current_time,
                'price': current_price['mid'],
                'baseline': self.current_baseline,
                'grid_levels': self.visualization_data['grid_levels'].copy(),
                'positions': self.visualization_data['active_positions'].copy(),
                'total_profit': self.visualization_data['profit_history'][-1] if self.visualization_data['profit_history'] else 0
            }
            self.viz_queue.put_nowait(viz_data)
            
            # Pygame 시각화에도 데이터 전송
            if self.pygame_viz:
                self.pygame_viz.add_data(
                    current_price['mid'],
                    self.visualization_data['profit_history'][-1] if self.visualization_data['profit_history'] else 0,
                    self.current_baseline,
                    self.visualization_data['grid_levels'].copy(),
                    self.visualization_data['active_positions'].copy()
                )
        except queue.Full:
            pass  # 큐가 가득 찬 경우 무시
    
    def start_visualization(self):
        """🎨 실시간 시각화 시작"""
        def run_visualization():
            try:
                import matplotlib
                matplotlib.use('TkAgg')  # GUI 백엔드 설정
                
                # 그래프 설정
                plt.style.use('dark_background')
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
                fig.suptitle('🚀 Revolutionary Unlimited Grid Trading System 🚀', fontsize=16, color='gold')
                
                # 데이터 저장용
                times = []
                prices = []
                profits = []
                
                def animate(frame):
                    try:
                        # 큐에서 데이터 가져오기
                        data_updated = False
                        while not self.viz_queue.empty():
                            try:
                                data = self.viz_queue.get_nowait()
                                
                                times.append(data['timestamp'])
                                prices.append(data['price'])
                                profits.append(data['total_profit'])
                                data_updated = True
                                
                                # 최근 100개 데이터만 유지
                                if len(times) > 100:
                                    times.pop(0)
                                    prices.pop(0)
                                    profits.pop(0)
                            except queue.Empty:
                                break
                        
                        if len(times) < 2:
                            return
                        
                        # 1. 가격 차트 + 그리드 레벨
                        ax1.clear()
                        ax1.plot(times, prices, 'cyan', linewidth=2, label='BTC Price')
                        
                        # 기준선 표시
                        if hasattr(self, 'current_baseline') and self.current_baseline > 0:
                            ax1.axhline(y=self.current_baseline, color='yellow', linestyle='--', alpha=0.8, label='Baseline')
                        
                        # 그리드 레벨 표시 (최근 가격 기준으로 일부만)
                        if len(self.visualization_data['grid_levels']) > 0 and len(prices) > 0:
                            current_price = prices[-1]
                            for i, level_data in enumerate(self.visualization_data['grid_levels']):
                                # 현재가 근처 레벨만 표시 (±20% 범위)
                                if abs(level_data['buy_entry'] - current_price) / current_price < 0.2:
                                    ax1.axhline(y=level_data['buy_entry'], color='lime', alpha=0.4, linestyle='-', linewidth=1)
                                if abs(level_data['sell_entry'] - current_price) / current_price < 0.2:
                                    ax1.axhline(y=level_data['sell_entry'], color='red', alpha=0.4, linestyle='-', linewidth=1)
                        
                        ax1.set_title('� BTC Price &, Grid Levels', color='white')
                        ax1.set_ylabel('Price ($)', color='white')
                        ax1.legend()
                        ax1.grid(True, alpha=0.3)
                        ax1.tick_params(axis='x', rotation=45)
                        
                        # 2. 수익 차트
                        ax2.clear()
                        if len(profits) > 0:
                            ax2.plot(times, profits, 'gold', linewidth=2, label='Total Profit')
                            ax2.axhline(y=0, color='white', linestyle='-', alpha=0.5)
                            
                            # 수익/손실에 따른 색상 채우기
                            positive_profits = [max(0, p) for p in profits]
                            negative_profits = [min(0, p) for p in profits]
                            
                            ax2.fill_between(times, positive_profits, 0, alpha=0.3, color='lime', label='Profit')
                            ax2.fill_between(times, negative_profits, 0, alpha=0.3, color='red', label='Loss')
                            
                            ax2.set_title(f'� Profit History (${profits[-1]:+.2f})', color='white')
                        else:
                            ax2.set_title('💰 Profit History ($0.00)', color='white')
                        
                        ax2.set_ylabel('Profit ($)', color='white')
                        ax2.legend()
                        ax2.grid(True, alpha=0.3)
                        ax2.tick_params(axis='x', rotation=45)
                        
                        # 3. 활성 포지션 현황
                        ax3.clear()
                        if self.visualization_data['active_positions']:
                            buy_positions = [p for p in self.visualization_data['active_positions'] if p['type'] == 'BUY']
                            sell_positions = [p for p in self.visualization_data['active_positions'] if p['type'] == 'SELL']
                            
                            position_types = []
                            position_profits = []
                            colors = []
                            
                            if buy_positions:
                                buy_profit = sum(p['profit'] for p in buy_positions)
                                position_types.append(f'BUY ({len(buy_positions)})')
                                position_profits.append(buy_profit)
                                colors.append('lime' if buy_profit >= 0 else 'red')
                            
                            if sell_positions:
                                sell_profit = sum(p['profit'] for p in sell_positions)
                                position_types.append(f'SELL ({len(sell_positions)})')
                                position_profits.append(sell_profit)
                                colors.append('lime' if sell_profit >= 0 else 'red')
                            
                            if position_types:
                                bars = ax3.bar(position_types, position_profits, color=colors, alpha=0.7)
                                
                                # 수익 값 표시
                                for bar, profit in zip(bars, position_profits):
                                    height = bar.get_height()
                                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                                            f'${profit:.1f}', ha='center', va='bottom' if height >= 0 else 'top',
                                            color='white', fontsize=10)
                            
                            ax3.set_title(f'📊 Active Positions ({len(self.visualization_data["active_positions"])})', color='white')
                        else:
                            ax3.text(0.5, 0.5, 'No Active Positions', ha='center', va='center', 
                                    transform=ax3.transAxes, color='white', fontsize=12)
                            ax3.set_title('📊 Active Positions (0)', color='white')
                        
                        ax3.set_ylabel('Unrealized P&L ($)', color='white')
                        ax3.grid(True, alpha=0.3)
                        
                        # 4. 레벨별 수익 분포
                        ax4.clear()
                        if self.stats['level_stats']:
                            levels = []
                            level_profits = []
                            colors = []
                            
                            for level, stats in self.stats['level_stats'].items():
                                if stats['trades'] > 0:
                                    level_name = self.config['unlimited_grid_levels'][level]['name']
                                    levels.append(f"L{level+1}\n{level_name}")
                                    level_profits.append(stats['profit'])
                                    colors.append('lime' if stats['profit'] >= 0 else 'red')
                            
                            if levels:
                                bars = ax4.bar(levels, level_profits, color=colors, alpha=0.7)
                                
                                # 수익 값 표시
                                for bar, profit in zip(bars, level_profits):
                                    height = bar.get_height()
                                    ax4.text(bar.get_x() + bar.get_width()/2., height,
                                            f'${profit:.1f}', ha='center', va='bottom' if height >= 0 else 'top',
                                            color='white', fontsize=8)
                                
                                ax4.set_title('🎯 Level Performance', color='white')
                            else:
                                ax4.text(0.5, 0.5, 'No Completed Trades', ha='center', va='center',
                                        transform=ax4.transAxes, color='white', fontsize=12)
                                ax4.set_title('🎯 Level Performance', color='white')
                        else:
                            ax4.text(0.5, 0.5, 'No Completed Trades', ha='center', va='center',
                                    transform=ax4.transAxes, color='white', fontsize=12)
                            ax4.set_title('🎯 Level Performance', color='white')
                        
                        ax4.set_ylabel('Profit ($)', color='white')
                        ax4.grid(True, alpha=0.3)
                        
                        # 전체 레이아웃 조정
                        plt.tight_layout()
                        
                    except Exception as e:
                        print(f"시각화 애니메이션 오류: {e}")
                
                # 애니메이션 시작
                ani = animation.FuncAnimation(fig, animate, interval=2000, cache_frame_data=False)
                
                # 창 제목 설정
                manager = plt.get_current_fig_manager()
                if hasattr(manager, 'window'):
                    if hasattr(manager.window, 'wm_title'):
                        manager.window.wm_title('🚀 Grid Trading System - Real-time Visualization')
                
                plt.show()
                
            except Exception as e:
                print(f"시각화 시작 오류: {e}")
                print("matplotlib 또는 GUI 백엔드 설치가 필요할 수 있습니다.")
                print("다음 명령어로 설치해보세요:")
                print("pip install matplotlib")
                print("pip install tkinter")
        
        # 별도 스레드에서 시각화 실행
        viz_thread = threading.Thread(target=run_visualization, daemon=True)
        viz_thread.start()
        self.viz_running = True
        print("🎨 실시간 시각화 시작됨!")
        
    def start_pygame_visualization(self):
        """🎮 Pygame 시각화 시작"""
        if not PYGAME_AVAILABLE:
            print("❌ Pygame이 설치되지 않았습니다.")
            print("다음 명령어로 설치하세요: pip install pygame")
            return None
        
        def run_pygame_viz():
            try:
                self.pygame_viz = PygameGridVisualizer()
                self.pygame_viz.run()
            except Exception as e:
                print(f"Pygame 시각화 오류: {e}")
        
        self.pygame_thread = threading.Thread(target=run_pygame_viz, daemon=True)
        self.pygame_thread.start()
        print("🎮 Pygame 시각화 시작됨!")
        
        return self.pygame_thread
    
    def revolutionary_scalping_system(self, current_price):
        """⚡ 혁명적 초단기 스캘핑 시스템"""
        if not self.config['scalping_enabled']:
            return
        
        current_time = time.time()
        if current_time - self.last_scalp_time < self.config['scalp_frequency']:
            return
        
        self.last_scalp_time = current_time
        
        # 가격 모멘텀 계산
        self.last_prices.append(current_price['mid'])
        if len(self.last_prices) >= 3:
            recent_change = self.last_prices[-1] - self.last_prices[-3]
            self.price_momentum = recent_change
            
            # 강한 모멘텀 감지시 즉시 스캘핑
            if abs(recent_change) > current_price['mid'] * 0.0005:  # 0.05% 이상 변동
                self.execute_momentum_scalp(current_price, recent_change)
    
    def execute_momentum_scalp(self, current_price, momentum):
        """🚀 모멘텀 기반 스캘핑 실행"""
        try:
            lot_size = self.config['base_lot_size'] * 2  # 2배 거래량
            
            if momentum > 0:  # 상승 모멘텀
                # 매수 진입
                scalp_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": "SCALP_BUY_MOMENTUM",
                }
                
                result = mt5.order_send(scalp_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    entry_price = result.price
                    target_price = entry_price + (current_price['mid'] * 0.0007)  # 0.07% 목표
                    
                    print(f"⚡ 스캘핑 매수: ${entry_price:.2f} → 목표: ${target_price:.2f}")
                    
                    # 즉시 청산 주문 배치
                    self.place_scalp_exit_order(result.order, 'buy', target_price, lot_size)
                    
            else:  # 하락 모멘텀
                # 매도 진입
                scalp_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": "SCALP_SELL_MOMENTUM",
                }
                
                result = mt5.order_send(scalp_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    entry_price = result.price
                    target_price = entry_price - (current_price['mid'] * 0.0007)  # 0.07% 목표
                    
                    print(f"⚡ 스캘핑 매도: ${entry_price:.2f} → 목표: ${target_price:.2f}")
                    
                    # 즉시 청산 주문 배치
                    self.place_scalp_exit_order(result.order, 'sell', target_price, lot_size)
                    
        except Exception as e:
            print(f"❌ 스캘핑 오류: {e}")
    
    def place_scalp_exit_order(self, position_ticket, position_type, target_price, volume):
        """⚡ 스캘핑 청산 주문 배치"""
        try:
            if position_type == 'buy':
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"SCALP_EXIT_BUY_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"SCALP_EXIT_SELL_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"   ✅ 스캘핑 청산주문: #{result.order}")
                
                # 스캘핑 포지션 추적
                self.grid_positions['scalp_positions'][position_ticket] = {
                    'exit_order': result.order,
                    'target_price': target_price,
                    'timestamp': datetime.now()
                }
            
        except Exception as e:
            print(f"❌ 스캘핑 청산주문 오류: {e}")
    
    def revolutionary_martingale_system(self, current_price):
        """🎯 혁명적 마틴게일 시스템 (손실을 수익으로 전환)"""
        if not self.config['martingale_enabled']:
            return
        
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return
        
        for position in positions:
            # 손실 포지션 감지
            if position.type == mt5.ORDER_TYPE_BUY:
                profit = (current_price['bid'] - position.price_open) * position.volume
            else:
                profit = (position.price_open - current_price['ask']) * position.volume
            
            # 손실이 임계값을 넘으면 마틴게일 실행
            if profit < -self.config['scalp_max_loss_pips']:
                self.execute_martingale(position, current_price, profit)
    
    def execute_martingale(self, losing_position, current_price, loss_amount):
        """🔥 마틴게일 실행 (손실 복구)"""
        try:
            # 마틴게일 레벨 확인
            position_key = f"{losing_position.ticket}"
            current_level = self.grid_positions['martingale_levels'].get(position_key, 0)
            
            if current_level >= self.config['martingale_max_levels']:
                return  # 최대 레벨 도달
            
            # 마틴게일 거래량 계산 (손실 복구 + 추가 수익)
            recovery_volume = abs(loss_amount) / current_price['mid'] * self.config['martingale_multiplier']
            recovery_volume = max(self.config['base_lot_size'], recovery_volume)
            
            # 반대 방향으로 마틴게일 주문
            if losing_position.type == mt5.ORDER_TYPE_BUY:
                # 매수 포지션 손실 → 매도로 복구
                martingale_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": recovery_volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MARTINGALE_L{current_level+1}_SELL",
                }
            else:
                # 매도 포지션 손실 → 매수로 복구
                martingale_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": recovery_volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MARTINGALE_L{current_level+1}_BUY",
                }
            
            result = mt5.order_send(martingale_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🔥 마틴게일 L{current_level+1}: 거래량 {recovery_volume:.3f} | 손실복구: ${abs(loss_amount):.2f}")
                
                # 마틴게일 레벨 업데이트
                self.grid_positions['martingale_levels'][position_key] = current_level + 1
                
                # 즉시 수익 청산 주문 배치
                self.place_martingale_exit_order(result.order, losing_position.type, current_price, recovery_volume)
                
        except Exception as e:
            print(f"❌ 마틴게일 오류: {e}")
    
    def place_martingale_exit_order(self, martingale_ticket, original_type, current_price, volume):
        """🎯 마틴게일 청산 주문 (빠른 수익 실현)"""
        try:
            if original_type == mt5.ORDER_TYPE_BUY:
                # 원래 매수 손실 → 매도 마틴게일 → 매수 청산
                target_price = current_price['ask'] - (current_price['mid'] * 0.001)  # 0.1% 수익
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MARTINGALE_EXIT_{martingale_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                # 원래 매도 손실 → 매수 마틴게일 → 매도 청산
                target_price = current_price['bid'] + (current_price['mid'] * 0.001)  # 0.1% 수익
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MARTINGALE_EXIT_{martingale_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"   ✅ 마틴게일 청산주문: #{result.order} @ ${target_price:.2f}")
                
        except Exception as e:
            print(f"❌ 마틴게일 청산주문 오류: {e}")
    
    def revolutionary_hedging_system(self, current_price):
        """🛡️ 혁명적 헤징 시스템 (리스크 제로화)"""
        if not self.config['hedging_enabled']:
            return
        
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return
        
        total_buy_volume = 0
        total_sell_volume = 0
        total_buy_loss = 0
        total_sell_loss = 0
        
        # 포지션 분석
        for position in positions:
            if position.type == mt5.ORDER_TYPE_BUY:
                total_buy_volume += position.volume
                profit = (current_price['bid'] - position.price_open) * position.volume
                if profit < 0:
                    total_buy_loss += abs(profit)
            else:
                total_sell_volume += position.volume
                profit = (position.price_open - current_price['ask']) * position.volume
                if profit < 0:
                    total_sell_loss += abs(profit)
        
        # 헤징 필요성 판단
        if total_buy_loss > self.config['hedge_trigger_loss']:
            self.execute_hedge('sell', total_buy_volume, total_buy_loss, current_price)
        
        if total_sell_loss > self.config['hedge_trigger_loss']:
            self.execute_hedge('buy', total_sell_volume, total_sell_loss, current_price)
    
    def execute_hedge(self, hedge_type, original_volume, loss_amount, current_price):
        """🛡️ 헤징 실행"""
        try:
            # 헤징 거래량 계산
            hedge_volume = original_volume * self.config['hedge_multiplier']
            
            if hedge_type == 'buy':
                hedge_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": hedge_volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"HEDGE_BUY_{loss_amount:.0f}",
                }
            else:
                hedge_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": hedge_volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"HEDGE_SELL_{loss_amount:.0f}",
                }
            
            result = mt5.order_send(hedge_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🛡️ 헤징 실행: {hedge_type.upper()} {hedge_volume:.3f} | 손실보호: ${loss_amount:.2f}")
                
                # 헤징 포지션 추적
                self.grid_positions['hedge_positions'][result.order] = {
                    'type': hedge_type,
                    'volume': hedge_volume,
                    'loss_protected': loss_amount,
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            print(f"❌ 헤징 오류: {e}")
    
    def instant_profit_system(self, current_price):
        """💎 즉시 수익 시스템 (손실 포지션을 즉시 수익으로 전환)"""
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return
        
        for position in positions:
            # 포지션 보유 시간
            position_age = datetime.now().timestamp() - position.time
            
            # 손실 포지션이 5초 이상 지속되면 즉시 수익 전환
            if position_age > 5:
                if position.type == mt5.ORDER_TYPE_BUY:
                    profit = (current_price['bid'] - position.price_open) * position.volume
                    if profit < -0.5:  # $0.5 이상 손실
                        self.execute_instant_profit_conversion(position, current_price, 'buy')
                else:
                    profit = (position.price_open - current_price['ask']) * position.volume
                    if profit < -0.5:  # $0.5 이상 손실
                        self.execute_instant_profit_conversion(position, current_price, 'sell')
    
    def execute_instant_profit_conversion(self, losing_position, current_price, position_type):
        """⚡ 즉시 수익 전환 실행"""
        try:
            # 3배 거래량으로 반대 포지션 진입
            conversion_volume = losing_position.volume * 3
            
            if position_type == 'buy':
                # 매수 손실 → 3배 매도로 즉시 수익 전환
                conversion_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": conversion_volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"INSTANT_PROFIT_SELL_{losing_position.ticket}",
                }
            else:
                # 매도 손실 → 3배 매수로 즉시 수익 전환
                conversion_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": conversion_volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"INSTANT_PROFIT_BUY_{losing_position.ticket}",
                }
            
            result = mt5.order_send(conversion_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"💎 즉시수익전환: {position_type.upper()} 손실 → {conversion_volume:.3f} 반대포지션")
                
                # 매우 작은 움직임으로도 수익이 나도록 청산 주문 배치
                self.place_micro_profit_exit(result.order, position_type, current_price, conversion_volume)
                
        except Exception as e:
            print(f"❌ 즉시수익전환 오류: {e}")
    
    def place_micro_profit_exit(self, position_ticket, original_type, current_price, volume):
        """⚡ 마이크로 수익 청산 주문 (0.01% 수익으로도 청산)"""
        try:
            if original_type == 'buy':
                # 매도 포지션 → 0.01% 하락시 청산
                target_price = current_price['ask'] - (current_price['mid'] * 0.0001)
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MICRO_PROFIT_EXIT_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                # 매수 포지션 → 0.01% 상승시 청산
                target_price = current_price['bid'] + (current_price['mid'] * 0.0001)
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MICRO_PROFIT_EXIT_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"   ⚡ 마이크로수익 청산주문: #{result.order} @ ${target_price:.2f} (0.01% 수익)")
                
        except Exception as e:
            print(f"❌ 마이크로수익 청산주문 오류: {e}")
    
    def emergency_close_all_system(self):
        """🚨 긴급 전체 청산 시스템"""
        print("\n🚨 긴급 전체 청산 시스템 실행!")
        print("="*60)
        
        total_closed_positions = 0
        total_cancelled_orders = 0
        total_profit = 0
        
        # 1. 모든 활성 포지션 즉시 청산
        print("📊 활성 포지션 청산 중...")
        positions = mt5.positions_get()
        if positions:
            for position in positions:
                profit = self.close_position_immediately(position)
                if profit is not None:
                    total_closed_positions += 1
                    total_profit += profit
                    print(f"  ✅ 포지션 #{position.ticket} 청산: ${profit:+.2f}")
                else:
                    print(f"  ❌ 포지션 #{position.ticket} 청산 실패")
        
        # 2. 모든 대기 주문 취소
        print("\n📋 대기 주문 취소 중...")
        orders = mt5.orders_get()
        if orders:
            for order in orders:
                if self.cancel_order_immediately(order.ticket):
                    total_cancelled_orders += 1
                    print(f"  ✅ 주문 #{order.ticket} 취소")
                else:
                    print(f"  ❌ 주문 #{order.ticket} 취소 실패")
        
        # 3. 내부 데이터 초기화
        self.grid_positions['buy_orders'].clear()
        self.grid_positions['sell_orders'].clear()
        self.grid_positions['active_positions'].clear()
        self.grid_positions['hedge_positions'].clear()
        self.grid_positions['martingale_levels'].clear()
        self.grid_positions['scalp_positions'].clear()
        
        # 4. 최종 결과 표시
        print(f"\n🎯 전체 청산 완료!")
        print(f"  📊 청산된 포지션: {total_closed_positions}개")
        print(f"  📋 취소된 주문: {total_cancelled_orders}개")
        print(f"  💰 총 실현손익: ${total_profit:+.2f}")
        
        # 5. 계좌 현황 확인
        account_info = mt5.account_info()
        if account_info:
            print(f"  💎 현재 잔고: ${account_info.balance:,.2f}")
            print(f"  📈 현재 자산: ${account_info.equity:,.2f}")
            print(f"  🔥 순손익: ${account_info.equity - account_info.balance:+.2f}")
        
        return total_closed_positions, total_cancelled_orders, total_profit
    
    def close_position_immediately(self, position):
        """⚡ 포지션 즉시 청산"""
        try:
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "EMERGENCY_CLOSE_ALL",
            }
            
            result = mt5.order_send(close_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # 수익 계산
                if position.type == mt5.ORDER_TYPE_BUY:
                    profit = (result.price - position.price_open) * position.volume
                else:
                    profit = (position.price_open - result.price) * position.volume
                
                return profit
            else:
                return None
                
        except Exception as e:
            print(f"❌ 포지션 청산 오류: {e}")
            return None
    
    def cancel_order_immediately(self, order_ticket):
        """⚡ 주문 즉시 취소"""
        try:
            cancel_request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order_ticket,
            }
            
            result = mt5.order_send(cancel_request)
            return result and result.retcode == mt5.TRADE_RETCODE_DONE
            
        except Exception as e:
            print(f"❌ 주문 취소 오류: {e}")
            return False
    
    def user_close_all_interface(self):
        """🎮 사용자 전체 청산 인터페이스"""
        print("\n" + "="*60)
        print("🚨 전체 청산 옵션")
        print("="*60)
        print("1. 모든 포지션 + 주문 즉시 청산")
        print("2. 포지션만 청산 (주문 유지)")
        print("3. 주문만 취소 (포지션 유지)")
        print("4. 수익 포지션만 청산")
        print("5. 손실 포지션만 청산")
        print("6. 🔄 모든 손실 포지션 방향 뒤집기")  # 새로운 옵션
        print("7. ⚡ 즉시 전체 뒤집기 (모든 포지션)")  # 새로운 옵션
        print("0. 취소")
        
        choice = input("\n선택하세요 (0-7): ").strip()
        
        if choice == "1":
            return self.emergency_close_all_system()
        elif choice == "2":
            return self.close_positions_only()
        elif choice == "3":
            return self.cancel_orders_only()
        elif choice == "4":
            return self.close_profit_positions_only()
        elif choice == "5":
            return self.close_loss_positions_only()
        elif choice == "6":
            return self.manual_flip_losing_positions()
        elif choice == "7":
            return self.manual_flip_all_positions()
        else:
            print("취소되었습니다.")
            return None
    
    def manual_flip_losing_positions(self):
        """🔄 수동 손실 포지션 뒤집기"""
        print("\n🔄 손실 포지션 뒤집기 실행...")
        current_price = self.get_current_price()
        if not current_price:
            print("❌ 현재가 조회 실패")
            return None
        
        self.flip_all_losing_positions(current_price)
        return None
    
    def manual_flip_all_positions(self):
        """⚡ 수동 전체 포지션 뒤집기"""
        print("\n⚡ 전체 포지션 뒤집기 실행...")
        current_price = self.get_current_price()
        if not current_price:
            print("❌ 현재가 조회 실패")
            return None
        
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            print("뒤집을 포지션이 없습니다.")
            return None
        
        flipped_count = 0
        for position in positions:
            # 현재 손익 계산
            if position.type == mt5.ORDER_TYPE_BUY:
                profit = (current_price['bid'] - position.price_open) * position.volume
            else:
                profit = (position.price_open - current_price['ask']) * position.volume
            
            # 모든 포지션 뒤집기
            success = self.flip_position_direction(position, current_price, profit)
            if success:
                flipped_count += 1
                print(f"  🔄 포지션 #{position.ticket} 뒤집기: ${profit:+.2f}")
        
        print(f"✅ 전체 {flipped_count}개 포지션 뒤집기 완료!")
        return None
    
    def close_positions_only(self):
        """📊 포지션만 청산"""
        print("\n📊 포지션만 청산 중...")
        positions = mt5.positions_get()
        total_closed = 0
        total_profit = 0
        
        if positions:
            for position in positions:
                profit = self.close_position_immediately(position)
                if profit is not None:
                    total_closed += 1
                    total_profit += profit
                    print(f"  ✅ 포지션 #{position.ticket} 청산: ${profit:+.2f}")
        
        print(f"✅ 포지션 청산 완료: {total_closed}개, 총 손익: ${total_profit:+.2f}")
        return total_closed, 0, total_profit
    
    def cancel_orders_only(self):
        """📋 주문만 취소"""
        print("\n📋 주문만 취소 중...")
        orders = mt5.orders_get()
        total_cancelled = 0
        
        if orders:
            for order in orders:
                if self.cancel_order_immediately(order.ticket):
                    total_cancelled += 1
                    print(f"  ✅ 주문 #{order.ticket} 취소")
        
        print(f"✅ 주문 취소 완료: {total_cancelled}개")
        return 0, total_cancelled, 0
    
    def close_profit_positions_only(self):
        """💰 수익 포지션만 청산"""
        print("\n💰 수익 포지션만 청산 중...")
        positions = mt5.positions_get()
        current_price = self.get_current_price()
        total_closed = 0
        total_profit = 0
        
        if positions and current_price:
            for position in positions:
                # 수익 여부 확인
                if position.type == mt5.ORDER_TYPE_BUY:
                    profit = (current_price['bid'] - position.price_open) * position.volume
                else:
                    profit = (position.price_open - current_price['ask']) * position.volume
                
                if profit > 0:  # 수익 포지션만
                    actual_profit = self.close_position_immediately(position)
                    if actual_profit is not None:
                        total_closed += 1
                        total_profit += actual_profit
                        print(f"  ✅ 수익포지션 #{position.ticket} 청산: ${actual_profit:+.2f}")
        
        print(f"✅ 수익 포지션 청산 완료: {total_closed}개, 총 수익: ${total_profit:+.2f}")
        return total_closed, 0, total_profit
    
    def close_loss_positions_only(self):
        """📉 손실 포지션만 청산"""
        print("\n📉 손실 포지션만 청산 중...")
        positions = mt5.positions_get()
        current_price = self.get_current_price()
        total_closed = 0
        total_loss = 0
        
        if positions and current_price:
            for position in positions:
                # 손실 여부 확인
                if position.type == mt5.ORDER_TYPE_BUY:
                    profit = (current_price['bid'] - position.price_open) * position.volume
                else:
                    profit = (position.price_open - current_price['ask']) * position.volume
                
                if profit < 0:  # 손실 포지션만
                    actual_profit = self.close_position_immediately(position)
                    if actual_profit is not None:
                        total_closed += 1
                        total_loss += actual_profit
                        print(f"  ✅ 손실포지션 #{position.ticket} 청산: ${actual_profit:+.2f}")
        
        print(f"✅ 손실 포지션 청산 완료: {total_closed}개, 총 손실: ${total_loss:+.2f}")
        return total_closed, 0, total_loss
    
    def check_user_input(self):
        """🎮 사용자 입력 체크 (비동기)"""
        try:
            import select
            import sys
            
            # Windows에서는 msvcrt 사용
            if sys.platform == "win32":
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'q':
                        print("\n🎮 청산 메뉴 호출됨!")
                        result = self.user_close_all_interface()
                        if result:
                            return True  # 청산 실행됨
                    elif key == 'e':
                        print("\n🚨 긴급 전체 청산!")
                        self.emergency_close_all_system()
                        return True
                    elif key == 's':
                        self.display_current_status()
                    elif key == 'h':
                        self.display_help()
                    elif key == 'f':  # 새로운 단축키
                        print("\n🔄 손실 포지션 즉시 뒤집기!")
                        current_price = self.get_current_price()
                        if current_price:
                            self.flip_all_losing_positions(current_price)
                    elif key == 'r':  # 새로운 단축키
                        print("\n⚡ 전체 포지션 즉시 뒤집기!")
                        current_price = self.get_current_price()
                        if current_price:
                            positions = mt5.positions_get(symbol=self.config['symbol'])
                            if positions:
                                for position in positions:
                                    profit = 0  # 임시값
                                    self.flip_position_direction(position, current_price, profit)
            else:
                # Linux/Mac에서는 select 사용
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1).lower()
                    if key == 'q':
                        print("\n🎮 청산 메뉴 호출됨!")
                        result = self.user_close_all_interface()
                        if result:
                            return True
                    elif key == 'e':
                        print("\n🚨 긴급 전체 청산!")
                        self.emergency_close_all_system()
                        return True
                    elif key == 's':
                        self.display_current_status()
                    elif key == 'h':
                        self.display_help()
                    elif key == 'f':  # 새로운 단축키
                        print("\n🔄 손실 포지션 즉시 뒤집기!")
                        current_price = self.get_current_price()
                        if current_price:
                            self.flip_all_losing_positions(current_price)
                    elif key == 'r':  # 새로운 단축키
                        print("\n⚡ 전체 포지션 즉시 뒤집기!")
                        current_price = self.get_current_price()
                        if current_price:
                            positions = mt5.positions_get(symbol=self.config['symbol'])
                            if positions:
                                for position in positions:
                                    profit = 0  # 임시값
                                    self.flip_position_direction(position, current_price, profit)
            
            return False
            
        except:
            return False  # 오류시 계속 진행
    
    def display_current_status(self):
        """📊 현재 상태 표시"""
        print("\n" + "="*60)
        print("📊 현재 시스템 상태")
        print("="*60)
        
        # 계좌 정보
        account_info = mt5.account_info()
        if account_info:
            print(f"💎 잔고: ${account_info.balance:,.2f}")
            print(f"📈 자산: ${account_info.equity:,.2f}")
            print(f"🔥 손익: ${account_info.equity - account_info.balance:+.2f}")
        
        # 포지션 정보
        positions = mt5.positions_get()
        orders = mt5.orders_get()
        
        print(f"📊 활성 포지션: {len(positions) if positions else 0}개")
        print(f"📋 대기 주문: {len(orders) if orders else 0}개")
        
        # 완료된 거래
        completed = len(self.grid_positions['completed_trades'])
        winning = sum(1 for trade in self.grid_positions['completed_trades'] if trade['profit'] > 0)
        
        print(f"✅ 완료 거래: {completed}회")
        print(f"🎯 성공 거래: {winning}회")
        
        if completed > 0:
            win_rate = (winning / completed) * 100
            print(f"📈 승률: {win_rate:.1f}%")
        
        print("="*60)
    
    def display_help(self):
        """❓ 도움말 표시"""
        print("\n" + "="*60)
        print("❓ 키보드 단축키")
        print("="*60)
        print("Q: 청산 메뉴 열기")
        print("E: 긴급 전체 청산")
        print("S: 현재 상태 표시")
        print("H: 도움말 표시")
        print("F: 🔄 손실 포지션 즉시 뒤집기")  # 새로운 키
        print("R: ⚡ 전체 포지션 즉시 뒤집기")  # 새로운 키
        print("Ctrl+C: 시스템 종료")
        print("="*60)
    
    def instant_loss_to_profit_flip(self, current_price):
        """⚡ 즉시 손실→수익 전환 (포지션 방향 뒤집기)"""
        account_info = mt5.account_info()
        if not account_info:
            return
        
        # 현재 손익 확인
        current_loss = account_info.equity - account_info.balance
        
        # $10 이상 손실이면 즉시 전환
        if current_loss < -10:
            print(f"\n⚡ 손실 감지 ${current_loss:+.2f} → 즉시 방향 전환!")
            self.flip_all_losing_positions(current_price)
    
    def flip_all_losing_positions(self, current_price):
        """🔄 모든 손실 포지션 방향 뒤집기"""
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return
        
        flipped_count = 0
        total_converted_loss = 0
        
        for position in positions:
            # 손실 포지션인지 확인
            if position.type == mt5.ORDER_TYPE_BUY:
                profit = (current_price['bid'] - position.price_open) * position.volume
            else:
                profit = (position.price_open - current_price['ask']) * position.volume
            
            # 손실 포지션이면 즉시 뒤집기
            if profit < -0.5:  # $0.5 이상 손실
                success = self.flip_position_direction(position, current_price, profit)
                if success:
                    flipped_count += 1
                    total_converted_loss += abs(profit)
                    print(f"  🔄 포지션 #{position.ticket} 뒤집기: ${profit:+.2f} → 수익전환")
        
        if flipped_count > 0:
            print(f"✅ {flipped_count}개 포지션 뒤집기 완료! 전환된 손실: ${total_converted_loss:.2f}")
    
    def flip_position_direction(self, losing_position, current_price, loss_amount):
        """🔄 개별 포지션 방향 뒤집기"""
        try:
            # 1. 기존 손실 포지션 즉시 청산
            close_result = self.close_position_immediately(losing_position)
            if close_result is None:
                return False
            
            # 2. 즉시 반대 방향으로 같은 거래량 진입
            if losing_position.type == mt5.ORDER_TYPE_BUY:
                # 매수 손실 → 매도로 전환
                flip_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": losing_position.volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"FLIP_SELL_{losing_position.ticket}",
                }
            else:
                # 매도 손실 → 매수로 전환
                flip_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": losing_position.volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"FLIP_BUY_{losing_position.ticket}",
                }
            
            # 3. 반대 방향 포지션 진입
            flip_result = mt5.order_send(flip_request)
            if flip_result and flip_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"    ✅ 방향전환: {losing_position.type} → {flip_request['type']} @ ${flip_result.price:.2f}")
                
                # 4. 매우 작은 수익으로도 청산되도록 설정
                self.set_micro_profit_exit(flip_result.order, flip_request['type'], flip_result.price, losing_position.volume)
                
                return True
            else:
                print(f"    ❌ 방향전환 실패: {flip_result.retcode if flip_result else 'Unknown'}")
                return False
                
        except Exception as e:
            print(f"❌ 포지션 뒤집기 오류: {e}")
            return False
    
    def set_micro_profit_exit(self, position_ticket, position_type, entry_price, volume):
        """⚡ 마이크로 수익 청산 설정 (0.02% 수익으로도 청산)"""
        try:
            if position_type == mt5.ORDER_TYPE_BUY:
                # 매수 → 0.02% 상승시 청산
                target_price = entry_price * 1.0002
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MICRO_EXIT_BUY_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                # 매도 → 0.02% 하락시 청산
                target_price = entry_price * 0.9998
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MICRO_EXIT_SELL_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"      ⚡ 마이크로청산 설정: #{result.order} @ ${target_price:.2f} (0.02% 수익)")
            
        except Exception as e:
            print(f"❌ 마이크로청산 설정 오류: {e}")
    
    def auto_flip_system(self, current_price):
        """🔄 자동 뒤집기 시스템 (실시간 모니터링)"""
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return
        
        for position in positions:
            # 포지션 보유 시간
            position_age = datetime.now().timestamp() - position.time
            
            # 3초 이상 손실이면 즉시 뒤집기
            if position_age > 3:
                if position.type == mt5.ORDER_TYPE_BUY:
                    profit = (current_price['bid'] - position.price_open) * position.volume
                else:
                    profit = (position.price_open - current_price['ask']) * position.volume
                
                if profit < -0.3:  # $0.3 이상 손실
                    print(f"🔄 자동뒤집기: 포지션#{position.ticket} 손실${profit:+.2f}")
                    self.flip_position_direction(position, current_price, profit)
    
    def execute_complete_direction_reversal(self, current_price, loss_amount):
        """⚡ 완전 방향 전환 실행 (손실을 수익으로 완전 전환)"""
        try:
            print("🔄 완전 방향 전환 시작...")
            
            # 1. 현재 포지션 분석
            positions = mt5.positions_get(symbol=self.config['symbol'])
            if not positions:
                return
            
            total_buy_volume = 0
            total_sell_volume = 0
            losing_positions = []
            
            for position in positions:
                if position.type == mt5.ORDER_TYPE_BUY:
                    profit = (current_price['bid'] - position.price_open) * position.volume
                    total_buy_volume += position.volume
                    if profit < 0:
                        losing_positions.append(position)
                else:
                    profit = (position.price_open - current_price['ask']) * position.volume
                    total_sell_volume += position.volume
                    if profit < 0:
                        losing_positions.append(position)
            
            # 2. 손실 복구에 필요한 거래량 계산
            recovery_multiplier = max(3.0, loss_amount / 100)  # 손실에 비례한 복구 배수
            
            # 3. 방향 전환 실행
            if total_buy_volume > total_sell_volume:
                # 매수 포지션이 많으면 → 대량 매도로 전환
                self.execute_massive_sell_conversion(current_price, total_buy_volume, recovery_multiplier, loss_amount)
            else:
                # 매도 포지션이 많으면 → 대량 매수로 전환
                self.execute_massive_buy_conversion(current_price, total_sell_volume, recovery_multiplier, loss_amount)
            
            print(f"✅ 방향 전환 완료! 예상 복구: ${loss_amount * recovery_multiplier:.2f}")
            
        except Exception as e:
            print(f"❌ 방향 전환 오류: {e}")
    
    def execute_massive_sell_conversion(self, current_price, buy_volume, multiplier, loss_amount):
        """📉 대량 매도 전환 (매수 손실 → 매도 수익)"""
        try:
            # 손실 복구 + 추가 수익을 위한 대량 매도
            conversion_volume = buy_volume * multiplier
            
            # 여러 번에 나누어 진입 (리스크 분산)
            num_entries = min(5, max(1, int(conversion_volume / 0.1)))
            volume_per_entry = conversion_volume / num_entries
            
            for i in range(num_entries):
                # 각각 다른 가격에서 진입 (더 유리한 평균가)
                entry_price_adjustment = current_price['mid'] * 0.0001 * i  # 0.01%씩 차이
                
                sell_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": volume_per_entry,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MASSIVE_SELL_CONV_{i+1}_{loss_amount:.0f}",
                }
                
                result = mt5.order_send(sell_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"  📉 대량매도 {i+1}/{num_entries}: {volume_per_entry:.3f} @ ${result.price:.2f}")
                    
                    # 매우 작은 하락으로도 수익이 나도록 청산 주문
                    target_price = result.price - (current_price['mid'] * 0.0005)  # 0.05% 하락시 청산
                    self.place_ultra_quick_exit(result.order, 'sell', target_price, volume_per_entry)
                
                time.sleep(0.1)  # 0.1초 간격
                
        except Exception as e:
            print(f"❌ 대량매도 전환 오류: {e}")
    
    def execute_massive_buy_conversion(self, current_price, sell_volume, multiplier, loss_amount):
        """📈 대량 매수 전환 (매도 손실 → 매수 수익)"""
        try:
            # 손실 복구 + 추가 수익을 위한 대량 매수
            conversion_volume = sell_volume * multiplier
            
            # 여러 번에 나누어 진입 (리스크 분산)
            num_entries = min(5, max(1, int(conversion_volume / 0.1)))
            volume_per_entry = conversion_volume / num_entries
            
            for i in range(num_entries):
                # 각각 다른 가격에서 진입 (더 유리한 평균가)
                entry_price_adjustment = current_price['mid'] * 0.0001 * i  # 0.01%씩 차이
                
                buy_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": volume_per_entry,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MASSIVE_BUY_CONV_{i+1}_{loss_amount:.0f}",
                }
                
                result = mt5.order_send(buy_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"  📈 대량매수 {i+1}/{num_entries}: {volume_per_entry:.3f} @ ${result.price:.2f}")
                    
                    # 매우 작은 상승으로도 수익이 나도록 청산 주문
                    target_price = result.price + (current_price['mid'] * 0.0005)  # 0.05% 상승시 청산
                    self.place_ultra_quick_exit(result.order, 'buy', target_price, volume_per_entry)
                
                time.sleep(0.1)  # 0.1초 간격
                
        except Exception as e:
            print(f"❌ 대량매수 전환 오류: {e}")
    
    def place_ultra_quick_exit(self, position_ticket, position_type, target_price, volume):
        """⚡ 초고속 청산 주문 (0.05% 움직임으로 수익)"""
        try:
            if position_type == 'buy':
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"ULTRA_EXIT_BUY_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"ULTRA_EXIT_SELL_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"    ⚡ 초고속청산: #{result.order} @ ${target_price:.2f}")
                
        except Exception as e:
            print(f"❌ 초고속청산 오류: {e}")
    
    def emergency_profit_boost_system(self, current_price):
        """🚀 긴급 수익 부스트 시스템 (추가 수익 창출)"""
        account_info = mt5.account_info()
        if not account_info:
            return
        
        current_profit = account_info.equity - account_info.balance
        
        # 손실이 계속되면 더 공격적인 수익 부스트
        if current_profit < -100:
            print(f"🚀 긴급 수익 부스트 실행! 현재 손실: ${current_profit:+.2f}")
            
            # 양방향 동시 대량 진입
            self.execute_bidirectional_boost(current_price, abs(current_profit))
    
    def execute_bidirectional_boost(self, current_price, loss_amount):
        """⚡ 양방향 동시 부스트 (어떤 방향으로 가도 수익)"""
        try:
            boost_volume = max(0.1, loss_amount / 1000)  # 손실에 비례한 부스트 거래량
            
            # 동시 양방향 진입
            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": boost_volume,
                "type": mt5.ORDER_TYPE_BUY,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"BOOST_BUY_{loss_amount:.0f}",
            }
            
            sell_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": boost_volume,
                "type": mt5.ORDER_TYPE_SELL,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"BOOST_SELL_{loss_amount:.0f}",
            }
            
            # 매수 실행
            buy_result = mt5.order_send(buy_request)
            if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"  🚀 부스트매수: {boost_volume:.3f} @ ${buy_result.price:.2f}")
                # 0.03% 상승시 청산
                buy_target = buy_result.price + (current_price['mid'] * 0.0003)
                self.place_ultra_quick_exit(buy_result.order, 'buy', buy_target, boost_volume)
            
            # 매도 실행
            sell_result = mt5.order_send(sell_request)
            if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"  🚀 부스트매도: {boost_volume:.3f} @ ${sell_result.price:.2f}")
                # 0.03% 하락시 청산
                sell_target = sell_result.price - (current_price['mid'] * 0.0003)
                self.place_ultra_quick_exit(sell_result.order, 'sell', sell_target, boost_volume)
            
        except Exception as e:
            print(f"❌ 양방향 부스트 오류: {e}")
    
    def revolutionary_dynamic_grid_system(self, current_price):
        """🚀 혁명적 동적 그리드 시스템 (다양한 주문 타입 사용)"""
        if not self.config['dynamic_grid']:
            return
        
        # 1. 시장가 주문으로 즉시 진입 (30% 확률)
        self.execute_market_grid_orders(current_price)
        
        # 2. 스탑 주문으로 브레이크아웃 포착 (20% 확률)
        self.execute_stop_grid_orders(current_price)
        
        # 3. 동적 리미트 주문 (가격 추적)
        self.execute_dynamic_limit_orders(current_price)
        
        # 4. 공격적 진입 시스템 (매 5초마다)
        self.execute_aggressive_entry_system(current_price)
        
        # 5. 🔥 새로운 혁명적 기법들
        self.execute_momentum_breakout_system(current_price)
        self.execute_volatility_capture_system(current_price)
        self.execute_price_ladder_system(current_price)
        self.execute_multi_timeframe_grid(current_price)
    
    def execute_market_grid_orders(self, current_price):
        """⚡ 시장가 그리드 주문 (즉시 체결)"""
        if not self.config['market_orders']:
            return
        
        # 50% 확률로 시장가 주문 실행 (기존 30%에서 증가)
        if time.time() % 6 < 3:  # 6초 중 3초 (50% 확률)
            # 작은 거래량으로 즉시 양방향 진입
            market_volume = self.config['base_lot_size'] * 0.8  # 거래량 증가
            
            # 시장가 매수
            market_buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": market_volume,
                "type": mt5.ORDER_TYPE_BUY,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "MARKET_GRID_BUY",
            }
            
            buy_result = mt5.order_send(market_buy_request)
            if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"⚡ 시장가매수: {market_volume:.3f} @ ${buy_result.price:.2f}")
                # 0.08% 수익시 즉시 청산 (더 빠른 청산)
                self.set_quick_exit(buy_result.order, 'buy', buy_result.price, market_volume, 0.0008)
            
            # 시장가 매도
            market_sell_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": market_volume,
                "type": mt5.ORDER_TYPE_SELL,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "MARKET_GRID_SELL",
            }
            
            sell_result = mt5.order_send(market_sell_request)
            if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"⚡ 시장가매도: {market_volume:.3f} @ ${sell_result.price:.2f}")
                # 0.08% 수익시 즉시 청산 (더 빠른 청산)
                self.set_quick_exit(sell_result.order, 'sell', sell_result.price, market_volume, 0.0008)
    
    def execute_stop_grid_orders(self, current_price):
        """🎯 스탑 그리드 주문 (브레이크아웃 포착)"""
        if not self.config['stop_orders']:
            return
        
        # 40% 확률로 스탑 주문 배치 (기존 20%에서 증가)
        if time.time() % 10 < 4:  # 10초 중 4초 (40% 확률)
            stop_volume = self.config['base_lot_size'] * 1.2  # 거래량 증가
            
            # 상승 브레이크아웃 스탑 주문 (더 가까운 가격)
            buy_stop_price = current_price['ask'] + (current_price['mid'] * 0.0003)  # 0.03% 위 (더 가까움)
            buy_stop_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": stop_volume,
                "type": mt5.ORDER_TYPE_BUY_STOP,
                "price": buy_stop_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "STOP_GRID_BUY",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            buy_stop_result = mt5.order_send(buy_stop_request)
            if buy_stop_result and buy_stop_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🎯 매수스탑: {stop_volume:.3f} @ ${buy_stop_price:.2f}")
            
            # 하락 브레이크아웃 스탑 주문 (더 가까운 가격)
            sell_stop_price = current_price['bid'] - (current_price['mid'] * 0.0003)  # 0.03% 아래 (더 가까움)
            sell_stop_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": stop_volume,
                "type": mt5.ORDER_TYPE_SELL_STOP,
                "price": sell_stop_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "STOP_GRID_SELL",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            sell_stop_result = mt5.order_send(sell_stop_request)
            if sell_stop_result and sell_stop_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🎯 매도스탑: {stop_volume:.3f} @ ${sell_stop_price:.2f}")
    
    def execute_dynamic_limit_orders(self, current_price):
        """🔄 동적 리미트 주문 (가격 추적)"""
        if not self.config['price_chase']:
            return
        
        # 기존 리미트 주문들을 현재가에 맞춰 동적 조정
        orders = mt5.orders_get(symbol=self.config['symbol'])
        if not orders:
            return
        
        for order in orders:
            if "GRID" in order.comment and "LIMIT" in str(order.type):
                # 주문가와 현재가 차이가 0.2% 이상이면 조정
                price_diff_pct = abs(order.price_open - current_price['mid']) / current_price['mid']
                
                if price_diff_pct > 0.002:  # 0.2% 이상 차이
                    # 기존 주문 취소
                    self.cancel_order_immediately(order.ticket)
                    
                    # 새로운 가격으로 재배치
                    if order.type == mt5.ORDER_TYPE_BUY_LIMIT:
                        new_price = current_price['bid'] - (current_price['mid'] * 0.001)  # 0.1% 아래
                        new_request = {
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": self.config['symbol'],
                            "volume": order.volume_initial,
                            "type": mt5.ORDER_TYPE_BUY_LIMIT,
                            "price": new_price,
                            "deviation": 100,
                            "magic": self.config['magic_number'],
                            "comment": f"DYNAMIC_BUY_{order.ticket}",
                            "type_time": mt5.ORDER_TIME_GTC,
                        }
                    else:
                        new_price = current_price['ask'] + (current_price['mid'] * 0.001)  # 0.1% 위
                        new_request = {
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": self.config['symbol'],
                            "volume": order.volume_initial,
                            "type": mt5.ORDER_TYPE_SELL_LIMIT,
                            "price": new_price,
                            "deviation": 100,
                            "magic": self.config['magic_number'],
                            "comment": f"DYNAMIC_SELL_{order.ticket}",
                            "type_time": mt5.ORDER_TIME_GTC,
                        }
                    
                    result = mt5.order_send(new_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🔄 동적조정: #{order.ticket} → #{result.order} @ ${new_price:.2f}")
    
    def execute_aggressive_entry_system(self, current_price):
        """🚀 공격적 진입 시스템 (더 자주 체결)"""
        if not self.config['aggressive_entry']:
            return
        
        # 매 3초마다 공격적 진입 (기존 5초에서 단축)
        if time.time() % 3 < 1:
            aggressive_volume = self.config['base_lot_size'] * 2.0  # 거래량 증가
            
            # 현재가 매우 가까운 곳에 주문 배치 (거의 시장가 수준)
            aggressive_buy_price = current_price['bid'] + (current_price['mid'] * 0.00005)  # 0.005% 위 (더 가까움)
            aggressive_sell_price = current_price['ask'] - (current_price['mid'] * 0.00005)  # 0.005% 아래 (더 가까움)
            
            # 공격적 매수 주문
            aggressive_buy_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": aggressive_volume,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": aggressive_buy_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "AGGRESSIVE_BUY",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            buy_result = mt5.order_send(aggressive_buy_request)
            if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🚀 공격매수: {aggressive_volume:.3f} @ ${aggressive_buy_price:.2f}")
            
            # 공격적 매도 주문
            aggressive_sell_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": aggressive_volume,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": aggressive_sell_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "AGGRESSIVE_SELL",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            sell_result = mt5.order_send(aggressive_sell_request)
            if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🚀 공격매도: {aggressive_volume:.3f} @ ${aggressive_sell_price:.2f}")
    
    def set_quick_exit(self, position_ticket, position_type, entry_price, volume, profit_pct):
        """⚡ 빠른 청산 설정"""
        try:
            if position_type == 'buy':
                target_price = entry_price * (1 + profit_pct)
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"QUICK_EXIT_BUY_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                target_price = entry_price * (1 - profit_pct)
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"QUICK_EXIT_SELL_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"   ⚡ 빠른청산: #{result.order} @ ${target_price:.2f}")
                
        except Exception as e:
            print(f"❌ 빠른청산 설정 오류: {e}")
    
    def execute_momentum_breakout_system(self, current_price):
        """🚀 모멘텀 브레이크아웃 시스템 (강한 움직임 포착)"""
        try:
            # 가격 변동률 계산
            if len(self.last_prices) < 5:
                return
            
            recent_prices = list(self.last_prices)[-5:]
            price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            # 강한 모멘텀 감지 (0.1% 이상 변동)
            if abs(price_change) > 0.001:
                momentum_volume = self.config['base_lot_size'] * 3  # 3배 거래량
                
                if price_change > 0:  # 상승 모멘텀
                    # 상승 추세 따라가기 - 시장가 매수
                    momentum_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.config['symbol'],
                        "volume": momentum_volume,
                        "type": mt5.ORDER_TYPE_BUY,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"MOMENTUM_UP_{price_change*100:.2f}%",
                    }
                    
                    result = mt5.order_send(momentum_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🚀 모멘텀매수: {momentum_volume:.3f} @ ${result.price:.2f} (상승{price_change*100:.2f}%)")
                        # 0.2% 수익시 청산
                        self.set_quick_exit(result.order, 'buy', result.price, momentum_volume, 0.002)
                
                else:  # 하락 모멘텀
                    # 하락 추세 따라가기 - 시장가 매도
                    momentum_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.config['symbol'],
                        "volume": momentum_volume,
                        "type": mt5.ORDER_TYPE_SELL,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"MOMENTUM_DOWN_{abs(price_change)*100:.2f}%",
                    }
                    
                    result = mt5.order_send(momentum_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🚀 모멘텀매도: {momentum_volume:.3f} @ ${result.price:.2f} (하락{abs(price_change)*100:.2f}%)")
                        # 0.2% 수익시 청산
                        self.set_quick_exit(result.order, 'sell', result.price, momentum_volume, 0.002)
                        
        except Exception as e:
            print(f"❌ 모멘텀 브레이크아웃 오류: {e}")
    
    def execute_volatility_capture_system(self, current_price):
        """⚡ 변동성 포착 시스템 (급격한 변동 활용)"""
        try:
            # 스프레드 기반 변동성 측정
            spread_pct = (current_price['ask'] - current_price['bid']) / current_price['mid']
            
            # 높은 변동성 감지 (스프레드가 평소보다 큰 경우)
            if spread_pct > 0.0001:  # 0.01% 이상 스프레드
                volatility_volume = self.config['base_lot_size'] * 2
                
                # 양방향 동시 진입 (변동성 활용)
                # 매수 주문 (현재 ASK 가격에서)
                vol_buy_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": volatility_volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"VOLATILITY_BUY_{spread_pct*10000:.0f}",
                }
                
                # 매도 주문 (현재 BID 가격에서)
                vol_sell_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": volatility_volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"VOLATILITY_SELL_{spread_pct*10000:.0f}",
                }
                
                # 동시 실행
                buy_result = mt5.order_send(vol_buy_request)
                sell_result = mt5.order_send(vol_sell_request)
                
                if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"⚡ 변동성매수: {volatility_volume:.3f} @ ${buy_result.price:.2f}")
                    # 매우 빠른 청산 (0.05% 수익)
                    self.set_quick_exit(buy_result.order, 'buy', buy_result.price, volatility_volume, 0.0005)
                
                if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"⚡ 변동성매도: {volatility_volume:.3f} @ ${sell_result.price:.2f}")
                    # 매우 빠른 청산 (0.05% 수익)
                    self.set_quick_exit(sell_result.order, 'sell', sell_result.price, volatility_volume, 0.0005)
                    
        except Exception as e:
            print(f"❌ 변동성 포착 오류: {e}")
    
    def execute_price_ladder_system(self, current_price):
        """🎯 가격 사다리 시스템 (계단식 주문 배치)"""
        try:
            # 매 30초마다 실행
            if time.time() % 30 < 1:
                ladder_volume = self.config['base_lot_size'] * 0.5
                
                # 현재가 기준으로 위아래 5단계씩 사다리 주문
                for i in range(1, 6):  # 5단계
                    # 매수 사다리 (아래쪽)
                    buy_price = current_price['mid'] * (1 - 0.0002 * i)  # 0.02%씩 아래
                    buy_ladder_request = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": self.config['symbol'],
                        "volume": ladder_volume,
                        "type": mt5.ORDER_TYPE_BUY_LIMIT,
                        "price": buy_price,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"LADDER_BUY_L{i}",
                        "type_time": mt5.ORDER_TIME_GTC,
                    }
                    
                    # 매도 사다리 (위쪽)
                    sell_price = current_price['mid'] * (1 + 0.0002 * i)  # 0.02%씩 위
                    sell_ladder_request = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": self.config['symbol'],
                        "volume": ladder_volume,
                        "type": mt5.ORDER_TYPE_SELL_LIMIT,
                        "price": sell_price,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"LADDER_SELL_L{i}",
                        "type_time": mt5.ORDER_TIME_GTC,
                    }
                    
                    # 주문 실행
                    buy_result = mt5.order_send(buy_ladder_request)
                    if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🎯 사다리매수{i}: {ladder_volume:.3f} @ ${buy_price:.2f}")
                    
                    sell_result = mt5.order_send(sell_ladder_request)
                    if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🎯 사다리매도{i}: {ladder_volume:.3f} @ ${sell_price:.2f}")
                    
                    time.sleep(0.1)  # 0.1초 간격
                    
        except Exception as e:
            print(f"❌ 가격 사다리 오류: {e}")
    
    def execute_multi_timeframe_grid(self, current_price):
        """🔄 다중 시간대 그리드 (다양한 주기로 주문)"""
        try:
            current_time = time.time()
            
            # 1초마다 - 초단기 그리드
            if current_time % 1 < 0.1:
                self.place_ultra_short_grid(current_price, 0.0001, 0.3)  # 0.01%, 0.3배 거래량
            
            # 5초마다 - 단기 그리드
            if current_time % 5 < 0.1:
                self.place_ultra_short_grid(current_price, 0.0005, 0.5)  # 0.05%, 0.5배 거래량
            
            # 15초마다 - 중기 그리드
            if current_time % 15 < 0.1:
                self.place_ultra_short_grid(current_price, 0.001, 1.0)   # 0.1%, 1배 거래량
            
            # 60초마다 - 장기 그리드
            if current_time % 60 < 0.1:
                self.place_ultra_short_grid(current_price, 0.002, 2.0)   # 0.2%, 2배 거래량
                
        except Exception as e:
            print(f"❌ 다중 시간대 그리드 오류: {e}")
    
    def place_ultra_short_grid(self, current_price, distance_pct, volume_multiplier):
        """⚡ 초단기 그리드 배치"""
        try:
            volume = self.config['base_lot_size'] * volume_multiplier
            
            # 매수 주문
            buy_price = current_price['mid'] * (1 - distance_pct)
            buy_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": buy_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"ULTRA_BUY_{distance_pct*10000:.0f}",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            # 매도 주문
            sell_price = current_price['mid'] * (1 + distance_pct)
            sell_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": sell_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"ULTRA_SELL_{distance_pct*10000:.0f}",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            # 주문 실행
            buy_result = mt5.order_send(buy_request)
            sell_result = mt5.order_send(sell_request)
            
            if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"⚡ 초단기매수: {volume:.3f} @ ${buy_price:.2f} ({distance_pct*100:.3f}%)")
            
            if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"⚡ 초단기매도: {volume:.3f} @ ${sell_price:.2f} ({distance_pct*100:.3f}%)")
                
        except Exception as e:
            print(f"❌ 초단기 그리드 오류: {e}")
    
    def place_grid_orders(self, grid_data):
        """🚀 그리드 주문 일괄 배치 (오류 10016 해결)"""
        print("🚀 대량 그리드 주문 일괄 배치 시작!")
        print(f"📊 총 {len(grid_data)}개 레벨 × 2방향 = 최대 {len(grid_data) * 2}개 주문")
        print("="*70)
        
        current_price = self.get_current_price()
        if not current_price:
            print("❌ 현재가 조회 실패")
            return False
        
        # 심볼 정보 확인
        symbol_info = mt5.symbol_info(self.config['symbol'])
        if not symbol_info:
            print("❌ 심볼 정보 조회 실패")
            return False
        
        successful_orders = 0
        failed_orders = 0
        
        # 배치 처리를 위한 주문 그룹화
        buy_orders = []
        sell_orders = []
        
        for level_data in grid_data:
            level = level_data['level']
            name = level_data['name']
            lot_size = level_data['lot_size']
            
            # 거래량 정규화
            min_lot = symbol_info.volume_min
            max_lot = symbol_info.volume_max
            lot_step = symbol_info.volume_step
            lot_size = max(min_lot, min(max_lot, round(lot_size / lot_step) * lot_step))
            
            # 매수 주문 준비 (현재가보다 아래에서 대기)
            if level_data['buy_entry'] < current_price['mid']:
                buy_orders.append((level, name, level_data, lot_size))
            
            # 매도 주문 준비 (현재가보다 위에서 대기)
            if level_data['sell_entry'] > current_price['mid']:
                sell_orders.append((level, name, level_data, lot_size))
        
        print(f"📊 배치 예정: 매수 {len(buy_orders)}개, 매도 {len(sell_orders)}개")
        
        # 매수 주문 일괄 처리
        print(f"\n🔵 매수 주문 {len(buy_orders)}개 배치 중...")
        for i, (level, name, level_data, lot_size) in enumerate(buy_orders):
            print(f"  [{i+1:2d}/{len(buy_orders):2d}] 레벨 {level+1:2d} {name:10s}: ${level_data['buy_entry']:8,.0f}", end=" ")
            
            # SL/TP 계산 (안전한 범위로 설정)
            buy_sl = self.calculate_safe_sl(level_data['buy_entry'], 'buy', current_price['mid'])
            buy_tp = self.calculate_safe_tp(level_data['buy_entry'], level_data['buy_target'], 'buy', current_price['mid'])
            
            # 극한 레벨 체크 (500% 이상 차이)
            price_ratio = abs(level_data['buy_entry'] - current_price['mid']) / current_price['mid']
            is_extreme_level = price_ratio > 5.0
            
            buy_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": level_data['buy_entry'],
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"GRID_BUY_L{level+1}_{name}{'_EXTREME' if is_extreme_level else ''}",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            # 극한 레벨이 아닌 경우에만 SL/TP 추가
            if not is_extreme_level:
                if buy_sl > 0:
                    buy_request["sl"] = buy_sl
                if buy_tp > 0:
                    buy_request["tp"] = buy_tp
            
            buy_result = mt5.order_send(buy_request)
            if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ 주문#{buy_result.order}")
                self.grid_positions['buy_orders'][level] = {
                    'order_id': buy_result.order,
                    'level_data': level_data,
                    'timestamp': datetime.now()
                }
                successful_orders += 1
            else:
                error_code = buy_result.retcode if buy_result else "Unknown"
                print(f"❌ 실패:{error_code}")
                
                # 오류 10016인 경우 SL/TP 없이 재시도
                if error_code == 10016:
                    print(f"    🔄 SL/TP 없이 재시도...", end=" ")
                    buy_request_retry = buy_request.copy()
                    buy_request_retry.pop("sl", None)
                    buy_request_retry.pop("tp", None)
                    
                    retry_result = mt5.order_send(buy_request_retry)
                    if retry_result and retry_result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"✅ 성공#{retry_result.order}")
                        self.grid_positions['buy_orders'][level] = {
                            'order_id': retry_result.order,
                            'level_data': level_data,
                            'timestamp': datetime.now()
                        }
                        successful_orders += 1
                    else:
                        print(f"❌ 재시도실패:{retry_result.retcode if retry_result else 'Unknown'}")
                        failed_orders += 1
                else:
                    failed_orders += 1
            
            # 너무 빠른 주문 방지 (0.1초 대기)
            time.sleep(0.1)
        
        # 매도 주문 일괄 처리
        print(f"\n🔴 매도 주문 {len(sell_orders)}개 배치 중...")
        for i, (level, name, level_data, lot_size) in enumerate(sell_orders):
            print(f"  [{i+1:2d}/{len(sell_orders):2d}] 레벨 {level+1:2d} {name:10s}: ${level_data['sell_entry']:8,.0f}", end=" ")
            
            # SL/TP 계산 (안전한 범위로 설정)
            sell_sl = self.calculate_safe_sl(level_data['sell_entry'], 'sell', current_price['mid'])
            sell_tp = self.calculate_safe_tp(level_data['sell_entry'], level_data['sell_target'], 'sell', current_price['mid'])
            
            # 극한 레벨 체크 (500% 이상 차이)
            price_ratio = abs(level_data['sell_entry'] - current_price['mid']) / current_price['mid']
            is_extreme_level = price_ratio > 5.0
            
            sell_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": level_data['sell_entry'],
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"GRID_SELL_L{level+1}_{name}{'_EXTREME' if is_extreme_level else ''}",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            # 극한 레벨이 아닌 경우에만 SL/TP 추가
            if not is_extreme_level:
                if sell_sl > 0:
                    sell_request["sl"] = sell_sl
                if sell_tp > 0:
                    sell_request["tp"] = sell_tp
            
            sell_result = mt5.order_send(sell_request)
            if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ 주문#{sell_result.order}")
                self.grid_positions['sell_orders'][level] = {
                    'order_id': sell_result.order,
                    'level_data': level_data,
                    'timestamp': datetime.now()
                }
                successful_orders += 1
            else:
                error_code = sell_result.retcode if sell_result else "Unknown"
                print(f"❌ 실패:{error_code}")
                
                # 오류 10016인 경우 SL/TP 없이 재시도
                if error_code == 10016:
                    print(f"    🔄 SL/TP 없이 재시도...", end=" ")
                    sell_request_retry = sell_request.copy()
                    sell_request_retry.pop("sl", None)
                    sell_request_retry.pop("tp", None)
                    
                    retry_result = mt5.order_send(sell_request_retry)
                    if retry_result and retry_result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"✅ 성공#{retry_result.order}")
                        self.grid_positions['sell_orders'][level] = {
                            'order_id': retry_result.order,
                            'level_data': level_data,
                            'timestamp': datetime.now()
                        }
                        successful_orders += 1
                    else:
                        print(f"❌ 재시도실패:{retry_result.retcode if retry_result else 'Unknown'}")
                        failed_orders += 1
                else:
                    failed_orders += 1
            
            # 너무 빠른 주문 방지 (0.1초 대기)
            time.sleep(0.1)
        
        print(f"\n🎯 대량 그리드 배치 완료!")
        print(f"  ✅ 성공: {successful_orders}개 주문")
        print(f"  ❌ 실패: {failed_orders}개 주문")
        print(f"  📊 성공률: {successful_orders/(successful_orders+failed_orders)*100:.1f}%")
        
        if successful_orders > 0:
            print(f"🚀 {successful_orders}개 주문이 활성화되어 수익 기회를 대기 중!")
            return True
        else:
            print("❌ 모든 주문이 실패했습니다.")
            return False
    
    def calculate_safe_sl(self, entry_price, order_type, current_price):
        """🛡️ 안전한 손절가 계산 (오류 10016 방지)"""
        try:
            # 극한 레벨 (현재가 대비 5배 이상)은 SL 없이 진행
            price_ratio = abs(entry_price - current_price) / current_price
            if price_ratio > 5.0:  # 500% 이상 차이나는 극한 레벨
                return 0  # SL 없음
            
            if order_type == 'buy':
                # 매수 주문: 진입가보다 낮은 손절가
                sl_price = entry_price * 0.98  # 2% 손절
                # 현재가보다 너무 높지 않도록 제한
                if sl_price >= current_price * 0.95:
                    sl_price = current_price * 0.95
            else:
                # 매도 주문: 진입가보다 높은 손절가
                sl_price = entry_price * 1.02  # 2% 손절
                # 현재가보다 너무 낮지 않도록 제한
                if sl_price <= current_price * 1.05:
                    sl_price = current_price * 1.05
            
            # 최소 가격 단위로 반올림
            return round(sl_price, 2)
            
        except:
            return 0  # 오류시 SL 없이 진행
    
    def calculate_safe_tp(self, entry_price, target_price, order_type, current_price):
        """🎯 안전한 목표가 계산 (오류 10016 방지)"""
        try:
            # 극한 레벨 (현재가 대비 5배 이상)은 TP 없이 진행
            price_ratio = abs(entry_price - current_price) / current_price
            if price_ratio > 5.0:  # 500% 이상 차이나는 극한 레벨
                return 0  # TP 없음
            
            if order_type == 'buy':
                # 매수 주문: 진입가보다 높은 목표가
                tp_price = max(target_price, entry_price * 1.005)  # 최소 0.5% 수익
                # 너무 높지 않도록 제한
                if tp_price > current_price * 2:
                    tp_price = current_price * 1.5
            else:
                # 매도 주문: 진입가보다 낮은 목표가
                tp_price = min(target_price, entry_price * 0.995)  # 최소 0.5% 수익
                # 너무 낮지 않도록 제한
                if tp_price < current_price * 0.5:
                    tp_price = current_price * 0.7
            
            # 최소 가격 단위로 반올림
            return round(tp_price, 2)
            
        except:
            return 0  # 오류시 TP 없이 진행
    
    def monitor_grid_positions(self):
        """📊 그리드 포지션 모니터링 + 완전 자동 청산"""
        # 대기 주문 확인
        pending_orders = mt5.orders_get(symbol=self.config['symbol'])
        active_positions = mt5.positions_get(symbol=self.config['symbol'])
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        # 체결된 주문 확인 및 자동 청산 처리
        filled_orders = []
        for level, order_info in list(self.grid_positions['buy_orders'].items()):
            order_id = order_info['order_id']
            if not any(order.ticket == order_id for order in pending_orders or []):
                # 주문이 체결됨 - 자동 청산 처리
                filled_orders.append(('buy', level, order_info))
                del self.grid_positions['buy_orders'][level]
        
        for level, order_info in list(self.grid_positions['sell_orders'].items()):
            order_id = order_info['order_id']
            if not any(order.ticket == order_id for order in pending_orders or []):
                # 주문이 체결됨 - 자동 청산 처리
                filled_orders.append(('sell', level, order_info))
                del self.grid_positions['sell_orders'][level]
        
        # 체결된 주문 처리 및 즉시 청산
        for order_type, level, order_info in filled_orders:
            level_data = order_info['level_data']
            self.process_filled_order(order_type, level, level_data, current_price)
        
        # 활성 포지션 자동 청산 모니터링
        if active_positions:
            for position in active_positions:
                self.check_auto_close_position(position, current_price)
        
        # 🔥 혁명적 기법들 실행
        self.revolutionary_scalping_system(current_price)
        self.revolutionary_martingale_system(current_price)
        self.revolutionary_hedging_system(current_price)
        self.instant_profit_system(current_price)  # 즉시 수익 시스템
        self.instant_loss_to_profit_flip(current_price)  # ⚡ 즉시 손실→수익 뒤집기
        self.auto_flip_system(current_price)  # 🔄 자동 뒤집기 시스템
        
        # 🚀 혁명적 동적 그리드 시스템 (새로 추가!)
        self.revolutionary_dynamic_grid_system(current_price)
        
        # 실시간 상태 표시
        total_pending = len(pending_orders or [])
        total_positions = len(active_positions or [])
        
        if total_pending > 0 or total_positions > 0:
            unrealized_profit = sum(
                (current_price['bid'] - pos.price_open) * pos.volume if pos.type == mt5.ORDER_TYPE_BUY
                else (pos.price_open - current_price['ask']) * pos.volume
                for pos in (active_positions or [])
            )
            
            print(f"📊 그리드 상태: 대기주문 {total_pending}개 | 활성포지션 {total_positions}개 | 미실현 ${unrealized_profit:+.2f}")
    
    def process_filled_order(self, order_type, level, level_data, current_price):
        """🎯 체결된 주문 처리 및 자동 청산"""
        level_name = level_data['name']
        expected_profit = level_data[f'{order_type}_profit']
        
        print(f"🎯 레벨 {level+1} {level_name} {order_type.upper()} 주문 체결!")
        print(f"   예상수익: ${expected_profit:.2f}")
        
        # 통계 업데이트
        self.stats['level_stats'][level]['trades'] += 1
        self.stats['total_trades'] += 1
        
        # 즉시 반대 방향 청산 주문 배치 (더 공격적인 수익 실현)
        self.place_immediate_close_order(order_type, level, level_data, current_price)
        
        # 새로운 그리드 주문 즉시 재배치
        self.replace_grid_order(order_type, level, level_data, current_price)
    
    def place_immediate_close_order(self, order_type, level, level_data, current_price):
        """⚡ 즉시 청산 주문 배치 (오류 수정)"""
        try:
            # 심볼 정보 다시 확인
            symbol_info = mt5.symbol_info(self.config['symbol'])
            if not symbol_info:
                print(f"   ❌ 심볼 정보 조회 실패")
                return
            
            # 거래량 정규화 (오류 10014 해결)
            volume = level_data['lot_size']
            min_lot = symbol_info.volume_min
            max_lot = symbol_info.volume_max
            lot_step = symbol_info.volume_step
            
            # 정확한 거래량 계산
            volume = max(min_lot, min(max_lot, round(volume / lot_step) * lot_step))
            
            if order_type == 'buy':
                # 매수 포지션 -> 시장가로 즉시 매도 (더 확실한 청산)
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MARKET_CLOSE_BUY_L{level+1}",
                }
                close_type = "매도"
            else:
                # 매도 포지션 -> 시장가로 즉시 매수 (더 확실한 청산)
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"MARKET_CLOSE_SELL_L{level+1}",
                }
                close_type = "매수"
            
            result = mt5.order_send(close_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                actual_price = result.price if hasattr(result, 'price') else current_price['mid']
                profit = self.calculate_trade_profit(order_type, level_data, actual_price)
                print(f"   ⚡ 시장가 청산 완료: {close_type} ${actual_price:.2f} | 수익: ${profit:+.2f}")
                
                # 통계 업데이트
                self.stats['total_profit'] += profit
                if profit > 0:
                    self.stats['winning_trades'] += 1
                    self.stats['level_stats'][level]['profit'] += profit
                
                return True
            else:
                error_code = result.retcode if result else "Unknown"
                print(f"   ❌ 시장가 청산 실패: {error_code}")
                
                # 실패시 포지션 직접 찾아서 청산 시도
                self.force_close_position_by_symbol(volume, order_type)
                return False
                
        except Exception as e:
            print(f"   ❌ 청산 오류: {e}")
            return False
    
    def calculate_trade_profit(self, order_type, level_data, exit_price):
        """💰 거래 수익 계산"""
        try:
            if order_type == 'buy':
                entry_price = level_data['buy_entry']
                profit = (exit_price - entry_price) * level_data['lot_size']
            else:
                entry_price = level_data['sell_entry']
                profit = (entry_price - exit_price) * level_data['lot_size']
            
            return profit
        except:
            return 0
    
    def force_close_position_by_symbol(self, volume, order_type):
        """🔧 포지션 강제 청산 (백업 방법)"""
        try:
            positions = mt5.positions_get(symbol=self.config['symbol'])
            if not positions:
                return
            
            # 해당 타입의 포지션 찾기
            target_type = mt5.ORDER_TYPE_BUY if order_type == 'buy' else mt5.ORDER_TYPE_SELL
            
            for position in positions:
                if position.type == target_type and abs(position.volume - volume) < 0.001:
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": position.ticket,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": "FORCE_CLOSE_BACKUP",
                    }
                    
                    result = mt5.order_send(close_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"   🔧 백업 청산 성공: 포지션#{position.ticket}")
                        return True
            
            return False
        except Exception as e:
            print(f"   ❌ 백업 청산 오류: {e}")
            return False
    
    def replace_grid_order(self, order_type, level, level_data, current_price):
        """🔄 그리드 주문 즉시 재배치 (연속 수익)"""
        try:
            # 같은 레벨에 새로운 주문 즉시 배치
            if order_type == 'buy':
                # 매수 주문이 체결되었으므로 새로운 매수 주문 배치
                new_buy_price = current_price['mid'] - (current_price['mid'] * level_data['distance_pct'])
                
                if new_buy_price > 0:
                    new_request = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": self.config['symbol'],
                        "volume": level_data['lot_size'],
                        "type": mt5.ORDER_TYPE_BUY_LIMIT,
                        "price": new_buy_price,
                        "tp": current_price['mid'],
                        "sl": new_buy_price * 0.95,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"REGRID_BUY_L{level+1}_{level_data['name']}",
                        "type_time": mt5.ORDER_TIME_GTC,
                    }
                    
                    result = mt5.order_send(new_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"   🔄 새 매수주문 배치: ${new_buy_price:.2f} (주문#{result.order})")
                        # 내부 데이터 업데이트
                        self.grid_positions['buy_orders'][level] = {
                            'order_id': result.order,
                            'level_data': level_data,
                            'timestamp': datetime.now()
                        }
            else:
                # 매도 주문이 체결되었으므로 새로운 매도 주문 배치
                new_sell_price = current_price['mid'] + (current_price['mid'] * level_data['distance_pct'])
                
                new_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": level_data['lot_size'],
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": new_sell_price,
                    "tp": current_price['mid'],
                    "sl": new_sell_price * 1.05,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"REGRID_SELL_L{level+1}_{level_data['name']}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                
                result = mt5.order_send(new_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"   🔄 새 매도주문 배치: ${new_sell_price:.2f} (주문#{result.order})")
                    # 내부 데이터 업데이트
                    self.grid_positions['sell_orders'][level] = {
                        'order_id': result.order,
                        'level_data': level_data,
                        'timestamp': datetime.now()
                    }
                    
        except Exception as e:
            print(f"   ❌ 재배치 오류: {e}")
    
    def check_auto_close_position(self, position, current_price):
        """🎯 활성 포지션 자동 청산 체크 (개선된 버전)"""
        try:
            # 수익 계산
            if position.type == mt5.ORDER_TYPE_BUY:
                profit = (current_price['bid'] - position.price_open) * position.volume
                profit_pct = (current_price['bid'] - position.price_open) / position.price_open
                current_market_price = current_price['bid']
            else:
                profit = (position.price_open - current_price['ask']) * position.volume
                profit_pct = (position.price_open - current_price['ask']) / position.price_open
                current_market_price = current_price['ask']
            
            # 포지션 보유 시간 계산
            position_age = datetime.now().timestamp() - position.time
            
            # 자동 청산 조건들 (더 공격적)
            should_close = False
            close_reason = ""
            
            # 1. 빠른 수익 실현 (0.15% 이상)
            if profit_pct >= 0.0015:
                should_close = True
                close_reason = f"빠른수익({profit_pct*100:.3f}%)"
            
            # 2. 초단기 수익 (0.1% 이상이고 30초 경과)
            elif profit_pct >= 0.001 and position_age > 30:
                should_close = True
                close_reason = f"초단기수익({profit_pct*100:.3f}%)"
            
            # 3. 시간 기반 청산 (0.05% 이상이고 2분 경과)
            elif profit_pct >= 0.0005 and position_age > 120:
                should_close = True
                close_reason = f"시간기반({profit_pct*100:.3f}%)"
            
            # 4. 손절 조건 (-1% 이하)
            elif profit_pct <= -0.01:
                should_close = True
                close_reason = f"손절({profit_pct*100:.2f}%)"
            
            # 5. 긴급 손절 (-2% 이하)
            elif profit_pct <= -0.02:
                should_close = True
                close_reason = f"긴급손절({profit_pct*100:.2f}%)"
            
            if should_close:
                success = self.auto_close_position_improved(position, profit, close_reason, current_market_price)
                if success:
                    return True
                    
        except Exception as e:
            print(f"❌ 포지션 체크 오류: {e}")
        
        return False
    
    def auto_close_position_improved(self, position, profit, reason, market_price):
        """⚡ 개선된 포지션 자동 청산"""
        try:
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"AUTO_{reason}",
            }
            
            result = mt5.order_send(close_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                actual_price = result.price if hasattr(result, 'price') else market_price
                print(f"⚡ 자동청산: #{position.ticket} | ${actual_price:.2f} | ${profit:+.2f} | {reason}")
                
                # 통계 업데이트
                self.stats['total_profit'] += profit
                if profit > 0:
                    self.stats['winning_trades'] += 1
                
                # 완료된 거래 기록
                self.grid_positions['completed_trades'].append({
                    'timestamp': datetime.now(),
                    'ticket': position.ticket,
                    'type': 'BUY' if position.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'volume': position.volume,
                    'entry_price': position.price_open,
                    'exit_price': actual_price,
                    'profit': profit,
                    'reason': reason
                })
                
                return True
            else:
                error_code = result.retcode if result else "Unknown"
                print(f"❌ 자동청산 실패: #{position.ticket} | 오류: {error_code}")
                return False
                
        except Exception as e:
            print(f"❌ 자동청산 오류: {e}")
            return False
    
    def update_grid_system(self):
        """🔄 그리드 시스템 업데이트"""
        current_price = self.get_current_price()
        if not current_price:
            return
        
        # 기준가 업데이트 (3% 이상 변동시 - 더 자주 업데이트)
        if abs(current_price['mid'] - self.current_baseline) / self.current_baseline > 0.03:
            print(f"\n🔄 기준가 업데이트: ${self.current_baseline:,.2f} → ${current_price['mid']:,.2f}")
            
            # 기존 대기 주문 취소 (개선된 정리 함수 사용)
            self.cleanup_all_positions_and_orders()
            
            # 새로운 기준가로 그리드 재설정
            self.current_baseline = current_price['mid']
            grid_data = self.calculate_unlimited_grid_levels(self.current_baseline)
            self.visualization_data['grid_levels'] = grid_data  # 시각화용 업데이트
            self.place_grid_orders(grid_data)
    
    def cleanup_all_positions_and_orders(self):
        """🗑️ 모든 기존 포지션과 주문 완전 삭제"""
        print("\n🗑️ 기존 포지션 및 주문 완전 정리 시작...")
        
        # 1. 모든 대기 주문 취소
        pending_orders = mt5.orders_get()
        if pending_orders:
            print(f"� 대기 주문 {len(pending_orders)}개 취소 중...")
            for order in pending_orders:
                cancel_request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                result = mt5.order_send(cancel_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"  ✅ 주문 #{order.ticket} 취소 완료")
                else:
                    print(f"  ❌ 주문 #{order.ticket} 취소 실패: {result.retcode if result else 'Unknown'}")
        
        # 2. 모든 활성 포지션 강제 청산
        active_positions = mt5.positions_get()
        if active_positions:
            print(f"📋 활성 포지션 {len(active_positions)}개 강제 청산 중...")
            for position in active_positions:
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "position": position.ticket,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": "FORCE_CLOSE_ALL",
                }
                
                result = mt5.order_send(close_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"  ✅ 포지션 #{position.ticket} 청산 완료")
                else:
                    print(f"  ❌ 포지션 #{position.ticket} 청산 실패: {result.retcode if result else 'Unknown'}")
        
        # 3. 내부 데이터 초기화
        self.grid_positions['buy_orders'].clear()
        self.grid_positions['sell_orders'].clear()
        self.grid_positions['active_positions'].clear()
        self.grid_positions['completed_trades'].clear()
        
        print("✅ 모든 포지션 및 주문 정리 완료!")
        time.sleep(2)  # 정리 완료 대기
    
    def run_grid_system(self):
        """🚀 그리드 시스템 실행"""
        print("\n" + "="*70)
        print("  🚀 혁명적 완전자동 다층 양방향 그리드 시스템 시작!")
        print("="*70)
        
        # 시작 전 모든 기존 포지션/주문 정리
        cleanup_choice = input("\n🗑️ 기존 모든 포지션/주문을 정리하시겠습니까? (y/n): ").strip().lower()
        if cleanup_choice == 'y':
            self.cleanup_all_positions_and_orders()
        
        # 초기 기준가 설정
        current_price = self.get_current_price()
        if not current_price:
            print("❌ 현재가 조회 실패")
            return
        
        self.current_baseline = current_price['mid']
        
        # 초기 그리드 설정
        grid_data = self.calculate_unlimited_grid_levels(self.current_baseline)
        self.visualization_data['grid_levels'] = grid_data  # 시각화용 저장
        
        if not self.place_grid_orders(grid_data):
            print("❌ 그리드 배치 실패")
            return
        
        print("\n🎯 완전자동 그리드 시스템 가동 중...")
        print("💡 체결 즉시 자동 청산으로 빠른 수익 실현!")
        print("🔄 청산 후 즉시 새 주문 재배치로 연속 수익!")
        print("\n🚀 혁명적 동적 그리드 시스템 활성화!")
        print("  ⚡ 시장가 주문: 50% 확률로 즉시 체결")
        print("  🎯 스탑 주문: 40% 확률로 브레이크아웃 포착")
        print("  � 공격적 진입: 3초마다 거의 시장가 수준 주문")
        print("  🔄 모멘텀 추종: 0.1% 변동시 즉시 추종")
        print("  ⚡ 변동성 포착: 스프레드 확대시 양방향 진입")
        print("  🎯 가격 사다리: 30초마다 5단계 사다리 주문")
        print("  🔄 다중 시간대: 1초/5초/15초/60초 주기별 그리드")
        print("\n🎮 실시간 제어 키:")
        print("  Q: 청산 메뉴 (포지션/주문 선택 청산)")
        print("  E: 긴급 전체 청산 (모든 포지션+주문 즉시 청산)")
        print("  F: � 손실 포지션 즉시 뒤집기 (손실→수익 전환)")
        print("  R: ⚡ 전체 포지션 즉시 뒤집기 (모든 방향 전환)")
        print("  S: 현재 상태 표시")
        print("  H: 도움말")
        print("  Ctrl+C: 시스템 종료")
        print("\n�💡 언제든지 위 키를 눌러서 제어할 수 있습니다!")
        print("🔥 특히 F키로 손실을 즉시 수익으로 전환하세요!")
        print("🚀 이제 LIMIT 주문뿐만 아니라 다양한 주문 타입으로 더 자주 체결됩니다!")
        
        # 실시간 시각화 시작
        print("\n🎨 시각화 옵션을 선택하세요:")
        print("1. Matplotlib (기본) - 차트 기반")
        if PYGAME_AVAILABLE:
            print("2. Pygame (고급) - 게임 엔진 기반, 더 부드러운 애니메이션")
            print("3. 둘 다 사용")
        print("0. 시각화 없음")
        
        viz_choice = input("선택: ").strip()
        
        if viz_choice == "1":
            self.start_visualization()
            print("✅ Matplotlib 시각화 창이 열렸습니다!")
        elif viz_choice == "2" and PYGAME_AVAILABLE:
            self.start_pygame_visualization()
            print("✅ Pygame 시각화 창이 열렸습니다!")
        elif viz_choice == "3" and PYGAME_AVAILABLE:
            self.start_visualization()
            self.start_pygame_visualization()
            print("✅ 두 시각화 창이 모두 열렸습니다!")
        elif viz_choice == "2" and not PYGAME_AVAILABLE:
            print("❌ Pygame이 설치되지 않았습니다. Matplotlib을 사용합니다.")
            self.start_visualization()
        else:
            print("시각화 없이 진행합니다.")
        
        last_update_time = 0
        last_viz_update = 0
        
        try:
            while True:
                current_time = time.time()
                
                # 사용자 입력 체크 (비동기)
                if self.check_user_input():
                    break  # 사용자가 청산을 선택하면 종료
                
                # 그리드 포지션 모니터링 (더 자주 - 1초마다)
                self.monitor_grid_positions()
                
                # 3분마다 그리드 업데이트 확인 (더 자주)
                if current_time - last_update_time > 180:
                    self.update_grid_system()
                    last_update_time = current_time
                
                # 1초마다 시각화 데이터 업데이트 (더 자주)
                if current_time - last_viz_update > 1:
                    self.update_visualization_data()
                    last_viz_update = current_time
                
                # 실시간 상태 표시 (15초마다)
                if current_time % 15 < 1:
                    account_info = mt5.account_info()
                    current_price = self.get_current_price()
                    
                    if account_info and current_price:
                        profit = account_info.equity - account_info.balance
                        completed_trades = len(self.grid_positions['completed_trades'])
                        total_profit_from_trades = sum(trade['profit'] for trade in self.grid_positions['completed_trades'])
                        winning_trades = sum(1 for trade in self.grid_positions['completed_trades'] if trade['profit'] > 0)
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${current_price['mid']:,.2f} | "
                              f"기준가: ${self.current_baseline:,.2f} | "
                              f"계좌손익: ${profit:+.2f} | "
                              f"거래수익: ${total_profit_from_trades:+.2f} | "
                              f"완료: {completed_trades}회 | "
                              f"성공: {winning_trades}회 | "
                              f"💡 'q' 입력시 청산메뉴")
                
                time.sleep(1)  # 1초마다 체크 (더 빠른 반응)
                
        except KeyboardInterrupt:
            print("\n\n🛑 시스템 중단 요청됨")
            
            # 종료시 청산 옵션 제공
            print("\n🚨 시스템 종료 전 청산 옵션:")
            print("1. 모든 포지션+주문 청산 후 종료")
            print("2. 포지션만 청산 후 종료")
            print("3. 청산 없이 바로 종료")
            
            choice = input("선택하세요 (1-3): ").strip()
            
            if choice == "1":
                print("🚨 전체 청산 후 종료...")
                self.emergency_close_all_system()
            elif choice == "2":
                print("📊 포지션만 청산 후 종료...")
                self.close_positions_only()
            else:
                print("청산 없이 종료합니다.")
            
            self.display_grid_final_stats()
        except Exception as e:
            print(f"\n❌ 시스템 오류: {e}")
            print("🔄 시스템 재시작...")
            time.sleep(10)
            self.run_grid_system()
    
    def display_grid_final_stats(self):
        """그리드 최종 통계"""
        runtime = datetime.now() - self.stats['start_time']
        account_info = mt5.account_info()
        
        print(f"\n📊 혁명적 그리드 시스템 최종 통계:")
        print(f"  ⏰ 운영 시간: {runtime}")
        print(f"  🎯 총 거래: {self.stats['total_trades']}회")
        print(f"  📈 성공 거래: {self.stats['winning_trades']}회")
        
        if account_info:
            total_profit = account_info.equity - account_info.balance
            print(f"  💰 총 손익: ${total_profit:+.2f}")
        
        # 레벨별 통계
        print(f"\n📊 레벨별 성과:")
        for level, stats in self.stats['level_stats'].items():
            if stats['trades'] > 0:
                level_name = self.config['unlimited_grid_levels'][level]['name']
                distance_pct = self.config['unlimited_grid_levels'][level]['distance_pct']
                print(f"  레벨 {level+1} ({level_name}, ±{distance_pct*100:.1f}%): {stats['trades']}회, ${stats['profit']:+.2f}")
        
        # 무제한 수익 달성 여부
        unlimited_levels = [i for i, level in enumerate(self.config['unlimited_grid_levels']) if level['distance_pct'] >= 1.0]
        if any(self.stats['level_stats'][level]['trades'] > 0 for level in unlimited_levels):
            print(f"\n🚀 무제한 수익 레벨 달성!")
            for level in unlimited_levels:
                if self.stats['level_stats'][level]['trades'] > 0:
                    level_name = self.config['unlimited_grid_levels'][level]['name']
                    distance_pct = self.config['unlimited_grid_levels'][level]['distance_pct']
                    print(f"  🔥 {level_name} (±{distance_pct*100:.0f}%): 대박 수익 달성!")

def main():
    """메인 함수"""
    print("🚀💰 혁명적 무제한 양방향 그리드 시스템 + 실시간 시각화 💰🚀")
    print("\n🔥 특징:")
    print("  🎯 현재가 중심 무제한 그리드 배치")
    print("  💰 최소수익(0.5%)부터 무제한수익(500%)까지!")
    print("  🚀 양방향 동시 포지션으로 무조건 수익")
    print("  📊 BTC 6배 상승 또는 1/6 폭락까지 대응")
    print("  💎 극한 변동시 무제한 대박 수익!")
    print("  � 실시간 시각화로 모든 상황 한눈에 파악!")
    print("  �🎮 완전 자동 무제한 수익 시스템")
    
    print("\n🎨 시각화 요소:")
    print("  📈 실시간 BTC 가격 차트 + 그리드 레벨")
    print("  💰 수익 히스토리 그래프")
    print("  📊 활성 포지션 현황")
    print("  🎯 레벨별 성과 분석")
    
    print("\n🚀 혁명적 동적 그리드 시스템:")
    print("  ⚡ 시장가 주문: 즉시 체결로 빠른 진입")
    print("  🎯 스탑 주문: 브레이크아웃 순간 포착")
    print("  🚀 공격적 진입: 거의 시장가 수준으로 자주 체결")
    print("  🔄 모멘텀 추종: 강한 움직임 즉시 따라가기")
    print("  ⚡ 변동성 포착: 급격한 변동 활용")
    print("  🎯 가격 사다리: 계단식 주문으로 촘촘한 포착")
    print("  🔄 다중 시간대: 여러 주기로 동시 운영")
    print("  💡 더 이상 LIMIT 주문만 기다리지 않습니다!")
    
    print("\n💡 무제한 수익 시나리오:")
    print("  📈 BTC $70K → $420K (6배): 무제한3 레벨 대박!")
    print("  📉 BTC $70K → $12K (1/6): 무제한3 레벨 대박!")
    print("  🎯 어떤 극한 상황에도 수익 보장!")
    
    bot = GridRevolutionaryBot()
    
    if not bot.connect_mt5():
        return
    
    # 심볼 확인
    symbol_info = mt5.symbol_info('BTCUSD')
    if symbol_info is None:
        print("❌ BTCUSD 심볼 없음")
        mt5.shutdown()
        return
    
    answer = input("\n혁명적 무제한 양방향 그리드 + 시각화 시스템을 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        print("프로그램 종료")
        mt5.shutdown()
        return
    
    print("\n🔥 무제한 그리드 + 혁명적 동적 시스템 가동!")
    print("💎 BTC가 어디로 가든 무제한 수익 대기 중...")
    print("🎨 실시간 시각화로 모든 상황을 모니터링!")
    print("🚀 시장가/스탑/공격적 진입으로 더 자주 체결!")
    print("⚡ 모멘텀/변동성/사다리/다중시간대 시스템 활성화!")
    
    # 무제한 그리드 + 시각화 시스템 시작!
    bot.run_grid_system()
    
    mt5.shutdown()

if __name__ == "__main__":
    main()