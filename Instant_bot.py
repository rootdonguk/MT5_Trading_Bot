"""
Instant Funding 전용 BTC 양방향 수익 자동매매 시스템
- 무료 $5,000 챌린지 계정용
- 규칙 자동 준수: 10% trailing drawdown, 최소 3거래일
- 48시간 내 출금 가능
"""

import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta
import sys
import json
import os

# ==================== Instant Funding 규칙 설정 ====================
INSTANT_FUNDING_CONFIG = {
    # 거래 설정
    'symbol': 'BTCUSD',             # BTC 심볼
    'lot_size': 0.01,               # 거래량 (안전하게 시작)
    'profit_target': 50.0,          # 목표 수익 ($50 - 작게 자주)
    'magic_number': 123456,
    
    # Instant Funding 규칙
    'max_drawdown_percent': 10,     # 최대 손실 10% (trailing)
    'min_trading_days': 3,          # 최소 거래일 3일
    'daily_profit_limit': None,     # 일일 수익 제한 없음
    
    # 리스크 관리
    'max_spread': 100,
    'check_interval': 0.5,
    'deviation': 20,
    
    # 출금 설정
    'min_withdrawal': 25.0,         # 최소 출금 $25
    'auto_withdrawal': True,        # 자동 출금 추천 활성화
}

class InstantFundingTrader:
    def __init__(self, config):
        self.config = config
        self.initial_balance = 0
        self.peak_balance = 0
        self.total_profit = 0.0
        self.trading_days = set()  # 거래한 날짜 저장
        self.daily_trades = {}      # 일별 거래 횟수
        self.session_file = 'instant_funding_session.json'
        
        # 세션 데이터 로드
        self.load_session()
        
    def load_session(self):
        """이전 세션 데이터 로드"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    self.trading_days = set(data.get('trading_days', []))
                    self.total_profit = data.get('total_profit', 0.0)
                    print(f"✓ 세션 복원: {len(self.trading_days)}일 거래 완료, 누적 수익: ${self.total_profit:.2f}")
            except:
                pass
    
    def save_session(self):
        """세션 데이터 저장"""
        data = {
            'trading_days': list(self.trading_days),
            'total_profit': self.total_profit,
            'last_update': datetime.now().isoformat()
        }
        with open(self.session_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def connect(self):
        """MT5 연결 (Instant Funding 계정)"""
        print("Instant Funding MT5 연결 중...")
        
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패: {mt5.last_error()}")
            print("\n✓ Instant Funding 계정으로 MT5에 로그인하셨나요?")
            return False
        
        print("✓ MT5 연결 성공!")
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보를 가져올 수 없습니다")
            mt5.shutdown()
            return False
        
        # 초기 잔고 및 최고점 설정
        self.initial_balance = account_info.balance
        self.peak_balance = account_info.equity
        
        print("\n" + "="*70)
        print("  🎯 INSTANT FUNDING 계정 정보")
        print("="*70)
        print(f"계좌 번호: {account_info.login}")
        print(f"브로커: {account_info.server}")
        print(f"초기 잔고: ${self.initial_balance:,.2f}")
        print(f"현재 증거금: ${account_info.equity:,.2f}")
        print(f"레버리지: 1:{account_info.leverage}")
        print("="*70)
        
        # 규칙 안내
        print("\n📋 Instant Funding 규칙:")
        print(f"✓ 최대 손실: {self.config['max_drawdown_percent']}% (Trailing)")
        print(f"✓ 최소 거래일: {self.config['min_trading_days']}일")
        print(f"✓ 현재 거래일: {len(self.trading_days)}일")
        print(f"✓ 최소 출금: ${self.config['min_withdrawal']}")
        print(f"✓ 수익 배분: 80-90%")
        print("="*70 + "\n")
        
        return True
    
    def check_drawdown(self):
        """Trailing Drawdown 체크"""
        account_info = mt5.account_info()
        if account_info is None:
            return True
        
        current_equity = account_info.equity
        
        # Peak 업데이트
        if current_equity > self.peak_balance:
            self.peak_balance = current_equity
        
        # Trailing Drawdown 계산
        max_allowed_drawdown = self.peak_balance * (self.config['max_drawdown_percent'] / 100)
        current_drawdown = self.peak_balance - current_equity
        drawdown_percent = (current_drawdown / self.peak_balance) * 100
        
        if current_drawdown >= max_allowed_drawdown:
            print(f"\n⚠️ 경고! Trailing Drawdown 한계 근접!")
            print(f"Peak: ${self.peak_balance:,.2f}")
            print(f"현재: ${current_equity:,.2f}")
            print(f"손실: ${current_drawdown:,.2f} ({drawdown_percent:.2f}%)")
            print(f"한계: ${max_allowed_drawdown:,.2f} ({self.config['max_drawdown_percent']}%)")
            return False
        
        return True
    
    def update_trading_day(self):
        """거래일 업데이트"""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.trading_days:
            self.trading_days.add(today)
            self.save_session()
            print(f"✓ 거래일 기록: {today} ({len(self.trading_days)}일차)")
    
    def can_withdraw(self):
        """출금 가능 여부 확인"""
        account_info = mt5.account_info()
        if account_info is None:
            return False
        
        profit = account_info.equity - self.initial_balance
        
        # 조건 체크
        has_min_days = len(self.trading_days) >= self.config['min_trading_days']
        has_min_profit = profit >= self.config['min_withdrawal']
        
        if has_min_days and has_min_profit:
            return True, profit
        
        return False, profit
    
    def get_symbol_info(self):
        """심볼 정보 조회"""
        symbol_info = mt5.symbol_info(self.config['symbol'])
        
        if symbol_info is None:
            print(f"❌ {self.config['symbol']} 심볼을 찾을 수 없습니다")
            
            # 대체 심볼 검색
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
        # Drawdown 체크
        if not self.check_drawdown():
            print("❌ Drawdown 한계로 인해 신규 진입을 중단합니다")
            return False
        
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 양방향 진입")
        print(f"{'='*70}")
        print(f"BTC: ${price['ask']:,.2f} | 스프레드: {spread_points:.1f}p | 거래량: {lot_size} BTC")
        print(f"목표 수익: ${self.config['profit_target']}")
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
            "comment": "IF_BUY",
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
            "comment": "IF_SELL",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        sell_result = mt5.order_send(sell_request)
        if not sell_result or sell_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ 매도 실패: {sell_result.retcode if sell_result else 'None'}")
            # 매수 포지션 청산
            self.close_position(buy_result.order)
            return False
        
        print(f"✓ 매도 체결: 티켓 {sell_result.order} @ ${sell_result.price:,.2f}\n")
        
        # 거래일 업데이트
        self.update_trading_day()
        
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
            
            # 목표 달성 시 청산
            if profit_usd >= self.config['profit_target']:
                if self.close_position(position.ticket):
                    self.total_profit += profit_usd
                    self.save_session()
                    
                    print(f"\n{'='*70}")
                    print(f"💰 수익 실현!")
                    print(f"{'='*70}")
                    print(f"티켓: {position.ticket}")
                    print(f"타입: {'매수' if position.type == mt5.ORDER_TYPE_BUY else '매도'}")
                    print(f"진입: ${position.price_open:,.2f}")
                    print(f"청산: ${current_price['bid'] if position.type == mt5.ORDER_TYPE_BUY else current_price['ask']:,.2f}")
                    print(f"이번 수익: ${profit_usd:,.2f}")
                    print(f"총 수익: ${self.total_profit:,.2f}")
                    print(f"{'='*70}\n")
                    
                    # 출금 가능 체크
                    can_wd, total_profit = self.can_withdraw()
                    if can_wd:
                        print(f"🎉 출금 가능! 총 ${total_profit:.2f}")
                        print(f"   거래일: {len(self.trading_days)}일 (최소 {self.config['min_trading_days']}일 충족)")
                        if self.config['auto_withdrawal']:
                            print(f"   → Instant Funding 대시보드에서 출금 신청하세요!")
                            print(f"   → 48시간 내 처리됩니다.\n")
                    
                    closed_tickets.append(position.ticket)
        
        return closed_tickets if closed_tickets else None
    
    def run(self):
        """메인 트레이딩 루프"""
        print("\n" + "="*70)
        print("  🚀 INSTANT FUNDING 자동매매 시작")
        print("="*70 + "\n")
        
        last_print_time = time.time()
        position_opened = False
        
        try:
            while True:
                # Drawdown 체크
                if not self.check_drawdown():
                    print("\n⛔ 최대 손실 한도 도달. 프로그램을 종료합니다.")
                    break
                
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
                        drawdown_from_peak = ((self.peak_balance - account_info.equity) / self.peak_balance) * 100
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${price['ask']:,.2f} | "
                              f"포지션: {len(positions) if positions else 0} | "
                              f"수익: ${profit:+,.2f} | "
                              f"DD: {drawdown_from_peak:.2f}% | "
                              f"거래일: {len(self.trading_days)}")
                    
                    last_print_time = current_time
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("  ⏹️  프로그램 중단")
            print("="*70)
            
            # 최종 통계
            account_info = mt5.account_info()
            if account_info:
                final_profit = account_info.equity - self.initial_balance
                print(f"\n최종 통계:")
                print(f"  초기 잔고: ${self.initial_balance:,.2f}")
                print(f"  현재 잔고: ${account_info.equity:,.2f}")
                print(f"  총 수익: ${final_profit:+,.2f}")
                print(f"  거래일: {len(self.trading_days)}일")
                
                can_wd, _ = self.can_withdraw()
                if can_wd:
                    print(f"\n✓ 출금 가능!")
                else:
                    remaining_days = self.config['min_trading_days'] - len(self.trading_days)
                    if remaining_days > 0:
                        print(f"\n⚠️ 출금까지 {remaining_days}일 더 거래 필요")
            
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            mt5.shutdown()
            print("\nMT5 연결 종료\n")

def main():
    print("\n" + "="*70)
    print("  INSTANT FUNDING 전용 BTC 양방향 자동매매 봇")
    print("="*70)
    print("\n무료 $5,000 챌린지 계정으로 실력 증명하세요!")
    print("\n현재 설정:")
    print(f"  심볼: {INSTANT_FUNDING_CONFIG['symbol']}")
    print(f"  거래량: {INSTANT_FUNDING_CONFIG['lot_size']} BTC")
    print(f"  목표 수익: ${INSTANT_FUNDING_CONFIG['profit_target']}")
    print(f"  최대 손실: {INSTANT_FUNDING_CONFIG['max_drawdown_percent']}% (Trailing)")
    print(f"  최소 거래일: {INSTANT_FUNDING_CONFIG['min_trading_days']}일")
    
    trader = InstantFundingTrader(INSTANT_FUNDING_CONFIG)
    
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