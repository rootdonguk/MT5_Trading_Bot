"""
Tradeify (Lightning Funded) 전용 BTC 양방향 수익 자동매매 시스템
- 평가 없는 즉시 펀딩 계정용
- 규칙: 단일 거래일이 전체 수익의 35% 초과 불가
- 10분 내 초고속 출금 가능
"""

import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta
import sys
import json
import os
from collections import defaultdict

# ==================== Tradeify 규칙 설정 ====================
TRADEIFY_CONFIG = {
    # 거래 설정
    'symbol': 'BTCUSD',             # BTC 심볼
    'lot_size': 0.02,               # 거래량 (즉시 펀딩이므로 조금 더 크게)
    'profit_target': 100.0,         # 목표 수익 ($100)
    'magic_number': 654321,
    
    # Tradeify 규칙 (Lightning Funded)
    'max_daily_profit_ratio': 0.35, # 단일 거래일 최대 35%
    'consistency_rule': True,        # 일관성 규칙 적용
    'min_withdrawal': 100.0,         # 최소 출금 $100
    
    # 리스크 관리
    'max_spread': 100,
    'check_interval': 0.5,
    'deviation': 20,
    'daily_loss_limit': 200.0,      # 일일 손실 제한 (선택)
    
    # 출금 설정
    'auto_withdrawal_threshold': 500.0,  # 자동 출금 추천 임계값
}

class TradeifyTrader:
    def __init__(self, config):
        self.config = config
        self.initial_balance = 0
        self.total_profit = 0.0
        self.daily_profits = defaultdict(float)  # 날짜별 수익
        self.daily_trades = defaultdict(int)     # 날짜별 거래 횟수
        self.session_file = 'tradeify_session.json'
        
        # 세션 데이터 로드
        self.load_session()
        
    def load_session(self):
        """이전 세션 데이터 로드"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    self.daily_profits = defaultdict(float, data.get('daily_profits', {}))
                    self.total_profit = data.get('total_profit', 0.0)
                    print(f"✓ 세션 복원: 총 수익 ${self.total_profit:.2f}")
            except:
                pass
    
    def save_session(self):
        """세션 데이터 저장"""
        data = {
            'daily_profits': dict(self.daily_profits),
            'total_profit': self.total_profit,
            'last_update': datetime.now().isoformat()
        }
        with open(self.session_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def connect(self):
        """MT5 연결 (Tradeify 계정)"""
        print("Tradeify (Lightning Funded) MT5 연결 중...")
        
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패: {mt5.last_error()}")
            print("\n✓ Tradeify 계정으로 MT5에 로그인하셨나요?")
            return False
        
        print("✓ MT5 연결 성공!")
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보를 가져올 수 없습니다")
            mt5.shutdown()
            return False
        
        self.initial_balance = account_info.balance
        
        print("\n" + "="*70)
        print("  ⚡ TRADEIFY LIGHTNING FUNDED 계정 정보")
        print("="*70)
        print(f"계좌 번호: {account_info.login}")
        print(f"브로커: {account_info.server}")
        print(f"초기 잔고: ${self.initial_balance:,.2f}")
        print(f"현재 증거금: ${account_info.equity:,.2f}")
        print(f"레버리지: 1:{account_info.leverage}")
        print("="*70)
        
        # 규칙 안내
        print("\n📋 Tradeify Lightning Funded 규칙:")
        print(f"✓ 단일 거래일 최대 수익: 전체 수익의 {self.config['max_daily_profit_ratio']*100}%")
        print(f"✓ 일관성 중요: 매일 꾸준히 수익 실현")
        print(f"✓ 최소 출금: ${self.config['min_withdrawal']}")
        print(f"✓ 수익 배분: 80-90%")
        print(f"✓ 출금 속도: 10분 이내 가능!")
        print("="*70 + "\n")
        
        return True
    
    def check_daily_profit_limit(self, potential_profit):
        """오늘의 수익이 35% 규칙을 위반하는지 체크"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_profit = self.daily_profits[today]
        
        # 전체 수익 계산
        total_accumulated_profit = sum(self.daily_profits.values())
        
        if total_accumulated_profit <= 0:
            return True  # 아직 전체 수익이 없으면 OK
        
        # 오늘 수익에 잠재 수익을 더한 비율
        projected_today_profit = today_profit + potential_profit
        projected_ratio = projected_today_profit / (total_accumulated_profit + potential_profit)
        
        if projected_ratio > self.config['max_daily_profit_ratio']:
            print(f"\n⚠️ 35% 규칙 위반 가능성!")
            print(f"   오늘 수익: ${today_profit:.2f}")
            print(f"   잠재 수익: ${potential_profit:.2f}")
            print(f"   전체 대비: {projected_ratio*100:.1f}%")
            print(f"   → 오늘은 더 이상 수익 실현하지 않습니다\n")
            return False
        
        return True
    
    def record_daily_profit(self, profit):
        """오늘의 수익 기록"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_profits[today] += profit
        self.daily_trades[today] += 1
        self.save_session()
    
    def get_daily_statistics(self):
        """일일 통계 반환"""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            'today_profit': self.daily_profits[today],
            'today_trades': self.daily_trades[today],
            'total_days': len(self.daily_profits),
            'avg_daily_profit': sum(self.daily_profits.values()) / max(len(self.daily_profits), 1)
        }
    
    def get_symbol_info(self):
        """심볼 정보 조회"""
        symbol_info = mt5.symbol_info(self.config['symbol'])
        
        if symbol_info is None:
            print(f"❌ {self.config['symbol']} 심볼을 찾을 수 없습니다")
            
            all_symbols = mt5.symbols_get()
            btc_symbols = [s.name for s in all_symbols if 'BTC' in s.name.upper()]
            
            if btc_symbols:
                print(f"\n사용 가능한 BTC 심볼:")
                for i, sym in enumerate(btc_symbols[:10], 1):
                    print(f"  {i}. {sym}")
            
            return None
        
        if not symbol_info.visible:
            if not mt5.symbol_select(self.config['symbol'], True):
                print(f"❌ {self.config['symbol']} 심볼 활성화 실패")
                return None
        
        return symbol_info
    
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
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        
        price = self.get_current_price()
        if price is None:
            return False
        
        # 스프레드 체크
        spread_points = (price['spread'] / symbol_info.point)
        if spread_points > self.config['max_spread']:
            print(f"⚠️ 스프레드가 높음: {spread_points:.0f} 포인트")
            return False
        
        lot_size = self.config['lot_size']
        
        print(f"\n{'='*70}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ 양방향 진입 (Tradeify)")
        print(f"{'='*70}")
        print(f"BTC: ${price['ask']:,.2f} | 스프레드: {spread_points:.1f}p | 거래량: {lot_size} BTC")
        print(f"목표 수익: ${self.config['profit_target']}")
        
        stats = self.get_daily_statistics()
        print(f"오늘 수익: ${stats['today_profit']:.2f} | 오늘 거래: {stats['today_trades']}회")
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
            "comment": "TF_BUY",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        buy_result = mt5.order_send(buy_request)
        if not buy_result or buy_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ 매수 실패: {buy_result.retcode if buy_result else 'None'}")
            return False
        
        print(f"✓ 매수 체결: 티켓 {buy_result.order} @ ${buy_result.price:,.2f}")
        
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
            "comment": "TF_SELL",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        sell_result = mt5.order_send(sell_request)
        if not sell_result or sell_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ 매도 실패: {sell_result.retcode if sell_result else 'None'}")
            self.close_position(buy_result.order)
            return False
        
        print(f"✓ 매도 체결: 티켓 {sell_result.order} @ ${sell_result.price:,.2f}\n")
        
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
            "comment": "CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        return result and result.retcode == mt5.TRADE_RETCODE_DONE
    
    def monitor_positions(self):
        """포지션 모니터링"""
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
            
            # 목표 달성 체크
            if profit_usd >= self.config['profit_target']:
                # 35% 규칙 체크
                if not self.check_daily_profit_limit(profit_usd):
                    print("⏸️  오늘은 35% 규칙 때문에 청산을 보류합니다")
                    print("   내일 다시 청산 시도합니다\n")
                    continue
                
                if self.close_position(position.ticket):
                    self.total_profit += profit_usd
                    self.record_daily_profit(profit_usd)
                    
                    print(f"\n{'='*70}")
                    print(f"💰 수익 실현! (Tradeify)")
                    print(f"{'='*70}")
                    print(f"티켓: {position.ticket}")
                    print(f"타입: {'매수' if position.type == mt5.ORDER_TYPE_BUY else '매도'}")
                    print(f"진입: ${position.price_open:,.2f}")
                    print(f"청산: ${current_price['bid'] if position.type == mt5.ORDER_TYPE_BUY else current_price['ask']:,.2f}")
                    print(f"이번 수익: ${profit_usd:,.2f}")
                    
                    stats = self.get_daily_statistics()
                    print(f"\n📊 통계:")
                    print(f"   오늘 수익: ${stats['today_profit']:.2f} ({stats['today_trades']}회 거래)")
                    print(f"   총 수익: ${self.total_profit:.2f}")
                    print(f"   평균 일일 수익: ${stats['avg_daily_profit']:.2f}")
                    print(f"{'='*70}\n")
                    
                    # 출금 추천
                    if self.total_profit >= self.config['auto_withdrawal_threshold']:
                        print(f"🎉 출금 추천!")
                        print(f"   총 수익이 ${self.total_profit:.2f}에 도달했습니다")
                        print(f"   → Tradeify 대시보드에서 출금 신청하세요!")
                        print(f"   → 10분 이내 처리 가능합니다! ⚡\n")
                    
                    closed_tickets.append(position.ticket)
        
        return closed_tickets if closed_tickets else None
    
    def run(self):
        """메인 트레이딩 루프"""
        print("\n" + "="*70)
        print("  ⚡ TRADEIFY LIGHTNING FUNDED 자동매매 시작")
        print("="*70 + "\n")
        
        last_print_time = time.time()
        position_opened = False
        
        try:
            while True:
                # 포지션 모니터링
                closed = self.monitor_positions()
                
                if closed:
                    position_opened = False
                    time.sleep(2)
                
                # 신규 진입
                if not position_opened:
                    if self.open_straddle():
                        position_opened = True
                
                # 상태 출력 (5초마다)
                current_time = time.time()
                if current_time - last_print_time >= 5:
                    account_info = mt5.account_info()
                    price = self.get_current_price()
                    positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                    
                    if price and account_info:
                        profit = account_info.equity - self.initial_balance
                        stats = self.get_daily_statistics()
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${price['ask']:,.2f} | "
                              f"포지션: {len(positions) if positions else 0} | "
                              f"수익: ${profit:+,.2f} | "
                              f"오늘: ${stats['today_profit']:+,.2f} | "
                              f"총: ${self.total_profit:+,.2f}")
                    
                    last_print_time = current_time
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("  ⏹️  프로그램 중단")
            print("="*70)
            
            stats = self.get_daily_statistics()
            print(f"\n최종 통계:")
            print(f"  총 거래일: {stats['total_days']}일")
            print(f"  총 수익: ${self.total_profit:,.2f}")
            print(f"  평균 일일 수익: ${stats['avg_daily_profit']:.2f}")
            print(f"  오늘 수익: ${stats['today_profit']:.2f}")
            
            if self.total_profit >= self.config['min_withdrawal']:
                print(f"\n✓ 출금 가능! (최소 ${self.config['min_withdrawal']})")
                print(f"  → 10분 이내 처리 가능! ⚡")
        
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            mt5.shutdown()
            print("\nMT5 연결 종료\n")

def main():
    print("\n" + "="*70)
    print("  TRADEIFY (LIGHTNING FUNDED) 전용 BTC 양방향 자동매매 봇")
    print("="*70)
    print("\n⚡ 평가 없이 즉시 거래! 10분 내 출금 가능!")
    print("\n현재 설정:")
    print(f"  심볼: {TRADEIFY_CONFIG['symbol']}")
    print(f"  거래량: {TRADEIFY_CONFIG['lot_size']} BTC")
    print(f"  목표 수익: ${TRADEIFY_CONFIG['profit_target']}")
    print(f"  35% 규칙: 활성화 (일관성 중요)")
    print(f"  최소 출금: ${TRADEIFY_CONFIG['min_withdrawal']}")
    
    trader = TradeifyTrader(TRADEIFY_CONFIG)
    
    if not trader.connect():
        sys.exit(1)
    
    if trader.get_symbol_info() is None:
        mt5.shutdown()
        sys.exit(1)
    
    answer = input("\n거래를 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        print("프로그램을 종료합니다.")
        mt5.shutdown()
        sys.exit(0)
    
    trader.run()

if __name__ == "__main__":
    main()