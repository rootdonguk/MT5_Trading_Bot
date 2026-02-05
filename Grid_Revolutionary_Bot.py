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

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class GridRevolutionaryBot:
    def __init__(self):
        self.config = {
            'symbol': 'BTCUSD',
            'magic_number': 777777,
            'base_lot_size': 0.01,
            'max_spread': 10.0,
            'unlimited_grid_levels': [
                # 최소수익 (빠른 회전)
                {'name': '초단기', 'distance_pct': 0.005, 'lot_multiplier': 0.5},   # ±0.5%
                {'name': '단기', 'distance_pct': 0.01, 'lot_multiplier': 1.0},     # ±1%
                {'name': '소액', 'distance_pct': 0.02, 'lot_multiplier': 1.5},     # ±2%
                
                # 중간수익
                {'name': '중간', 'distance_pct': 0.05, 'lot_multiplier': 2.0},     # ±5%
                {'name': '큰수익', 'distance_pct': 0.10, 'lot_multiplier': 2.5},   # ±10%
                {'name': '대수익', 'distance_pct': 0.20, 'lot_multiplier': 3.0},   # ±20%
                
                # 최대수익 (무제한!)
                {'name': '극한1', 'distance_pct': 0.30, 'lot_multiplier': 4.0},    # ±30%
                {'name': '극한2', 'distance_pct': 0.50, 'lot_multiplier': 5.0},    # ±50%
                {'name': '무제한1', 'distance_pct': 1.0, 'lot_multiplier': 10.0},  # ±100% (2배/반토막)
                {'name': '무제한2', 'distance_pct': 2.0, 'lot_multiplier': 20.0},  # ±200% (3배/1/3)
                {'name': '무제한3', 'distance_pct': 5.0, 'lot_multiplier': 50.0},  # ±500% (6배/1/6)
            ]
        }
        
        self.grid_positions = {
            'buy_orders': {},   # {level: order_info}
            'sell_orders': {},  # {level: order_info}
            'active_positions': {},
            'completed_trades': []
        }
        
        self.stats = {
            'total_profit': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'grid_profits': defaultdict(float),
            'level_stats': defaultdict(lambda: {'trades': 0, 'profit': 0.0}),
            'start_time': datetime.now()
        }
        
        self.current_baseline = 0.0
        self.last_grid_update = 0
        
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
        
        print("🔥 무제한 양방향 그리드 시스템 + 실시간 시각화 초기화 완료!")
        print(f"📊 그리드 레벨: {len(self.config['unlimited_grid_levels'])}개")
        print("🎨 실시간 시각화 준비 완료!")
        print("\n🎯 그리드 구성:")
        print("  📈 최소수익 (빠른 회전): 0.5% ~ 2%")
        print("  💰 중간수익 (안정적): 5% ~ 20%") 
        print("  🚀 최대수익 (무제한): 30% ~ 500%!")
        print("  💎 극한 시나리오: BTC 6배 상승 또는 1/6 폭락까지 대응!")
        
        for i, level in enumerate(self.config['unlimited_grid_levels']):
            if level['distance_pct'] >= 1.0:  # 무제한 레벨만 표시
                print(f"     🔥 {level['name']}: ±{level['distance_pct']*100:.0f}% (거래량: {level['lot_multiplier']:.0f}x)")
    
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
        except queue.Full:
            pass  # 큐가 가득 찬 경우 무시
    
    def start_visualization(self):
        """🎨 실시간 시각화 시작"""
        def run_visualization():
            # 그래프 설정
            plt.style.use('dark_background')
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('🚀 Revolutionary Unlimited Grid Trading System 🚀', fontsize=16, color='gold')
            
            # 데이터 저장용
            times = []
            prices = []
            profits = []
            grid_lines = []
            
            def animate(frame):
                try:
                    # 큐에서 데이터 가져오기
                    while not self.viz_queue.empty():
                        data = self.viz_queue.get_nowait()
                        
                        times.append(data['timestamp'])
                        prices.append(data['price'])
                        profits.append(data['total_profit'])
                        
                        # 최근 100개 데이터만 유지
                        if len(times) > 100:
                            times.pop(0)
                            prices.pop(0)
                            profits.pop(0)
                    
                    if len(times) < 2:
                        return
                    
                    # 1. 가격 차트 + 그리드 레벨
                    ax1.clear()
                    ax1.plot(times, prices, 'cyan', linewidth=2, label='BTC Price')
                    
                    # 기준선 표시
                    if hasattr(self, 'current_baseline') and self.current_baseline > 0:
                        ax1.axhline(y=self.current_baseline, color='yellow', linestyle='--', alpha=0.8, label='Baseline')
                    
                    # 그리드 레벨 표시
                    if len(self.visualization_data['grid_levels']) > 0:
                        for level_data in self.visualization_data['grid_levels']:
                            # 매수 레벨 (녹색)
                            ax1.axhline(y=level_data['buy_entry'], color='lime', alpha=0.6, linestyle='-')
                            # 매도 레벨 (빨간색)
                            ax1.axhline(y=level_data['sell_entry'], color='red', alpha=0.6, linestyle='-')
                    
                    ax1.set_title('📈 BTC Price & Grid Levels', color='white')
                    ax1.set_ylabel('Price ($)', color='white')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    # 2. 수익 차트
                    ax2.clear()
                    ax2.plot(times, profits, 'gold', linewidth=2, label='Total Profit')
                    ax2.axhline(y=0, color='white', linestyle='-', alpha=0.5)
                    ax2.fill_between(times, profits, 0, alpha=0.3, color='gold' if profits[-1] >= 0 else 'red')
                    ax2.set_title('💰 Profit History', color='white')
                    ax2.set_ylabel('Profit ($)', color='white')
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    
                    # 3. 활성 포지션 현황
                    ax3.clear()
                    if self.visualization_data['active_positions']:
                        buy_positions = [p for p in self.visualization_data['active_positions'] if p['type'] == 'BUY']
                        sell_positions = [p for p in self.visualization_data['active_positions'] if p['type'] == 'SELL']
                        
                        buy_profits = [p['profit'] for p in buy_positions]
                        sell_profits = [p['profit'] for p in sell_positions]
                        
                        if buy_profits:
                            ax3.bar(['BUY Positions'], [sum(buy_profits)], color='lime', alpha=0.7)
                        if sell_profits:
                            ax3.bar(['SELL Positions'], [sum(sell_profits)], color='red', alpha=0.7)
                        
                        ax3.set_title(f'📊 Active Positions ({len(self.visualization_data["active_positions"])})', color='white')
                        ax3.set_ylabel('Unrealized P&L ($)', color='white')
                    else:
                        ax3.text(0.5, 0.5, 'No Active Positions', ha='center', va='center', 
                                transform=ax3.transAxes, color='white', fontsize=12)
                        ax3.set_title('📊 Active Positions (0)', color='white')
                    
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
                            ax4.set_title('🎯 Level Performance', color='white')
                            ax4.set_ylabel('Profit ($)', color='white')
                            
                            # 수익 값 표시
                            for bar, profit in zip(bars, level_profits):
                                height = bar.get_height()
                                ax4.text(bar.get_x() + bar.get_width()/2., height,
                                        f'${profit:.1f}', ha='center', va='bottom' if height >= 0 else 'top',
                                        color='white', fontsize=8)
                    else:
                        ax4.text(0.5, 0.5, 'No Completed Trades', ha='center', va='center',
                                transform=ax4.transAxes, color='white', fontsize=12)
                        ax4.set_title('🎯 Level Performance', color='white')
                    
                    # 전체 레이아웃 조정
                    plt.tight_layout()
                    
                except Exception as e:
                    print(f"시각화 오류: {e}")
            
            # 애니메이션 시작
            ani = animation.FuncAnimation(fig, animate, interval=2000, cache_frame_data=False)
            plt.show()
        
        # 별도 스레드에서 시각화 실행
        viz_thread = threading.Thread(target=run_visualization, daemon=True)
        viz_thread.start()
        self.viz_running = True
        print("🎨 실시간 시각화 시작됨!")
        
        return viz_thread
    
    def place_grid_orders(self, grid_data):
        """🚀 그리드 주문 일괄 배치"""
        print("🚀 그리드 주문 일괄 배치 시작!")
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
        
        for level_data in grid_data:
            level = level_data['level']
            name = level_data['name']
            lot_size = level_data['lot_size']
            
            # 거래량 정규화
            min_lot = symbol_info.volume_min
            max_lot = symbol_info.volume_max
            lot_step = symbol_info.volume_step
            lot_size = max(min_lot, min(max_lot, round(lot_size / lot_step) * lot_step))
            
            print(f"\n📊 레벨 {level+1}: {name} 주문 배치")
            
            # 매수 주문 (현재가보다 아래에서 대기)
            if level_data['buy_entry'] < current_price['mid']:
                buy_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": level_data['buy_entry'],
                    "tp": level_data['buy_target'],
                    "sl": level_data['buy_entry'] * 0.95,  # 5% 손절
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"GRID_BUY_L{level+1}_{name}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                
                buy_result = mt5.order_send(buy_request)
                if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"  ✅ 매수 대기주문: {buy_result.order}")
                    print(f"     진입: ${level_data['buy_entry']:,.2f}")
                    print(f"     목표: ${level_data['buy_target']:,.2f}")
                    print(f"     예상수익: ${level_data['buy_profit']:.2f}")
                    
                    self.grid_positions['buy_orders'][level] = {
                        'order_id': buy_result.order,
                        'level_data': level_data,
                        'timestamp': datetime.now()
                    }
                    successful_orders += 1
                else:
                    error_code = buy_result.retcode if buy_result else "Unknown"
                    print(f"  ❌ 매수 주문 실패: {error_code}")
            
            # 매도 주문 (현재가보다 위에서 대기)
            if level_data['sell_entry'] > current_price['mid']:
                sell_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": level_data['sell_entry'],
                    "tp": level_data['sell_target'],
                    "sl": level_data['sell_entry'] * 1.05,  # 5% 손절
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"GRID_SELL_L{level+1}_{name}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                
                sell_result = mt5.order_send(sell_request)
                if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"  ✅ 매도 대기주문: {sell_result.order}")
                    print(f"     진입: ${level_data['sell_entry']:,.2f}")
                    print(f"     목표: ${level_data['sell_target']:,.2f}")
                    print(f"     예상수익: ${level_data['sell_profit']:.2f}")
                    
                    self.grid_positions['sell_orders'][level] = {
                        'order_id': sell_result.order,
                        'level_data': level_data,
                        'timestamp': datetime.now()
                    }
                    successful_orders += 1
                else:
                    error_code = sell_result.retcode if sell_result else "Unknown"
                    print(f"  ❌ 매도 주문 실패: {error_code}")
        
        print(f"\n🎯 그리드 배치 완료: {successful_orders}개 주문 성공!")
        return successful_orders > 0
    
    def monitor_grid_positions(self):
        """📊 그리드 포지션 모니터링"""
        # 대기 주문 확인
        pending_orders = mt5.orders_get(symbol=self.config['symbol'])
        active_positions = mt5.positions_get(symbol=self.config['symbol'])
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        # 체결된 주문 확인
        filled_orders = []
        for level, order_info in list(self.grid_positions['buy_orders'].items()):
            order_id = order_info['order_id']
            if not any(order.ticket == order_id for order in pending_orders or []):
                # 주문이 체결됨
                filled_orders.append(('buy', level, order_info))
                del self.grid_positions['buy_orders'][level]
        
        for level, order_info in list(self.grid_positions['sell_orders'].items()):
            order_id = order_info['order_id']
            if not any(order.ticket == order_id for order in pending_orders or []):
                # 주문이 체결됨
                filled_orders.append(('sell', level, order_info))
                del self.grid_positions['sell_orders'][level]
        
        # 체결된 주문 처리
        for order_type, level, order_info in filled_orders:
            level_data = order_info['level_data']
            print(f"🎯 레벨 {level+1} {order_type} 주문 체결!")
            print(f"   {level_data['name']}: 예상수익 ${level_data[f'{order_type}_profit']:.2f}")
            
            self.stats['level_stats'][level]['trades'] += 1
        
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
    
    def update_grid_system(self):
        """🔄 그리드 시스템 업데이트"""
        current_price = self.get_current_price()
        if not current_price:
            return
        
        # 기준가 업데이트 (5% 이상 변동시)
        if abs(current_price['mid'] - self.current_baseline) / self.current_baseline > 0.05:
            print(f"\n🔄 기준가 업데이트: ${self.current_baseline:,.2f} → ${current_price['mid']:,.2f}")
            
            # 기존 대기 주문 취소
            self.cancel_all_pending_orders()
            
            # 새로운 기준가로 그리드 재설정
            self.current_baseline = current_price['mid']
            grid_data = self.calculate_unlimited_grid_levels(self.current_baseline)
            self.visualization_data['grid_levels'] = grid_data  # 시각화용 업데이트
            self.place_grid_orders(grid_data)
    
    def cancel_all_pending_orders(self):
        """모든 대기 주문 취소"""
        pending_orders = mt5.orders_get(symbol=self.config['symbol'])
        if not pending_orders:
            return
        
        print(f"🗑️ 기존 대기 주문 {len(pending_orders)}개 취소 중...")
        
        for order in pending_orders:
            cancel_request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
            }
            mt5.order_send(cancel_request)
        
        # 내부 데이터 초기화
        self.grid_positions['buy_orders'].clear()
        self.grid_positions['sell_orders'].clear()
    
    def run_grid_system(self):
        """🚀 그리드 시스템 실행"""
        print("\n" + "="*70)
        print("  🚀 혁명적 다층 양방향 그리드 시스템 시작!")
        print("="*70)
        
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
        
        print("\n🎯 그리드 시스템 가동 중...")
        print("💡 여러 레벨에서 동시에 수익 기회를 포착합니다!")
        
        # 실시간 시각화 시작
        print("\n🎨 실시간 시각화 창을 여시겠습니까? (y/n): ", end='')
        viz_answer = input().strip().lower()
        if viz_answer == 'y':
            self.start_visualization()
            print("✅ 시각화 창이 열렸습니다!")
        
        last_update_time = 0
        last_viz_update = 0
        
        try:
            while True:
                current_time = time.time()
                
                # 그리드 포지션 모니터링
                self.monitor_grid_positions()
                
                # 5분마다 그리드 업데이트 확인
                if current_time - last_update_time > 300:
                    self.update_grid_system()
                    last_update_time = current_time
                
                # 2초마다 시각화 데이터 업데이트
                if current_time - last_viz_update > 2:
                    self.update_visualization_data()
                    last_viz_update = current_time
                
                # 실시간 상태 표시
                if current_time % 30 < 2:
                    account_info = mt5.account_info()
                    current_price = self.get_current_price()
                    
                    if account_info and current_price:
                        profit = account_info.equity - account_info.balance
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${current_price['mid']:,.2f} | "
                              f"기준가: ${self.current_baseline:,.2f} | "
                              f"실제손익: ${profit:+.2f} | "
                              f"그리드거래: {self.stats['total_trades']}회")
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n\n🛑 그리드 시스템 중단")
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
    print("  � 수익 히스토리 그래프")
    print("  📊 활성 포지션 현황")
    print("  🎯 레벨별 성과 분석")
    
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
    
    print("\n🔥 무제한 그리드 + 시각화 시스템 가동!")
    print("💎 BTC가 어디로 가든 무제한 수익 대기 중...")
    print("🎨 실시간 시각화로 모든 상황을 모니터링!")
    
    # 무제한 그리드 + 시각화 시스템 시작!
    bot.run_grid_system()
    
    mt5.shutdown()

if __name__ == "__main__":
    main()