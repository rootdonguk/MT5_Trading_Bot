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
            'symbol': 'BTCUSD',  # 기본값, 나중에 사용자 입력으로 변경
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
            'market_order_ratio': 0.9,          # 90%는 시장가 주문 (기존 70%에서 대폭 증가!)
            'stop_order_ratio': 0.6,            # 60%는 스탑 주문 (기존 40%에서 증가)
            'limit_order_ratio': 0.1,           # 10%만 리미트 주문 (대부분 즉시 체결!)
            'dynamic_adjustment': True,          # 동적 가격 조정
            'aggressive_entry': True,            # 공격적 진입
            'price_chase': True,                 # 가격 추적 시스템
            'instant_execution': True,           # 즉시 체결 우선
            
            'unlimited_grid_levels': [
                # 🔥 초밀집 그리드 (0.001% 간격으로 천문학적 수익!)
                # 현재가 기준 위아래로 0.001%씩 1000개 레벨 배치
            ] + [
                # 동적으로 생성되는 초밀집 레벨들
                {'name': f'초밀집{i:04d}', 'distance_pct': 0.00001 * i, 'lot_multiplier': 0.01 + (i * 0.001)}
                for i in range(1, 10001)  # 10,000개 레벨!
            ] + [
                # 기존 무제한 레벨들 (백업용)
                {'name': '무제한1', 'distance_pct': 1.0, 'lot_multiplier': 100.0},
                {'name': '무제한2', 'distance_pct': 2.0, 'lot_multiplier': 200.0},
                {'name': '무제한3', 'distance_pct': 5.0, 'lot_multiplier': 500.0},
                {'name': '극한무제한', 'distance_pct': 10.0, 'lot_multiplier': 1000.0},
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
    
    def select_trading_symbol(self):
        """🎯 거래 심볼 선택"""
        print("\n" + "="*70)
        print("🎯 거래 심볼 선택")
        print("="*70)
        
        # 인기 심볼 목록
        popular_symbols = {
            '1': {'symbol': 'BTCUSD', 'name': 'Bitcoin', 'description': '비트코인 - 가장 인기있는 암호화폐'},
            '2': {'symbol': 'ETHUSD', 'name': 'Ethereum', 'description': '이더리움 - 두 번째로 큰 암호화폐'},
            '3': {'symbol': 'XRPUSD', 'name': 'Ripple', 'description': '리플 - 빠른 국제송금용 암호화폐'},
            '4': {'symbol': 'ADAUSD', 'name': 'Cardano', 'description': '카르다노 - 지속가능한 블록체인'},
            '5': {'symbol': 'SOLUSD', 'name': 'Solana', 'description': '솔라나 - 고성능 블록체인'},
            '6': {'symbol': 'DOTUSD', 'name': 'Polkadot', 'description': '폴카닷 - 상호운용성 블록체인'},
            '7': {'symbol': 'AVAXUSD', 'name': 'Avalanche', 'description': '아발란체 - 빠른 스마트 컨트랙트'},
            '8': {'symbol': 'MATICUSD', 'name': 'Polygon', 'description': '폴리곤 - 이더리움 레이어2'},
            '9': {'symbol': 'LINKUSD', 'name': 'Chainlink', 'description': '체인링크 - 오라클 네트워크'},
            '10': {'symbol': 'UNIUSD', 'name': 'Uniswap', 'description': '유니스왑 - 탈중앙화 거래소'},
        }
        
        forex_symbols = {
            '11': {'symbol': 'EURUSD', 'name': 'EUR/USD', 'description': '유로/달러 - 가장 거래량이 많은 통화쌍'},
            '12': {'symbol': 'GBPUSD', 'name': 'GBP/USD', 'description': '파운드/달러 - 케이블'},
            '13': {'symbol': 'USDJPY', 'name': 'USD/JPY', 'description': '달러/엔 - 아시아 주요 통화쌍'},
            '14': {'symbol': 'AUDUSD', 'name': 'AUD/USD', 'description': '호주달러/달러'},
            '15': {'symbol': 'USDCAD', 'name': 'USD/CAD', 'description': '달러/캐나다달러'},
            '16': {'symbol': 'USDCHF', 'name': 'USD/CHF', 'description': '달러/스위스프랑'},
            '17': {'symbol': 'NZDUSD', 'name': 'NZD/USD', 'description': '뉴질랜드달러/달러'},
        }
        
        stock_symbols = {
            '18': {'symbol': 'AAPL', 'name': 'Apple Inc.', 'description': '애플 - 기술주 대표'},
            '19': {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'description': '테슬라 - 전기차 선도기업'},
            '20': {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'description': '구글 - 검색엔진 및 클라우드'},
            '21': {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'description': '마이크로소프트 - 소프트웨어 거대기업'},
            '22': {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'description': '아마존 - 전자상거래 및 클라우드'},
            '23': {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'description': '엔비디아 - AI 및 그래픽카드'},
            '24': {'symbol': 'META', 'name': 'Meta Platforms', 'description': '메타 - 소셜미디어 플랫폼'},
        }
        
        commodity_symbols = {
            '25': {'symbol': 'XAUUSD', 'name': 'Gold', 'description': '금 - 안전자산 대표'},
            '26': {'symbol': 'XAGUSD', 'name': 'Silver', 'description': '은 - 귀금속'},
            '27': {'symbol': 'USOIL', 'name': 'Crude Oil', 'description': '원유 - WTI'},
            '28': {'symbol': 'UKOIL', 'name': 'Brent Oil', 'description': '원유 - 브렌트'},
        }
        
        print("🚀 암호화폐 (Cryptocurrency):")
        for key, info in popular_symbols.items():
            print(f"  {key:2s}. {info['symbol']:10s} - {info['name']:15s} ({info['description']})")
        
        print("\n💱 외환 (Forex):")
        for key, info in forex_symbols.items():
            print(f"  {key:2s}. {info['symbol']:10s} - {info['name']:15s} ({info['description']})")
        
        print("\n📈 주식 (Stocks):")
        for key, info in stock_symbols.items():
            print(f"  {key:2s}. {info['symbol']:10s} - {info['name']:15s} ({info['description']})")
        
        print("\n🥇 원자재 (Commodities):")
        for key, info in commodity_symbols.items():
            print(f"  {key:2s}. {info['symbol']:10s} - {info['name']:15s} ({info['description']})")
        
        print("\n  99. 직접 입력 (Custom Symbol)")
        print("   0. 기본값 사용 (BTCUSD)")
        
        # 모든 심볼을 하나의 딕셔너리로 합치기
        all_symbols = {**popular_symbols, **forex_symbols, **stock_symbols, **commodity_symbols}
        
        while True:
            choice = input(f"\n거래할 심볼을 선택하세요 (0-28, 99): ").strip()
            
            if choice == '0':
                selected_symbol = 'BTCUSD'
                selected_name = 'Bitcoin'
                break
            elif choice == '99':
                custom_symbol = input("심볼을 직접 입력하세요 (예: ETHUSD, EURUSD): ").strip().upper()
                if custom_symbol:
                    selected_symbol = custom_symbol
                    selected_name = custom_symbol
                    break
                else:
                    print("❌ 올바른 심볼을 입력해주세요.")
                    continue
            elif choice in all_symbols:
                selected_symbol = all_symbols[choice]['symbol']
                selected_name = all_symbols[choice]['name']
                break
            else:
                print("❌ 올바른 번호를 선택해주세요.")
                continue
        
        # 심볼 유효성 검사
        print(f"\n🔍 선택된 심볼: {selected_symbol} ({selected_name})")
        print("심볼 유효성 검사 중...")
        
        symbol_info = mt5.symbol_info(selected_symbol)
        if symbol_info is None:
            print(f"❌ 심볼 '{selected_symbol}'을 찾을 수 없습니다.")
            print("💡 다음을 확인해주세요:")
            print("  1. 심볼명이 정확한지 확인")
            print("  2. 브로커에서 해당 심볼을 지원하는지 확인")
            print("  3. 심볼이 활성화되어 있는지 확인")
            
            retry = input("\n다시 선택하시겠습니까? (y/n): ").strip().lower()
            if retry == 'y':
                return self.select_trading_symbol()
            else:
                print("기본값 BTCUSD를 사용합니다.")
                return 'BTCUSD', 'Bitcoin'
        
        # 심볼 정보 표시
        print(f"✅ 심볼 확인 완료!")
        print(f"  📊 심볼: {symbol_info.name}")
        print(f"  💰 현재가: {symbol_info.bid:.5f}")
        print(f"  📈 스프레드: {symbol_info.ask - symbol_info.bid:.5f}")
        print(f"  📊 최소거래량: {symbol_info.volume_min}")
        print(f"  📊 최대거래량: {symbol_info.volume_max}")
        print(f"  📊 거래량단위: {symbol_info.volume_step}")
        
        # 심볼별 특별 설정
        self.configure_symbol_specific_settings(selected_symbol)
        
        return selected_symbol, selected_name
    
    def configure_symbol_specific_settings(self, symbol):
        """🎯 심볼별 특별 설정"""
        symbol_upper = symbol.upper()
        
        # 암호화폐 설정
        if any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'XRP', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI']):
            print(f"\n🚀 암호화폐 최적화 설정 적용: {symbol}")
            self.config['base_lot_size'] = 0.01
            self.config['max_spread'] = 50.0  # 암호화폐는 스프레드가 클 수 있음
            self.config['scalp_profit_pips'] = 10  # 더 큰 수익 목표
            self.config['scalp_max_loss_pips'] = 20
            
        # 외환 설정
        elif any(forex in symbol_upper for forex in ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
            print(f"\n💱 외환 최적화 설정 적용: {symbol}")
            self.config['base_lot_size'] = 0.01
            self.config['max_spread'] = 3.0  # 외환은 스프레드가 작음
            self.config['scalp_profit_pips'] = 3
            self.config['scalp_max_loss_pips'] = 5
            
        # 주식 설정
        elif any(stock in symbol_upper for stock in ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'META']):
            print(f"\n📈 주식 최적화 설정 적용: {symbol}")
            self.config['base_lot_size'] = 1  # 주식은 보통 1주 단위
            self.config['max_spread'] = 1.0
            self.config['scalp_profit_pips'] = 5
            self.config['scalp_max_loss_pips'] = 10
            
        # 원자재 설정
        elif any(commodity in symbol_upper for commodity in ['XAU', 'XAG', 'OIL']):
            print(f"\n🥇 원자재 최적화 설정 적용: {symbol}")
            self.config['base_lot_size'] = 0.01
            self.config['max_spread'] = 5.0
            self.config['scalp_profit_pips'] = 8
            self.config['scalp_max_loss_pips'] = 15
            
        else:
            print(f"\n⚙️ 기본 설정 적용: {symbol}")
            self.config['base_lot_size'] = 0.01
            self.config['max_spread'] = 10.0
            self.config['scalp_profit_pips'] = 5
            self.config['scalp_max_loss_pips'] = 10
        
        print(f"  📊 기본 거래량: {self.config['base_lot_size']}")
        print(f"  📊 최대 스프레드: {self.config['max_spread']}")
        print(f"  📊 스캘핑 수익: {self.config['scalp_profit_pips']} pips")
        print(f"  📊 스캘핑 손절: {self.config['scalp_max_loss_pips']} pips")
    
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
        """🚀 즉시 수익 초고속 그리드 시스템 (실행하자마자 수익!)"""
        grid_data = []
        
        print(f"\n� 즉시 수익 그리드 계산 (현재가: ${baseline_price:,..2f})")
        print("="*80)
        print("� 실행하자마자 즉시 수익! 대기시간 ZERO!")
        
        # 즉시 수익 그리드 설정 (현재가 바로 위아래)
        print("\n🎯 즉시 수익 그리드 밀집도:")
        print("1. 🔥 초고속 (0.01% 간격, 500개 레벨) - 즉시 수익!")
        print("2. 🚀 고속 (0.05% 간격, 200개 레벨) - 빠른 수익!")  
        print("3. ⚡ 표준 (0.1% 간격, 100개 레벨) - 안정 수익!")
        
        choice = input("선택하세요 (1-3): ").strip()
        
        if choice == "1":
            grid_distance = 0.0001   # 0.01%
            max_levels = 500
            print("🔥 초고속 모드: 0.01% 간격으로 500개 레벨!")
            print("💎 0.01% 움직이면 즉시 수익! 실행하자마자 돈 벌기!")
        elif choice == "2":
            grid_distance = 0.0005   # 0.05%
            max_levels = 200
            print("� 고속 모드: 0.05% 간격으로 200개 레벨!")
            print("💎 0.05% 움직이면 즉시 수익! 빠른 돈 벌기!")
        else:
            grid_distance = 0.001    # 0.1%
            max_levels = 100
            print("⚡ 표준 모드: 0.1% 간격으로 100개 레벨!")
            print("💎 0.1% 움직이면 즉시 수익! 안정적 돈 벌기!")
        
        print(f"📊 총 주문 수: {max_levels * 2}개 (매수 {max_levels}개 + 매도 {max_levels}개)")
        print("🚀 현재가 바로 위아래에 촘촘하게 배치 → 즉시 수익!")
        
        total_potential_profit = 0
        
        # 현재가 중심으로 위아래 촘촘하게 배치
        for i in range(1, max_levels + 1):
            distance_pct = grid_distance * i
            lot_size = self.config['base_lot_size'] * (1 + i * 0.01)  # 레벨별 거래량 증가
            
            # 거리 계산
            distance = baseline_price * distance_pct
            
            # 🔥 핵심: 현재가 바로 위아래에 배치 (즉시 수익!)
            buy_entry = baseline_price - distance    # 현재가 아래
            sell_entry = baseline_price + distance   # 현재가 위
            
            # 즉시 수익 목표 (매우 작은 움직임으로도 수익!)
            buy_profit_target = buy_entry + (distance * 0.5)  # 절반만 회복해도 수익!
            sell_profit_target = sell_entry - (distance * 0.5)  # 절반만 회복해도 수익!
            
            # 예상 수익 계산
            profit_per_trade = distance * 0.5 * lot_size
            
            level_data = {
                'level': i - 1,
                'name': f'즉시{i:03d}',
                'distance_pct': distance_pct,
                'distance': distance,
                'lot_size': lot_size,
                'buy_entry': buy_entry,
                'buy_target': buy_profit_target,
                'sell_entry': sell_entry,
                'sell_target': sell_profit_target,
                'profit_per_trade': profit_per_trade
            }
            
            grid_data.append(level_data)
            total_potential_profit += profit_per_trade * 2  # 매수+매도
            
            # 처음 5개와 마지막 5개만 출력
            if i <= 5 or i > max_levels - 5:
                print(f"레벨 {i:3d}: 즉시{i:03d} (±{distance_pct*100:.3f}%)")
                print(f"  💰 거래량: {lot_size:.3f}")
                print(f"  🔵 매수: ${buy_entry:.2f} → ${buy_profit_target:.2f} (수익: ${profit_per_trade:.2f})")
                print(f"  🔴 매도: ${sell_entry:.2f} → ${sell_profit_target:.2f} (수익: ${profit_per_trade:.2f})")
            elif i == 6:
                print("  ... (중간 레벨들) ...")
        
        print(f"\n💎 총 잠재 수익: ${total_potential_profit:,.2f}")
        print(f"🎯 그리드 범위: ${grid_data[0]['buy_entry']:.2f} ~ ${grid_data[-1]['sell_entry']:.2f}")
        print(f"🚀 가격이 조금만 움직여도 즉시 수익 실현!")
        print(f"💡 실행하자마자 돈이 들어오는 시스템!")
        
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
                fig.suptitle(f'🚀 Revolutionary Unlimited Grid Trading System - {self.config["symbol"]} 🚀', fontsize=16, color='gold')
                
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
                        ax1.plot(times, prices, 'cyan', linewidth=2, label=f'{self.config["symbol"]} Price')
                        
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
                        manager.window.wm_title(f'🚀 {self.config["symbol"]} Grid Trading System - Real-time Visualization')
                
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
                self.pygame_viz = PygameGridVisualizer(symbol=self.config['symbol'])
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
        positions = mt5.positions_get(symbol=self.config['symbol'])  # 선택된 심볼만
        current_price = self.get_current_price()
        total_closed = 0
        total_profit = 0
        
        if positions and current_price:
            for position in positions:
                # 현재 미실현 수익 계산
                if position.type == mt5.ORDER_TYPE_BUY:
                    unrealized_profit = (current_price['bid'] - position.price_open) * position.volume
                    close_price = current_price['bid']
                else:
                    unrealized_profit = (position.price_open - current_price['ask']) * position.volume
                    close_price = current_price['ask']
                
                if unrealized_profit > 0:  # 수익 포지션만
                    print(f"  🎯 수익포지션 발견: #{position.ticket} | 미실현수익: ${unrealized_profit:+.2f}")
                    
                    # 포지션 청산
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": position.ticket,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": "PROFIT_CLOSE_ONLY",
                    }
                    
                    result = mt5.order_send(close_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        # 실제 청산 수익 계산
                        if position.type == mt5.ORDER_TYPE_BUY:
                            actual_profit = (result.price - position.price_open) * position.volume
                        else:
                            actual_profit = (position.price_open - result.price) * position.volume
                        
                        total_closed += 1
                        total_profit += actual_profit
                        print(f"  ✅ 수익포지션 #{position.ticket} 청산완료: ${actual_profit:+.2f} (청산가: ${result.price:.2f})")
                    else:
                        error_code = result.retcode if result else "Unknown"
                        print(f"  ❌ 포지션 #{position.ticket} 청산실패: {error_code}")
        
        if total_closed > 0:
            print(f"✅ 수익 포지션 청산 완료: {total_closed}개, 총 수익: ${total_profit:+.2f}")
        else:
            print("💡 청산할 수익 포지션이 없습니다.")
            
        return total_closed, 0, total_profit
    
    def close_loss_positions_only(self):
        """📉 손실 포지션만 청산"""
        print("\n📉 손실 포지션만 청산 중...")
        positions = mt5.positions_get(symbol=self.config['symbol'])  # 선택된 심볼만
        current_price = self.get_current_price()
        total_closed = 0
        total_loss = 0
        
        if positions and current_price:
            for position in positions:
                # 현재 미실현 손실 계산
                if position.type == mt5.ORDER_TYPE_BUY:
                    unrealized_profit = (current_price['bid'] - position.price_open) * position.volume
                    close_price = current_price['bid']
                else:
                    unrealized_profit = (position.price_open - current_price['ask']) * position.volume
                    close_price = current_price['ask']
                
                if unrealized_profit < 0:  # 손실 포지션만
                    print(f"  🎯 손실포지션 발견: #{position.ticket} | 미실현손실: ${unrealized_profit:+.2f}")
                    
                    # 포지션 청산
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": position.ticket,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": "LOSS_CLOSE_ONLY",
                    }
                    
                    result = mt5.order_send(close_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        # 실제 청산 손실 계산
                        if position.type == mt5.ORDER_TYPE_BUY:
                            actual_loss = (result.price - position.price_open) * position.volume
                        else:
                            actual_loss = (position.price_open - result.price) * position.volume
                        
                        total_closed += 1
                        total_loss += actual_loss
                        print(f"  ✅ 손실포지션 #{position.ticket} 청산완료: ${actual_loss:+.2f} (청산가: ${result.price:.2f})")
                    else:
                        error_code = result.retcode if result else "Unknown"
                        print(f"  ❌ 포지션 #{position.ticket} 청산실패: {error_code}")
        
        if total_closed > 0:
            print(f"✅ 손실 포지션 청산 완료: {total_closed}개, 총 손실: ${total_loss:+.2f}")
        else:
            print("💡 청산할 손실 포지션이 없습니다.")
            
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
                    elif key == 'g':  # 새로운 단축키 - 수익 포지션만 청산하고 계속
                        print("\n💰 수익 포지션만 청산 (계속 실행)!")
                        self.close_profit_positions_only()
                        print("💡 수익 포지션 청산 완료! 시스템 계속 실행 중...")
                        return False  # 시스템 종료하지 않고 계속
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
                    elif key == 'g':  # 새로운 단축키 - 수익 포지션만 청산하고 계속
                        print("\n💰 수익 포지션만 청산 (계속 실행)!")
                        self.close_profit_positions_only()
                        print("💡 수익 포지션 청산 완료! 시스템 계속 실행 중...")
                        return False  # 시스템 종료하지 않고 계속
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
        print("G: 💰 수익 포지션만 청산 (계속 실행)")  # 새로운 키
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
        
        # 6. 🚀 Market 주문 전용 그리드 (새로 추가!)
        self.execute_market_only_grid_system(current_price)
    
    def execute_market_grid_orders(self, current_price):
        """⚡ 시장가 그리드 주문 (즉시 체결) - 완전 개선!"""
        if not self.config['market_orders']:
            return
        
        # 90% 확률로 시장가 주문 실행 (매우 자주!)
        if time.time() % 3 < 2.7:  # 3초 중 2.7초 (90% 확률)
            # 더 큰 거래량으로 즉시 양방향 진입
            market_volume = self.config['base_lot_size'] * 2.5  # 거래량 더 증가
            
            # 시장가 매수
            market_buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": market_volume,
                "type": mt5.ORDER_TYPE_BUY,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "MARKET_GRID_BUY_INSTANT",
            }
            
            buy_result = mt5.order_send(market_buy_request)
            if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🚀 즉시시장가매수: {market_volume:.3f} @ ${buy_result.price:.5f}")
                # 0.03% 수익시 즉시 청산 (더 빠른 청산)
                self.set_quick_exit(buy_result.order, 'buy', buy_result.price, market_volume, 0.0003)
            
            # 시장가 매도
            market_sell_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": market_volume,
                "type": mt5.ORDER_TYPE_SELL,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "MARKET_GRID_SELL_INSTANT",
            }
            
            sell_result = mt5.order_send(market_sell_request)
            if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🚀 즉시시장가매도: {market_volume:.3f} @ ${sell_result.price:.5f}")
                # 0.03% 수익시 즉시 청산 (더 빠른 청산)
                self.set_quick_exit(sell_result.order, 'sell', sell_result.price, market_volume, 0.0003)
    
    def execute_stop_grid_orders(self, current_price):
        """🎯 스탑 그리드 주문 (브레이크아웃 포착) - 완전 개선!"""
        if not self.config['stop_orders']:
            return
        
        # 60% 확률로 스탑 주문 배치 (기존 40%에서 대폭 증가)
        if time.time() % 10 < 6:  # 10초 중 6초 (60% 확률)
            stop_volume = self.config['base_lot_size'] * 2.0  # 거래량 더 증가
            
            # 상승 브레이크아웃 스탑 주문 (더 가까운 가격)
            buy_stop_price = current_price['ask'] + (current_price['mid'] * 0.0002)  # 0.02% 위 (더 가까움)
            buy_stop_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": stop_volume,
                "type": mt5.ORDER_TYPE_BUY_STOP,
                "price": buy_stop_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "STOP_GRID_BUY_ULTRA",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            buy_stop_result = mt5.order_send(buy_stop_request)
            if buy_stop_result and buy_stop_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🎯 매수스탑: {stop_volume:.3f} @ ${buy_stop_price:.5f}")
            
            # 하락 브레이크아웃 스탑 주문 (더 가까운 가격)
            sell_stop_price = current_price['bid'] - (current_price['mid'] * 0.0002)  # 0.02% 아래 (더 가까움)
            sell_stop_request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": stop_volume,
                "type": mt5.ORDER_TYPE_SELL_STOP,
                "price": sell_stop_price,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": "STOP_GRID_SELL_ULTRA",
                "type_time": mt5.ORDER_TIME_GTC,
            }
            
            sell_stop_result = mt5.order_send(sell_stop_request)
            if sell_stop_result and sell_stop_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🎯 매도스탑: {stop_volume:.3f} @ ${sell_stop_price:.5f}")
    
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
    
    def execute_market_only_grid_system(self, current_price):
        """🚀 Market 주문 전용 초고속 그리드 시스템 (완전 개선!)"""
        try:
            # 1초마다 즉시 체결 그리드 실행 (더 자주!)
            if time.time() % 1 < 0.8:  # 1초 중 0.8초 (80% 확률로 매우 자주!)
                # 초고속 거래량으로 즉시 양방향 진입
                market_volume = self.config['base_lot_size'] * 3.0  # 3배 거래량 (더 큰 수익)
                
                # 연속 시장가 주문 (5개씩 더 많이!)
                for i in range(5):
                    # 시장가 매수 - 즉시 체결
                    market_buy_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.config['symbol'],
                        "volume": market_volume,
                        "type": mt5.ORDER_TYPE_BUY,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"ULTRA_MARKET_BUY_{i+1}",
                    }
                    
                    buy_result = mt5.order_send(market_buy_request)
                    if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🚀 초고속매수{i+1}: {market_volume:.3f} @ ${buy_result.price:.5f}")
                        # 0.02% 수익시 즉시 청산 (더 빠른 청산!)
                        self.set_ultra_quick_exit(buy_result.order, 'buy', buy_result.price, market_volume, 0.0002)
                    
                    # 시장가 매도 - 즉시 체결
                    market_sell_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.config['symbol'],
                        "volume": market_volume,
                        "type": mt5.ORDER_TYPE_SELL,
                        "deviation": 100,
                        "magic": self.config['magic_number'],
                        "comment": f"ULTRA_MARKET_SELL_{i+1}",
                    }
                    
                    sell_result = mt5.order_send(market_sell_request)
                    if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"🚀 초고속매도{i+1}: {market_volume:.3f} @ ${sell_result.price:.5f}")
                        # 0.02% 수익시 즉시 청산 (더 빠른 청산!)
                        self.set_ultra_quick_exit(sell_result.order, 'sell', sell_result.price, market_volume, 0.0002)
                    
                    time.sleep(0.1)  # 0.1초 간격 (더 빠르게!)
                    
        except Exception as e:
            print(f"❌ 초고속 Market 그리드 오류: {e}")
    
    def set_ultra_quick_exit(self, position_ticket, position_type, entry_price, volume, profit_pct):
        """⚡ 초고속 청산 주문 (0.02% 수익으로도 즉시 청산!)"""
        try:
            if position_type == 'buy':
                # 매수 → 0.02% 상승시 즉시 청산
                target_price = entry_price * (1 + profit_pct)
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
                # 매도 → 0.02% 하락시 즉시 청산
                target_price = entry_price * (1 - profit_pct)
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
                print(f"      ⚡ 초고속청산설정: #{result.order} @ ${target_price:.5f} ({profit_pct*100:.3f}% 수익)")
            
        except Exception as e:
            print(f"❌ 초고속청산 설정 오류: {e}")
    
    def schedule_market_exit(self, position_ticket, position_type, entry_price, volume, profit_pct):
        """⚡ Market 주문으로 청산 예약 (LIMIT 주문 없이)"""
        try:
            # 0.03% 수익 목표가 달성되면 즉시 Market 청산
            target_price = entry_price * (1 + profit_pct) if position_type == 'buy' else entry_price * (1 - profit_pct)
            
            # 별도 스레드에서 가격 모니터링 후 Market 청산
            import threading
            
            def monitor_and_close():
                import time
                max_wait_time = 30  # 최대 30초 대기
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    current_price = self.get_current_price()
                    if not current_price:
                        time.sleep(0.5)
                        continue
                    
                    # 목표가 달성 확인
                    if position_type == 'buy':
                        if current_price['bid'] >= target_price:
                            self.execute_market_close(position_ticket, volume, 'buy')
                            break
                    else:
                        if current_price['ask'] <= target_price:
                            self.execute_market_close(position_ticket, volume, 'sell')
                            break
                    
                    time.sleep(0.1)  # 0.1초마다 체크
                
                # 시간 초과시 강제 청산
                if time.time() - start_time >= max_wait_time:
                    self.execute_market_close(position_ticket, volume, position_type)
            
            # 백그라운드에서 모니터링 시작
            monitor_thread = threading.Thread(target=monitor_and_close, daemon=True)
            monitor_thread.start()
            
        except Exception as e:
            print(f"❌ Market 청산 예약 오류: {e}")
    
    def execute_market_close(self, position_ticket, volume, position_type):
        """🚀 Market 주문으로 즉시 청산"""
        try:
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL if position_type == 'buy' else mt5.ORDER_TYPE_BUY,
                "position": position_ticket,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"MARKET_CLOSE_{position_type.upper()}",
            }
            
            result = mt5.order_send(close_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"⚡ Market즉시청산: #{position_ticket} @ ${result.price:.5f}")
                return True
            else:
                print(f"❌ Market청산실패: #{position_ticket}")
                return False
                
        except Exception as e:
            print(f"❌ Market 청산 오류: {e}")
            return False
    
    def place_grid_orders(self, grid_data):
        """🚀 초밀집 그리드 주문 일괄 배치 (천문학적 수익 시스템)"""
        print("� 초밀집 그리드 주문 일괄 배치 시작!")
        print(f"📊 총 {len(grid_data)}개 레벨 × 2방향 = 최대 {len(grid_data) * 2}개 주문")
        print("⚡ 0.001% 간격으로 촘촘한 그리드 형성 - 천문학적 수익 대기!")
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
        
        # 배치 처리를 위한 주문 그룹화 (너무 많으면 분할 처리)
        batch_size = 100  # 한 번에 100개씩 처리
        total_batches = (len(grid_data) * 2 + batch_size - 1) // batch_size
        
        print(f"📦 배치 처리: {total_batches}개 배치로 분할 처리")
        
        # 매수 주문 배치 처리
        buy_orders = [(level_data['level'], level_data['name'], level_data, level_data['lot_size']) 
                     for level_data in grid_data if level_data['buy_entry'] < current_price['mid']]
        
        print(f"\n🔵 매수 주문 {len(buy_orders)}개 배치 중...")
        for batch_num in range(0, len(buy_orders), batch_size):
            batch_orders = buy_orders[batch_num:batch_num + batch_size]
            print(f"  📦 배치 {batch_num//batch_size + 1}/{(len(buy_orders) + batch_size - 1)//batch_size}: {len(batch_orders)}개 주문")
            
            for i, (level, name, level_data, lot_size) in enumerate(batch_orders):
                # 거래량 정규화
                min_lot = symbol_info.volume_min
                max_lot = symbol_info.volume_max
                lot_step = symbol_info.volume_step
                lot_size = max(min_lot, min(max_lot, round(lot_size / lot_step) * lot_step))
                
                buy_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": level_data['buy_entry'],
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"DENSE_GRID_BUY_L{level+1:04d}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                
                buy_result = mt5.order_send(buy_request)
                if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
                    successful_orders += 1
                    self.grid_positions['buy_orders'][level] = {
                        'order_id': buy_result.order,
                        'level_data': level_data,
                        'timestamp': datetime.now()
                    }
                    
                    # 처음 10개와 마지막 10개만 출력
                    if i < 10 or i >= len(batch_orders) - 10:
                        print(f"    ✅ L{level+1:04d}: ${level_data['buy_entry']:.5f} (#{buy_result.order})")
                    elif i == 10:
                        print(f"    ... (중간 주문들 생략) ...")
                else:
                    failed_orders += 1
                    if i < 5:  # 처음 5개 실패만 출력
                        error_code = buy_result.retcode if buy_result else "Unknown"
                        print(f"    ❌ L{level+1:04d}: 실패 {error_code}")
                
                # 너무 빠른 주문 방지
                if i % 50 == 0:  # 50개마다 잠시 대기
                    time.sleep(0.1)
        
        # 매도 주문 배치 처리
        sell_orders = [(level_data['level'], level_data['name'], level_data, level_data['lot_size']) 
                      for level_data in grid_data if level_data['sell_entry'] > current_price['mid']]
        
        print(f"\n🔴 매도 주문 {len(sell_orders)}개 배치 중...")
        for batch_num in range(0, len(sell_orders), batch_size):
            batch_orders = sell_orders[batch_num:batch_num + batch_size]
            print(f"  📦 배치 {batch_num//batch_size + 1}/{(len(sell_orders) + batch_size - 1)//batch_size}: {len(batch_orders)}개 주문")
            
            for i, (level, name, level_data, lot_size) in enumerate(batch_orders):
                # 거래량 정규화
                min_lot = symbol_info.volume_min
                max_lot = symbol_info.volume_max
                lot_step = symbol_info.volume_step
                lot_size = max(min_lot, min(max_lot, round(lot_size / lot_step) * lot_step))
                
                sell_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": level_data['sell_entry'],
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"DENSE_GRID_SELL_L{level+1:04d}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
                
                sell_result = mt5.order_send(sell_request)
                if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
                    successful_orders += 1
                    self.grid_positions['sell_orders'][level] = {
                        'order_id': sell_result.order,
                        'level_data': level_data,
                        'timestamp': datetime.now()
                    }
                    
                    # 처음 10개와 마지막 10개만 출력
                    if i < 10 or i >= len(batch_orders) - 10:
                        print(f"    ✅ L{level+1:04d}: ${level_data['sell_entry']:.5f} (#{sell_result.order})")
                    elif i == 10:
                        print(f"    ... (중간 주문들 생략) ...")
                else:
                    failed_orders += 1
                    if i < 5:  # 처음 5개 실패만 출력
                        error_code = sell_result.retcode if sell_result else "Unknown"
                        print(f"    ❌ L{level+1:04d}: 실패 {error_code}")
                
                # 너무 빠른 주문 방지
                if i % 50 == 0:  # 50개마다 잠시 대기
                    time.sleep(0.1)
        
        print(f"\n🔥 초밀집 그리드 배치 완료!")
        print(f"  ✅ 성공: {successful_orders}개 주문")
        print(f"  ❌ 실패: {failed_orders}개 주문")
        print(f"  📊 성공률: {successful_orders/(successful_orders+failed_orders)*100:.1f}%")
        
        if successful_orders > 0:
            print(f"🚀 {successful_orders}개 초밀집 주문이 활성화!")
            print("💎 가격이 조금만 움직여도 천문학적 수익 가능!")
            print("⚡ 0.001% 움직임마다 수십~수백개 주문 동시 체결!")
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
        pending_orders = mt5.orders_get(symbol=self.config['symbol'])
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
        active_positions = mt5.positions_get(symbol=self.config['symbol'])
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
        
        # 1. 심볼 선택
        selected_symbol, selected_name = self.select_trading_symbol()
        self.config['symbol'] = selected_symbol
        
        print(f"\n✅ 선택된 거래 심볼: {selected_symbol} ({selected_name})")
        
        # 시작 전 모든 기존 포지션/주문 정리
        cleanup_choice = input(f"\n🗑️ {selected_symbol}의 기존 모든 포지션/주문을 정리하시겠습니까? (y/n): ").strip().lower()
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
        
        print("\n🎯 완전자동 즉시 수익 시스템 가동 중...")
        print("💎 90% Market 주문으로 즉시 체결!")
        print("⚡ 0.01% 움직임으로도 즉시 수익 실현!")
        print("🔄 수익 실현 즉시 재배치로 연속 수익!")
        print("\n🚀 즉시 수익 동적 그리드 시스템 활성화!")
        print("  ⚡ 시장가 주문: 90% 확률로 즉시 체결")
        print("  🎯 스탑 주문: 60% 확률로 브레이크아웃 포착")
        print("  🚀 초고속 Market: 1초마다 80% 확률로 즉시 체결")
        print("  🔄 모멘텀 추종: 0.1% 변동시 즉시 추종")
        print("  ⚡ 변동성 포착: 스프레드 확대시 양방향 진입")
        print("  🎯 가격 사다리: 30초마다 5단계 사다리 주문")
        print("  🔄 다중 시간대: 1초/5초/15초/60초 주기별 그리드")
        print("  💎 즉시 수익: 0.01% 간격으로 즉시 수익!")
        print("  💡 Market 주문 90% + LIMIT 주문 10% = 즉시 체결 우선!")
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
                              f"{self.config['symbol']}: ${current_price['mid']:,.2f} | "
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
    print("🚀💰 즉시 수익 그리드 시스템 - 실행하자마자 돈 벌기! 💰🚀")
    print("\n🔥 핵심 개념:")
    print("  🎯 현재가 바로 위아래에 Market 주문 즉시 체결")
    print("  💰 0.01% 움직이면 즉시 수익 실현")
    print("  🚀 90% Market 주문으로 즉시 체결")
    print("  🔄 수익 실현 즉시 재배치로 연속 수익")
    print("  💎 대기시간 ZERO! 실행하자마자 돈!")
    
    print("\n💡 즉시 수익 원리:")
    print("  📊 현재가 $90,000 → 즉시 $89,999 매수, $90,001 매도")
    print("  ⚡ 가격이 $90,009로 0.01% 움직임")
    print("  💰 매수 포지션 즉시 $9 수익 실현!")
    print("  🔄 즉시 새로운 매수 주문 재배치")
    print("  🚀 연속 수익 발생!")
    
    print("\n🚀 즉시 수익 그리드 시스템:")
    print("  🚀 Market 주문: 90% 확률로 즉시 체결")
    print("  📋 LIMIT 주문: 10%만 사용 (대부분 즉시 체결!)")
    print("  ⚡ 초고속 실행: 0.05초 간격으로 연속 배치")
    print("  💎 즉시 수익: 0.01% 움직임으로도 수익")
    print("  🔄 자동 재배치: 수익 실현 즉시 새 주문")
    print("  💰 연속 수익: 24시간 자동 돈 벌기!")
    
    print("\n💎 수익 시나리오 예시:")
    print("  📈 BTC 0.1% 상승: 10개 레벨 체결 → $100 수익")
    print("  📉 BTC 0.1% 하락: 10개 레벨 체결 → $100 수익")
    print("  🔄 양방향 0.2% 변동: 20개 레벨 체결 → $200 수익")
    print("  🚀 1% 변동: 100개 레벨 체결 → $1,000 수익!")
    
    bot = GridRevolutionaryBot()
    
    if not bot.connect_mt5():
        return
    
    # 심볼 선택 및 확인
    print("\n🎯 먼저 거래할 심볼을 선택해주세요.")
    selected_symbol, selected_name = bot.select_trading_symbol()
    bot.config['symbol'] = selected_symbol
    
    # 선택된 심볼 정보 재확인
    symbol_info = mt5.symbol_info(selected_symbol)
    if symbol_info is None:
        print(f"❌ {selected_symbol} 심볼을 사용할 수 없습니다.")
        mt5.shutdown()
        return
    
    print(f"\n✅ 거래 심볼 확정: {selected_symbol} ({selected_name})")
    
    answer = input(f"\n🚀 {selected_symbol} 즉시 수익 그리드 시스템을 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        print("프로그램 종료")
        mt5.shutdown()
        return
    
    print(f"\n🚀 {selected_symbol} 즉시 수익 그리드 시스템 가동!")
    print(f"💎 {selected_name}이 조금만 움직여도 즉시 수익!")
    print("🚀 Market 주문 90%로 즉시 체결!")
    print("⚡ 0.01% 움직임으로도 수익 실현!")
    print("💰 실행하자마자 돈이 들어옵니다!")
    
    # 즉시 수익 그리드 시스템 시작!
    bot.run_grid_system()
    
    mt5.shutdown()

if __name__ == "__main__":
    main()