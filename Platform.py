"""
🚀 혁명적 복리 시스템 BTC 자동매매 봇
- 멀티 플랫폼 지원 (FTMO, Instant Funding, Phidias 등)
- 자동 복리 재투자 시스템
- 수익 극대화 알고리즘
- 실시간 모니터링 및 통계
"""

import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta
import sys
import json
import os
from collections import defaultdict

# ==================== 플랫폼 설정 ====================
PLATFORMS = {
    '1': {
        'name': 'FTMO',
        'description': 'FTMO Demo/Live 계정',
        'profit_split': 0.80,  # 수익의 80%
        'min_withdrawal': 100,
        'withdrawal_days': 14
    },
    '2': {
        'name': 'Instant Funding',
        'description': '무료 $5,000 챌린지 (instantfunding.com)',
        'profit_split': 0.90,  # 수익의 90%
        'min_withdrawal': 25,
        'withdrawal_days': 2
    },
    '3': {
        'name': 'Phidias',
        'description': '$19 챌린지 (phidiaspropfirm.com)',
        'profit_split': 0.90,
        'min_withdrawal': 50,
        'withdrawal_days': 1
    },
    '4': {
        'name': 'Tradeify',
        'description': '즉시 펀딩 (tradeify.co)',
        'profit_split': 0.85,
        'min_withdrawal': 25,
        'withdrawal_days': 0  # 즉시 출금
    },
    '5': {
        'name': 'FundedNext',
        'description': 'Stellar Instant (fundednext.com)',
        'profit_split': 0.80,
        'min_withdrawal': 50,
        'withdrawal_days': 1
    },
    '6': {
        'name': 'Custom',
        'description': '커스텀 설정 (직접 입력)',
        'profit_split': 0.80,
        'min_withdrawal': 100,
        'withdrawal_days': 7
    }
}

# ==================== 복리 전략 ====================
COMPOUND_STRATEGIES = {
    '1': {
        'name': '안정형 (Conservative)',
        'description': '천천히, 안전하게 복리 증가',
        'initial_lot': 0.01,
        'compound_threshold': 500,      # $500 수익마다
        'lot_increase': 0.01,           # 0.01씩 증가
        'max_lot': 0.5,
        'profit_target_multiplier': 1.0
    },
    '2': {
        'name': '균형형 (Balanced)',
        'description': '안정성과 공격성의 균형',
        'initial_lot': 0.02,
        'compound_threshold': 300,      # $300 수익마다
        'lot_increase': 0.02,           # 0.02씩 증가
        'max_lot': 1.0,
        'profit_target_multiplier': 1.0
    },
    '3': {
        'name': '공격형 (Aggressive)',
        'description': '빠른 복리, 높은 수익',
        'initial_lot': 0.03,
        'compound_threshold': 200,      # $200 수익마다
        'lot_increase': 0.03,           # 0.03씩 증가
        'max_lot': 2.0,
        'profit_target_multiplier': 1.2
    },
    '4': {
        'name': '혁명형 (Revolutionary)',
        'description': '⚡ 폭발적 복리! 최대 수익 추구',
        'initial_lot': 0.05,
        'compound_threshold': 150,      # $150 수익마다
        'lot_increase': 0.05,           # 0.05씩 증가
        'max_lot': 5.0,
        'profit_target_multiplier': 1.5,
        'turbo_mode': True              # 터보 모드 활성화
    },
    '5': {
        'name': '커스텀',
        'description': '직접 설정',
        'initial_lot': 0.01,
        'compound_threshold': 500,
        'lot_increase': 0.01,
        'max_lot': 1.0,
        'profit_target_multiplier': 1.0
    }
}

class RevolutionaryCompoundBot:
    def __init__(self):
        self.platform = None
        self.strategy = None
        self.config = {}
        self.stats = {
            'total_profit': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'current_lot': 0.01,
            'compound_level': 0,
            'start_time': datetime.now(),
            'daily_profits': defaultdict(float),
            'hourly_profits': defaultdict(float)
        }
        self.save_file = 'trading_stats.json'
        self.load_stats()
        
    def select_platform(self):
        """플랫폼 선택"""
        print("\n" + "="*70)
        print("  🏦 트레이딩 플랫폼 선택")
        print("="*70)
        
        for key, platform in PLATFORMS.items():
            profit_pct = int(platform['profit_split'] * 100)
            print(f"\n{key}. {platform['name']}")
            print(f"   📝 {platform['description']}")
            print(f"   💰 수익 배분: {profit_pct}%")
            print(f"   💵 최소 출금: ${platform['min_withdrawal']}")
            print(f"   ⏰ 출금 기간: {platform['withdrawal_days']}일")
        
        while True:
            choice = input("\n플랫폼 선택 (1-6): ").strip()
            if choice in PLATFORMS:
                self.platform = PLATFORMS[choice]
                
                # 커스텀 설정
                if choice == '6':
                    print("\n커스텀 설정을 입력하세요:")
                    try:
                        self.platform['profit_split'] = float(input("수익 배분율 (0.0-1.0, 예: 0.8): "))
                        self.platform['min_withdrawal'] = float(input("최소 출금액 ($): "))
                    except:
                        print("⚠️ 잘못된 입력. 기본값 사용")
                
                print(f"\n✓ {self.platform['name']} 선택됨!")
                break
            else:
                print("❌ 잘못된 선택입니다. 다시 선택하세요.")
    
    def select_compound_strategy(self):
        """복리 전략 선택"""
        print("\n" + "="*70)
        print("  📈 복리 전략 선택")
        print("="*70)
        
        for key, strategy in COMPOUND_STRATEGIES.items():
            print(f"\n{key}. {strategy['name']}")
            print(f"   {strategy['description']}")
            print(f"   🎯 초기 거래량: {strategy['initial_lot']} BTC")
            print(f"   💎 복리 기준: ${strategy['compound_threshold']} 수익마다")
            print(f"   📊 거래량 증가: +{strategy['lot_increase']} BTC")
            print(f"   🚀 최대 거래량: {strategy['max_lot']} BTC")
            
            if 'turbo_mode' in strategy and strategy['turbo_mode']:
                print(f"   ⚡ 터보 모드: 활성화!")
        
        while True:
            choice = input("\n전략 선택 (1-5): ").strip()
            if choice in COMPOUND_STRATEGIES:
                self.strategy = COMPOUND_STRATEGIES[choice].copy()
                
                # 커스텀 설정
                if choice == '5':
                    print("\n커스텀 전략 설정:")
                    try:
                        self.strategy['initial_lot'] = float(input("초기 거래량 (BTC): "))
                        self.strategy['compound_threshold'] = float(input("복리 기준 ($): "))
                        self.strategy['lot_increase'] = float(input("거래량 증가폭 (BTC): "))
                        self.strategy['max_lot'] = float(input("최대 거래량 (BTC): "))
                    except:
                        print("⚠️ 잘못된 입력. 기본값 사용")
                
                self.stats['current_lot'] = self.strategy['initial_lot']
                print(f"\n✓ {self.strategy['name']} 전략 선택됨!")
                break
            else:
                print("❌ 잘못된 선택입니다. 다시 선택하세요.")
    
    def configure_settings(self):
        """거래 설정"""
        print("\n" + "="*70)
        print("  ⚙️ 거래 설정")
        print("="*70)
        
        # 기본 설정
        self.config = {
            'symbol': 'BTCUSD',
            'profit_target': 100.0,
            'magic_number': 888888,
            'max_spread': 100,
            'check_interval': 0.5,
            'deviation': 20,
        }
        
        print("\nBTC 심볼 이름 (기본: BTCUSD)")
        symbol = input("심볼 [Enter=기본값]: ").strip()
        if symbol:
            self.config['symbol'] = symbol
        
        print("\n목표 수익 금액 (기본: $100)")
        profit = input("금액 [Enter=기본값]: ").strip()
        if profit:
            try:
                self.config['profit_target'] = float(profit)
            except:
                print("⚠️ 잘못된 입력. 기본값 사용")
        
        # 전략별 목표 수익 조정
        if 'profit_target_multiplier' in self.strategy:
            self.config['profit_target'] *= self.strategy['profit_target_multiplier']
        
        print(f"\n최종 설정:")
        print(f"  심볼: {self.config['symbol']}")
        print(f"  목표 수익: ${self.config['profit_target']:.2f}")
        print(f"  초기 거래량: {self.stats['current_lot']} BTC")
    
    def connect_mt5(self):
        """MT5 연결"""
        print("\n" + "="*70)
        print("  🔌 MT5 연결 중...")
        print("="*70)
        
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패: {mt5.last_error()}")
            print("\n해결 방법:")
            print("1. MT5를 먼저 실행하세요")
            print("2. 플랫폼 계정으로 로그인하세요")
            print("3. 다시 스크립트를 실행하세요")
            return False
        
        print("✓ MT5 연결 성공!")
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보를 가져올 수 없습니다")
            mt5.shutdown()
            return False
        
        print("\n" + "="*70)
        print("  💼 계좌 정보")
        print("="*70)
        print(f"플랫폼: {self.platform['name']}")
        print(f"계좌 번호: {account_info.login}")
        print(f"브로커: {account_info.server}")
        print(f"계좌 잔고: ${account_info.balance:,.2f}")
        print(f"증거금: ${account_info.equity:,.2f}")
        print(f"레버리지: 1:{account_info.leverage}")
        print("="*70)
        
        return True
    
    def calculate_dynamic_lot(self):
        """복리를 고려한 동적 거래량 계산"""
        base_lot = self.strategy['initial_lot']
        threshold = self.strategy['compound_threshold']
        increase = self.strategy['lot_increase']
        max_lot = self.strategy['max_lot']
        
        # 누적 수익 기반 복리 레벨 계산
        if self.stats['total_profit'] > 0:
            compound_level = int(self.stats['total_profit'] / threshold)
            new_lot = base_lot + (compound_level * increase)
            
            # 터보 모드: 복리 가속
            if self.strategy.get('turbo_mode', False):
                # 수익이 $1000 이상이면 복리 2배 가속
                if self.stats['total_profit'] >= 1000:
                    new_lot = new_lot * 1.5
                # 수익이 $2000 이상이면 복리 3배 가속
                if self.stats['total_profit'] >= 2000:
                    new_lot = new_lot * 2.0
            
            new_lot = min(new_lot, max_lot)
            
            if compound_level > self.stats['compound_level']:
                print(f"\n🎉 복리 레벨 UP! {self.stats['compound_level']} → {compound_level}")
                print(f"💎 거래량 증가: {self.stats['current_lot']:.2f} → {new_lot:.2f} BTC")
                self.stats['compound_level'] = compound_level
            
            self.stats['current_lot'] = new_lot
        
        return self.stats['current_lot']
    
    def get_current_price(self):
        """현재가 조회"""
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'spread': tick.ask - tick.bid,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def open_straddle(self):
        """양방향 포지션 오픈"""
        symbol_info = mt5.symbol_info(self.config['symbol'])
        if symbol_info is None:
            return False
        
        if not symbol_info.visible:
            mt5.symbol_select(self.config['symbol'], True)
        
        price = self.get_current_price()
        if price is None:
            return False
        
        # 스프레드 체크
        spread_points = (price['spread'] / symbol_info.point)
        if spread_points > self.config['max_spread']:
            print(f"⚠️ 스프레드 너무 큼: {spread_points:.0f} 포인트")
            return False
        
        # 동적 거래량 계산
        lot_size = self.calculate_dynamic_lot()
        
        print(f"\n{'='*70}")
        print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] 양방향 진입")
        print(f"{'='*70}")
        print(f"💰 BTC 가격: ${price['ask']:,.2f}")
        print(f"📊 거래량: {lot_size} BTC (복리 레벨: {self.stats['compound_level']})")
        print(f"🎯 목표 수익: ${self.config['profit_target']:.2f}")
        print(f"📈 누적 수익: ${self.stats['total_profit']:,.2f}")
        print(f"{'='*70}\n")
        
        # 매수 주문
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price['ask'],
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": f"COMPOUND_BUY_L{self.stats['compound_level']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        buy_result = mt5.order_send(buy_request)
        if not buy_result or buy_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ 매수 주문 실패")
            return False
        
        print(f"✓ 매수 체결: {buy_result.order} @ ${buy_result.price:,.2f}")
        
        time.sleep(0.1)
        
        # 매도 주문
        sell_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price['bid'],
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": f"COMPOUND_SELL_L{self.stats['compound_level']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        sell_result = mt5.order_send(sell_request)
        if not sell_result or sell_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ 매도 주문 실패")
            # 매수 포지션 청산
            self.close_position(buy_result.order)
            return False
        
        print(f"✓ 매도 체결: {sell_result.order} @ ${sell_result.price:,.2f}\n")
        
        return True
    
    def close_position(self, ticket):
        """포지션 청산"""
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        
        position = positions[0]
        price = self.get_current_price()
        if price is None:
            return False
        
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        close_price = price['bid'] if close_type == mt5.ORDER_TYPE_SELL else price['ask']
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": position.volume,
            "type": close_type,
            "position": ticket,
            "price": close_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "COMPOUND_CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        return result and result.retcode == mt5.TRADE_RETCODE_DONE
    
    def monitor_positions(self):
        """포지션 모니터링 및 청산"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        if not positions:
            return None
        
        current_price = self.get_current_price()
        if current_price is None:
            return None
        
        closed_tickets = []
        
        for position in positions:
            # 수익 계산
            if position.type == mt5.ORDER_TYPE_BUY:
                price_diff = current_price['bid'] - position.price_open
                profit_usd = price_diff * position.volume
            else:
                price_diff = position.price_open - current_price['ask']
                profit_usd = price_diff * position.volume
            
            # 목표 수익 도달 체크
            if profit_usd >= self.config['profit_target']:
                if self.close_position(position.ticket):
                    # 통계 업데이트
                    self.stats['total_profit'] += profit_usd
                    self.stats['total_trades'] += 1
                    self.stats['winning_trades'] += 1
                    
                    # 일별/시간별 수익 기록
                    today = datetime.now().strftime('%Y-%m-%d')
                    hour = datetime.now().strftime('%Y-%m-%d %H:00')
                    self.stats['daily_profits'][today] += profit_usd
                    self.stats['hourly_profits'][hour] += profit_usd
                    
                    # 플랫폼 수익 배분 계산
                    my_share = profit_usd * self.platform['profit_split']
                    platform_share = profit_usd * (1 - self.platform['profit_split'])
                    
                    print(f"\n{'='*70}")
                    print(f"💰💰💰 포지션 청산! 💰💰💰")
                    print(f"{'='*70}")
                    print(f"🎫 티켓: {position.ticket}")
                    print(f"📊 타입: {'매수 (LONG)' if position.type == mt5.ORDER_TYPE_BUY else '매도 (SHORT)'}")
                    print(f"📈 진입가: ${position.price_open:,.2f}")
                    print(f"📉 청산가: ${current_price['bid'] if position.type == mt5.ORDER_TYPE_BUY else current_price['ask']:,.2f}")
                    print(f"💵 총 수익: ${profit_usd:,.2f}")
                    print(f"👤 내 몫 ({int(self.platform['profit_split']*100)}%): ${my_share:,.2f}")
                    print(f"🏦 플랫폼 몫: ${platform_share:,.2f}")
                    print(f"📊 거래량: {position.volume} BTC (레벨 {self.stats['compound_level']})")
                    print(f"🎯 누적 수익: ${self.stats['total_profit']:,.2f}")
                    print(f"📈 총 거래: {self.stats['total_trades']}회 (승률: {self.get_win_rate():.1f}%)")
                    print(f"{'='*70}\n")
                    
                    self.save_stats()
                    closed_tickets.append(position.ticket)
            
            elif profit_usd < -self.config['profit_target']:
                # 손실 포지션도 기록 (통계용)
                self.stats['total_trades'] += 1
                self.stats['losing_trades'] += 1
        
        return closed_tickets if closed_tickets else None
    
    def get_win_rate(self):
        """승률 계산"""
        if self.stats['total_trades'] == 0:
            return 0
        return (self.stats['winning_trades'] / self.stats['total_trades']) * 100
    
    def display_compound_progress(self):
        """복리 진행 상황 표시"""
        next_level_profit = (self.stats['compound_level'] + 1) * self.strategy['compound_threshold']
        progress = (self.stats['total_profit'] / next_level_profit) * 100 if next_level_profit > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"  📊 복리 진행 상황")
        print(f"{'='*70}")
        print(f"현재 레벨: {self.stats['compound_level']}")
        print(f"현재 거래량: {self.stats['current_lot']:.2f} BTC")
        print(f"누적 수익: ${self.stats['total_profit']:,.2f}")
        print(f"다음 레벨까지: ${next_level_profit - self.stats['total_profit']:,.2f} (진행률: {progress:.1f}%)")
        print(f"다음 레벨 거래량: {self.stats['current_lot'] + self.strategy['lot_increase']:.2f} BTC")
        print(f"{'='*70}\n")
    
    def display_statistics(self):
        """상세 통계 표시"""
        runtime = datetime.now() - self.stats['start_time']
        days = runtime.days
        hours = runtime.seconds // 3600
        
        print(f"\n{'='*70}")
        print(f"  📈 상세 통계")
        print(f"{'='*70}")
        print(f"운영 시간: {days}일 {hours}시간")
        print(f"총 거래: {self.stats['total_trades']}회")
        print(f"승리: {self.stats['winning_trades']}회 | 패배: {self.stats['losing_trades']}회")
        print(f"승률: {self.get_win_rate():.1f}%")
        print(f"누적 수익: ${self.stats['total_profit']:,.2f}")
        
        if self.stats['total_profit'] > 0 and days > 0:
            daily_avg = self.stats['total_profit'] / max(days, 1)
            monthly_projection = daily_avg * 30
            yearly_projection = daily_avg * 365
            
            print(f"\n💰 수익 전망:")
            print(f"  일평균: ${daily_avg:,.2f}")
            print(f"  월 예상: ${monthly_projection:,.2f}")
            print(f"  년 예상: ${yearly_projection:,.2f}")
        
        # 출금 가능 여부
        withdrawable = self.stats['total_profit'] * self.platform['profit_split']
        if withdrawable >= self.platform['min_withdrawal']:
            print(f"\n🎉 출금 가능!")
            print(f"  출금 가능 금액: ${withdrawable:,.2f}")
            print(f"  최소 출금: ${self.platform['min_withdrawal']}")
            print(f"  예상 출금일: {self.platform['withdrawal_days']}일")
        else:
            remaining = self.platform['min_withdrawal'] - withdrawable
            print(f"\n📊 출금까지 ${remaining:,.2f} 더 필요")
        
        print(f"{'='*70}\n")
    
    def save_stats(self):
        """통계 저장"""
        stats_to_save = self.stats.copy()
        stats_to_save['daily_profits'] = dict(stats_to_save['daily_profits'])
        stats_to_save['hourly_profits'] = dict(stats_to_save['hourly_profits'])
        stats_to_save['start_time'] = stats_to_save['start_time'].isoformat()
        
        with open(self.save_file, 'w') as f:
            json.dump(stats_to_save, f, indent=2)
    
    def load_stats(self):
        """통계 불러오기"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    loaded_stats = json.load(f)
                
                self.stats.update(loaded_stats)
                self.stats['start_time'] = datetime.fromisoformat(loaded_stats['start_time'])
                self.stats['daily_profits'] = defaultdict(float, loaded_stats['daily_profits'])
                self.stats['hourly_profits'] = defaultdict(float, loaded_stats['hourly_profits'])
                
                print(f"\n✓ 이전 통계 불러옴: 누적 수익 ${self.stats['total_profit']:,.2f}")
            except:
                print("\n⚠️ 통계 파일 손상. 새로 시작합니다.")
    
    def run(self):
        """메인 트레이딩 루프"""
        print("\n" + "="*70)
        print("  🚀 혁명적 복리 자동매매 시작!")
        print("="*70)
        
        last_print_time = time.time()
        last_stats_time = time.time()
        position_opened = False
        
        try:
            while True:
                # 포지션 모니터링
                closed = self.monitor_positions()
                
                # 청산 시 잠시 대기 후 재진입
                if closed:
                    position_opened = False
                    self.display_compound_progress()
                    time.sleep(2)
                
                # 신규 진입
                if not position_opened:
                    if self.open_straddle():
                        position_opened = True
                
                # 실시간 모니터링 (3초마다)
                current_time = time.time()
                if current_time - last_print_time >= 3:
                    account_info = mt5.account_info()
                    price = self.get_current_price()
                    positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                    
                    if price and account_info:
                        unrealized = account_info.equity - account_info.balance
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${price['ask']:,.2f} | "
                              f"포지션: {len(positions) if positions else 0} | "
                              f"거래량: {self.stats['current_lot']:.2f} | "
                              f"미실현: ${unrealized:+,.2f} | "
                              f"누적: ${self.stats['total_profit']:+,.2f} | "
                              f"레벨: {self.stats['compound_level']}")
                    
                    last_print_time = current_time
                
                # 상세 통계 (5분마다)
                if current_time - last_stats_time >= 300:
                    self.display_statistics()
                    last_stats_time = current_time
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("  ⏹️  프로그램 중단")
            print("="*70)
            
            self.display_statistics()
            
            # 포지션 정리
            positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if positions:
                print(f"\n⚠️ 열린 포지션: {len(positions)}개")
                answer = input("모든 포지션을 청산하시겠습니까? (y/n): ")
                if answer.lower() == 'y':
                    for pos in positions:
                        self.close_position(pos.ticket)
                    print("✓ 모든 포지션 청산 완료")
            
        finally:
            self.save_stats()
            mt5.shutdown()
            print("\nMT5 연결 종료\n")

def main():
    """메인 함수"""
    print("\n" + "="*70)
    print("  🚀💰 혁명적 복리 BTC 자동매매 봇 💰🚀")
    print("="*70)
    print("\n이 봇은:")
    print("  ✅ 여러 플랫폼 지원 (FTMO, Instant Funding, Phidias 등)")
    print("  ✅ 자동 복리 재투자")
    print("  ✅ 수익에 따라 거래량 자동 증가")
    print("  ✅ 실시간 통계 및 모니터링")
    print("  ✅ 폭발적 수익 가능")
    
    bot = RevolutionaryCompoundBot()
    
    # 1단계: 플랫폼 선택
    bot.select_platform()
    
    # 2단계: 복리 전략 선택
    bot.select_compound_strategy()
    
    # 3단계: 거래 설정
    bot.configure_settings()
    
    # 4단계: MT5 연결
    if not bot.connect_mt5():
        sys.exit(1)
    
    # 5단계: 심볼 확인
    symbol_info = mt5.symbol_info(bot.config['symbol'])
    if symbol_info is None:
        print(f"\n❌ {bot.config['symbol']} 심볼을 찾을 수 없습니다")
        
        # BTC 심볼 검색
        all_symbols = mt5.symbols_get()
        btc_symbols = [s.name for s in all_symbols if 'BTC' in s.name.upper()]
        
        if btc_symbols:
            print(f"\n사용 가능한 BTC 심볼:")
            for sym in btc_symbols[:10]:
                print(f"  • {sym}")
        
        mt5.shutdown()
        sys.exit(1)
    
    # 최종 확인
    print("\n" + "="*70)
    print("  🎯 최종 설정 확인")
    print("="*70)
    print(f"플랫폼: {bot.platform['name']}")
    print(f"복리 전략: {bot.strategy['name']}")
    print(f"심볼: {bot.config['symbol']}")
    print(f"초기 거래량: {bot.stats['current_lot']} BTC")
    print(f"목표 수익: ${bot.config['profit_target']:.2f}")
    print(f"복리 기준: ${bot.strategy['compound_threshold']} 마다")
    print(f"거래량 증가: +{bot.strategy['lot_increase']} BTC")
    print(f"최대 거래량: {bot.strategy['max_lot']} BTC")
    if bot.strategy.get('turbo_mode'):
        print(f"⚡ 터보 모드: 활성화!")
    print("="*70)
    
    answer = input("\n거래를 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        print("프로그램을 종료합니다.")
        mt5.shutdown()
        sys.exit(0)
    
    # 거래 시작!
    bot.run()

if __name__ == "__main__":
    main()