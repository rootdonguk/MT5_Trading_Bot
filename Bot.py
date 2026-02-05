"""
MT5 BTC 양방향 수익 자동매매 시스템 (FTMO DEMO 버전)
이미 로그인된 MT5에 자동 연결 - 계정 정보 입력 불필요
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import sys

# ==================== 설정 ====================
CONFIG = {
    # 거래 설정
    'symbol': 'BTCUSD',             # 거래 심볼
    'lot_size': 0.01,               # 거래량 (0.01 BTC)
    'profit_target': 100.0,         # 목표 수익 ($100)
    'magic_number': 888888,         # 식별용 매직넘버
    
    # 리스크 관리
    'max_spread': 100,              # 최대 스프레드 (포인트)
    'check_interval': 0.5,          # 가격 체크 주기 (초)
    'deviation': 20,                # 슬리피지 허용범위
}

class FTMOVolatilityTrader:
    def __init__(self, config):
        self.config = config
        self.entry_price = None
        self.buy_ticket = None
        self.sell_ticket = None
        self.total_profit = 0.0
        
    def connect(self):
        """이미 로그인된 MT5에 연결"""
        print("MT5 연결 시도 중...")
        
        # MT5가 이미 실행 중인 경우 연결만 수행
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패")
            print(f"오류: {mt5.last_error()}")
            print("\n해결 방법:")
            print("1. MT5를 실행하세요")
            print("2. FTMO 데모 계정으로 로그인하세요")
            print("3. 다시 스크립트를 실행하세요")
            return False
        
        print("✓ MT5 연결 성공!")
        
        # 현재 로그인된 계좌 정보
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보를 가져올 수 없습니다")
            print("MT5에 로그인되어 있는지 확인하세요")
            mt5.shutdown()
            return False
        
        print("\n" + "="*60)
        print("  연결된 계좌 정보")
        print("="*60)
        print(f"계좌 번호: {account_info.login}")
        print(f"브로커: {account_info.server}")
        print(f"계좌 잔고: ${account_info.balance:,.2f}")
        print(f"증거금: ${account_info.equity:,.2f}")
        print(f"여유 증거금: ${account_info.margin_free:,.2f}")
        print(f"레버리지: 1:{account_info.leverage}")
        print("="*60 + "\n")
        
        return True
    
    def get_symbol_info(self):
        """심볼 정보 조회 및 활성화"""
        symbol_info = mt5.symbol_info(self.config['symbol'])
        
        if symbol_info is None:
            print(f"❌ {self.config['symbol']} 심볼을 찾을 수 없습니다")
            print("\nFTMO에서 사용 가능한 BTC 심볼 검색 중...")
            
            # BTC 관련 심볼 검색
            all_symbols = mt5.symbols_get()
            btc_symbols = [s.name for s in all_symbols if 'BTC' in s.name.upper()]
            
            if btc_symbols:
                print(f"\n사용 가능한 BTC 심볼:")
                for i, sym in enumerate(btc_symbols[:10], 1):
                    print(f"  {i}. {sym}")
                print(f"\nCONFIG['symbol']을 위 심볼 중 하나로 변경하세요")
            
            return None
        
        # 심볼이 비활성화된 경우 활성화
        if not symbol_info.visible:
            print(f"{self.config['symbol']} 심볼 활성화 중...")
            if not mt5.symbol_select(self.config['symbol'], True):
                print(f"❌ {self.config['symbol']} 심볼 활성화 실패")
                return None
            print(f"✓ {self.config['symbol']} 심볼 활성화 완료")
        
        print(f"✓ 심볼 정보:")
        print(f"  이름: {symbol_info.name}")
        print(f"  설명: {symbol_info.description}")
        print(f"  최소 거래량: {symbol_info.volume_min}")
        print(f"  최대 거래량: {symbol_info.volume_max}")
        print(f"  틱 사이즈: {symbol_info.trade_tick_size}")
        print(f"  포인트: {symbol_info.point}\n")
        
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
    
    def calculate_lot_size(self):
        """계좌 잔고에 따른 적절한 거래량 계산"""
        account_info = mt5.account_info()
        balance = account_info.balance
        
        # 잔고에 따른 권장 거래량
        if balance < 5000:
            recommended = 0.01
        elif balance < 10000:
            recommended = 0.02
        elif balance < 50000:
            recommended = 0.05
        else:
            recommended = 0.1
        
        return min(recommended, self.config['lot_size'])
    
    def open_straddle(self):
        """양방향 포지션 오픈 (매수 + 매도)"""
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        
        price = self.get_current_price()
        if price is None:
            print("❌ 가격 정보를 가져올 수 없습니다")
            return False
        
        # 스프레드 체크
        spread_points = (price['spread'] / symbol_info.point)
        if spread_points > self.config['max_spread']:
            print(f"⚠️ 스프레드가 너무 큽니다: {spread_points:.0f} 포인트")
            print(f"   현재 설정: 최대 {self.config['max_spread']} 포인트")
            return False
        
        # 거래량 계산
        lot_size = self.calculate_lot_size()
        
        self.entry_price = price
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 양방향 진입")
        print(f"{'='*60}")
        print(f"BTC 가격: ${price['ask']:,.2f}")
        print(f"스프레드: {spread_points:.1f} 포인트 (${price['spread']:.2f})")
        print(f"거래량: {lot_size} BTC")
        print(f"목표 수익: ${self.config['profit_target']:.2f}")
        print(f"{'='*60}\n")
        
        # 매수 주문 (BUY)
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price['ask'],
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "STRADDLE_BUY",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        buy_result = mt5.order_send(buy_request)
        
        if buy_result is None:
            print(f"❌ 매수 주문 전송 실패")
            return False
        
        if buy_result.retcode == mt5.TRADE_RETCODE_DONE:
            self.buy_ticket = buy_result.order
            print(f"✓ 매수 주문 체결")
            print(f"  티켓: {buy_result.order}")
            print(f"  가격: ${buy_result.price:,.2f}")
            print(f"  수량: {lot_size} BTC\n")
        else:
            print(f"❌ 매수 주문 실패")
            print(f"  오류 코드: {buy_result.retcode}")
            print(f"  설명: {self.get_retcode_description(buy_result.retcode)}")
            return False
        
        # 잠시 대기
        time.sleep(0.1)
        
        # 매도 주문 (SELL)
        sell_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price['bid'],
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "STRADDLE_SELL",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        sell_result = mt5.order_send(sell_request)
        
        if sell_result is None:
            print(f"❌ 매도 주문 전송 실패")
            # 매수 포지션 청산
            self.close_position(self.buy_ticket)
            return False
        
        if sell_result.retcode == mt5.TRADE_RETCODE_DONE:
            self.sell_ticket = sell_result.order
            print(f"✓ 매도 주문 체결")
            print(f"  티켓: {sell_result.order}")
            print(f"  가격: ${sell_result.price:,.2f}")
            print(f"  수량: {lot_size} BTC\n")
        else:
            print(f"❌ 매도 주문 실패")
            print(f"  오류 코드: {sell_result.retcode}")
            print(f"  설명: {self.get_retcode_description(sell_result.retcode)}")
            # 매수 포지션 청산
            self.close_position(self.buy_ticket)
            return False
        
        return True
    
    def get_retcode_description(self, retcode):
        """MT5 리턴 코드 설명"""
        retcode_dict = {
            10004: "재견적 (Requote)",
            10006: "요청 거부 (Request rejected)",
            10007: "요청 취소 (Request canceled)",
            10008: "주문 배치 완료 (Order placed)",
            10009: "요청 완료 (Done)",
            10010: "부분 체결만 완료 (Done partially)",
            10011: "오류 발생 (Error)",
            10012: "타임아웃 (Timeout)",
            10013: "잘못된 가격 (Invalid price)",
            10014: "잘못된 스탑 (Invalid stops)",
            10015: "잘못된 거래량 (Invalid volume)",
            10016: "시장 마감 (Market closed)",
            10017: "증거금 부족 (No money)",
            10018: "가격 변경 (Price changed)",
            10019: "오프 쿼트 (Off quotes)",
            10020: "주문 만료 (Expiration denied)",
        }
        return retcode_dict.get(retcode, f"알 수 없는 오류 ({retcode})")
    
    def close_position(self, ticket):
        """포지션 청산"""
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        
        position = positions[0]
        price = self.get_current_price()
        
        if price is None:
            return False
        
        # 반대 방향으로 청산
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
            "comment": "CLOSE_PROFIT",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            return True
        else:
            print(f"⚠️ 청산 실패: 티켓 {ticket}")
            if result:
                print(f"   오류: {self.get_retcode_description(result.retcode)}")
            return False
    
    def monitor_positions(self):
        """포지션 모니터링 및 수익 체크"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        if not positions:
            return None
        
        current_price = self.get_current_price()
        if current_price is None:
            return None
        
        closed_tickets = []
        
        for position in positions:
            # 수익 계산 (달러 기준)
            if position.type == mt5.ORDER_TYPE_BUY:
                price_diff = current_price['bid'] - position.price_open
                profit_usd = price_diff * position.volume
            else:  # SELL
                price_diff = position.price_open - current_price['ask']
                profit_usd = price_diff * position.volume
            
            # 목표 수익 도달 체크
            if profit_usd >= self.config['profit_target']:
                if self.close_position(position.ticket):
                    self.total_profit += profit_usd
                    
                    print(f"\n{'='*60}")
                    print(f"💰 포지션 청산 완료!")
                    print(f"{'='*60}")
                    print(f"티켓: {position.ticket}")
                    print(f"타입: {'매수 (LONG)' if position.type == mt5.ORDER_TYPE_BUY else '매도 (SHORT)'}")
                    print(f"진입가: ${position.price_open:,.2f}")
                    print(f"청산가: ${current_price['bid'] if position.type == mt5.ORDER_TYPE_BUY else current_price['ask']:,.2f}")
                    print(f"가격 변동: ${abs(price_diff):,.2f}")
                    print(f"이번 수익: ${profit_usd:,.2f}")
                    print(f"누적 수익: ${self.total_profit:,.2f}")
                    print(f"{'='*60}\n")
                    
                    closed_tickets.append(position.ticket)
        
        return closed_tickets if closed_tickets else None
    
    def run(self):
        """메인 트레이딩 루프"""
        print("\n" + "="*60)
        print("  🤖 MT5 BTC 양방향 수익 자동매매 시작")
        print("="*60 + "\n")
        
        last_print_time = time.time()
        position_opened = False
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # 포지션 모니터링
                closed = self.monitor_positions()
                
                # 포지션이 청산되면 재진입 준비
                if closed:
                    position_opened = False
                    print("3초 후 재진입합니다...\n")
                    time.sleep(3)
                
                # 포지션이 없으면 신규 진입
                if not position_opened:
                    if self.open_straddle():
                        position_opened = True
                
                # 상태 출력 (3초마다)
                current_time = time.time()
                if current_time - last_print_time >= 3:
                    account_info = mt5.account_info()
                    price = self.get_current_price()
                    positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                    
                    if price and account_info:
                        unrealized_profit = account_info.equity - account_info.balance
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${price['ask']:,.2f} | "
                              f"포지션: {len(positions) if positions else 0} | "
                              f"잔고: ${account_info.balance:,.2f} | "
                              f"미실현: ${unrealized_profit:+,.2f} | "
                              f"누적: ${self.total_profit:+,.2f}")
                    
                    last_print_time = current_time
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("  ⏹️  사용자에 의해 프로그램이 중단되었습니다")
            print("="*60)
            
            # 현재 포지션 확인
            positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if positions:
                print(f"\n⚠️ 열린 포지션이 {len(positions)}개 있습니다")
                answer = input("모든 포지션을 청산하시겠습니까? (y/n): ")
                if answer.lower() == 'y':
                    for pos in positions:
                        self.close_position(pos.ticket)
                    print("✓ 모든 포지션 청산 완료")
            
            print(f"\n최종 누적 수익: ${self.total_profit:+,.2f}")
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            mt5.shutdown()
            print("\nMT5 연결 종료\n")

def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("  MT5 BTC 양방향 수익 자동매매 봇 (FTMO 버전)")
    print("="*60)
    print("\n⚠️  시작하기 전에 확인하세요:")
    print("  1. MT5가 실행 중입니까? ✓")
    print("  2. FTMO 데모 계정으로 로그인되어 있습니까? ✓")
    print("\n현재 설정:")
    print(f"  심볼: {CONFIG['symbol']}")
    print(f"  거래량: {CONFIG['lot_size']} BTC (계좌 잔고에 따라 자동 조정)")
    print(f"  목표 수익: ${CONFIG['profit_target']}")
    print(f"  체크 주기: {CONFIG['check_interval']}초")
    print(f"  최대 스프레드: {CONFIG['max_spread']} 포인트")
    
    # 트레이더 초기화
    trader = FTMOVolatilityTrader(CONFIG)
    
    # MT5 연결 (이미 로그인된 상태)
    if not trader.connect():
        sys.exit(1)
    
    # 심볼 정보 확인
    if trader.get_symbol_info() is None:
        mt5.shutdown()
        sys.exit(1)
    
    # 사용자 확인
    print("\n" + "="*60)
    answer = input("거래를 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        print("프로그램을 종료합니다.")
        mt5.shutdown()
        sys.exit(0)
    
    # 트레이딩 시작
    trader.run()

if __name__ == "__main__":
    main()