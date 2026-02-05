"""
🌟 최종 완벽 단 하나의 선 혁명 봇 - 실시간 수익률 상시 표시 버전 🌟
- 이미 포지션 있으면 자동 인식 & 모니터링
- 1초마다 손익 $ / % + TP 예상 $ / % 실시간 출력
- 종료 시 자동 청산 여부 물어봄
- 키: H(수익청산종료), L(손실청산종료), Q(전체청산종료), A(전체청산계속), S(통계)
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import sys
import threading
import msvcrt

CONFIG = {
    'symbol': 'BTCUSD',
    'magic_number': 777777,
    'direction': 'buy',                # 초기 방향 (플립 시 자동 변경)
    'lot_size': 0.50,
    'sl_distance': 50.0,
    'tp_distance': 500000.0,
    'flip_on_sl': True,
    'max_spread': 150.0,
    'deviation': 20,
    'check_interval': 1.0,
}

class OneLineRevolution:
    def __init__(self, config):
        self.config = config
        self.position_ticket = None
        self.stats = {
            'total_profit': 0.0,
            'flips': 0,
            'start_time': datetime.now(),
        }
        self.running = True

    def connect_mt5(self):
        print("\n" + "="*80)
        print("  🌟 단 하나의 선 - 천문학적 수익 최종 버전")
        print("="*80)
        
        if not mt5.initialize():
            print(f"❌ 초기화 실패: {mt5.last_error()}")
            return False
        
        acc = mt5.account_info()
        if acc is None:
            print("❌ 계좌 정보 없음 → MT5에 계좌 로그인 먼저")
            mt5.shutdown()
            return False
        
        print(f"연결 성공 | 계좌: {acc.login} | 서버: {acc.server}")
        print(f"잔고: ${acc.balance:,.2f} | 자산: ${acc.equity:,.2f}")
        return True

    def find_existing_position(self):
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if positions and len(positions) > 0:
            pos = positions[0]
            self.position_ticket = pos.ticket
            print(f"\n기존 포지션 자동 인식! 티켓: {pos.ticket}")
            print(f"방향: {'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL'}")
            print(f"진입가: {pos.price_open:,.2f} | SL: {pos.sl:,.2f} | TP: {pos.tp:,.2f}")
            print(f"현재 손익: ${pos.profit:,.2f}")
            return True
        return False

    def open_one_line(self):
        if self.find_existing_position():
            return True  # 이미 있으면 진입 스킵
        
        price = self.get_current_price()
        if not price or (price['ask'] - price['bid']) > self.config['max_spread']:
            print("스프레드 초과 또는 가격 조회 실패")
            return False
        
        entry = price['ask'] if self.config['direction'] == 'buy' else price['bid']
        sl = entry - self.config['sl_distance'] if self.config['direction'] == 'buy' else entry + self.config['sl_distance']
        tp = entry + self.config['tp_distance'] if self.config['direction'] == 'buy' else entry - self.config['tp_distance']
        
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": self.config['lot_size'],
            "type": mt5.ORDER_TYPE_BUY if self.config['direction'] == 'buy' else mt5.ORDER_TYPE_SELL,
            "price": entry,
            "sl": sl,
            "tp": tp,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "ONE_LINE_REVOLUTION",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(req)
        if result and result.retcode in [mt5.TRADE_RETCODE_DONE, 10019, 10009, 10008]:
            self.position_ticket = result.order if hasattr(result, 'order') else result.deal
            print(f"\n혁명 진입 성공")
            print(f"방향: {self.config['direction'].upper()}")
            print(f"진입: {entry:,.2f} | SL: {sl:,.2f} | TP: {tp:,.2f}")
            print(f"목표: +${self.config['tp_distance'] * self.config['lot_size']:,.2f}")
            return True
        else:
            print(f"진입 실패: {result.retcode if result else 'Unknown'} - {mt5.last_error()}")
            return False

    def get_current_price(self):
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        return {'bid': tick.bid, 'ask': tick.ask}

    def monitor_and_display(self):
        while self.running:
            positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if positions and len(positions) > 0:
                pos = positions[0]
                current_price = self.get_current_price()
                if current_price:
                    if pos.type == mt5.ORDER_TYPE_BUY:
                        current_pnl = (current_price['bid'] - pos.price_open) * pos.volume
                        pnl_percent = ((current_price['bid'] - pos.price_open) / pos.price_open) * 100 if pos.price_open != 0 else 0
                        tp_pnl = (self.config['tp_distance'] * pos.volume)
                        tp_percent = (self.config['tp_distance'] / pos.price_open) * 100 if pos.price_open != 0 else 0
                    else:
                        current_pnl = (pos.price_open - current_price['ask']) * pos.volume
                        pnl_percent = ((pos.price_open - current_price['ask']) / pos.price_open) * 100 if pos.price_open != 0 else 0
                        tp_pnl = (-self.config['tp_distance'] * pos.volume)
                        tp_percent = (-self.config['tp_distance'] / pos.price_open) * 100 if pos.price_open != 0 else 0
                    
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"현재가: ${current_price['bid']:,.2f} | "
                          f"손익: ${current_pnl:+,.2f} ({pnl_percent:+.4f}%) | "
                          f"TP 예상: ${tp_pnl:+,.2f} ({tp_percent:+.2f}%)     ", end="")
            
            time.sleep(1.0)

    def check_and_flip_on_sl(self):
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions or len(positions) == 0:
            return
        
        pos = positions[0]
        current_price = self.get_current_price()
        if not current_price:
            return
        
        if pos.type == mt5.ORDER_TYPE_BUY:
            pnl = (current_price['bid'] - pos.price_open) * pos.volume
        else:
            pnl = (pos.price_open - current_price['ask']) * pos.volume
        
        if self.config['flip_on_sl'] and abs(pnl) >= (self.config['sl_distance'] * pos.volume * 0.9):
            print(f"\nSL 근처 도달 → 자동 플립!")
            self.flip_position(pos)

    def flip_position(self, position):
        current_price = self.get_current_price()
        if not current_price:
            return
        
        new_direction = 'sell' if self.config['direction'] == 'buy' else 'buy'
        self.config['direction'] = new_direction
        
        entry = current_price['bid'] if new_direction == 'sell' else current_price['ask']
        sl = entry + self.config['sl_distance'] if new_direction == 'sell' else entry - self.config['sl_distance']
        tp = entry - self.config['tp_distance'] if new_direction == 'sell' else entry + self.config['tp_distance']
        
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        close_req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": position.volume,
            "type": close_type,
            "position": position.ticket,
            "price": current_price['bid'] if close_type == mt5.ORDER_TYPE_SELL else current_price['ask'],
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "FLIP_CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(close_req)
        
        time.sleep(0.5)
        
        new_req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": self.config['lot_size'],
            "type": mt5.ORDER_TYPE_SELL if new_direction == 'sell' else mt5.ORDER_TYPE_BUY,
            "price": entry,
            "sl": sl,
            "tp": tp,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "FLIP_REVOLUTION",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(new_req)
        if result and result.retcode in [mt5.TRADE_RETCODE_DONE, 10019, 10009]:
            self.position_ticket = result.order if hasattr(result, 'order') else result.deal
            self.stats['flips'] += 1
            print(f"\n🔄 플립 성공 → {new_direction.upper()}")
            print(f"새 TP: {tp:,.2f}")
        else:
            print(f"플립 실패: {mt5.last_error()}")

    def close_all_positions(self):
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions:
            print("포지션 없음")
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        for pos in positions:
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = current_price['bid'] if close_type == mt5.ORDER_TYPE_SELL else current_price['ask']
            
            req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_CLOSE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            mt5.order_send(req)
            time.sleep(0.1)
        
        print("모든 포지션 청산 완료")

    def display_stats(self):
        runtime = datetime.now() - self.stats['start_time']
        print(f"\n운영 시간: {runtime.days}일 {runtime.seconds//3600}시간")
        print(f"플립 횟수: {self.stats['flips']}")
        print(f"누적 실현 수익: ${self.stats['total_profit']:+,.2f}")

    def keyboard_listener(self):
        print("\n키 명령:")
        print("H : 수익청산 → 종료")
        print("L : 손실청산 → 종료")
        print("Q : 전체청산 → 종료")
        print("A : 전체청산 (계속)")
        print("S : 통계")
        
        while self.running:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').upper()
                if key in ['H', 'L', 'Q']:
                    self.close_all_positions()
                    self.running = False
                elif key == 'A':
                    self.close_all_positions()
                    print("청산 완료 - 봇 계속")
                elif key == 'S':
                    self.display_stats()
            time.sleep(0.1)

    def run(self):
        listener = threading.Thread(target=self.keyboard_listener, daemon=True)
        listener.start()
        
        monitor = threading.Thread(target=self.monitor_and_display, daemon=True)
        monitor.start()
        
        if not self.open_one_line():
            print("진입 또는 인식 실패 - 종료")
            return
        
        try:
            while self.running:
                self.check_and_flip_on_sl()
                time.sleep(self.config['check_interval'])
        except KeyboardInterrupt:
            print("\nCtrl+C 종료")
            answer = input("종료 전 모든 포지션 청산하시겠습니까? (y/n): ")
            if answer.lower() == 'y':
                self.close_all_positions()
        finally:
            self.display_stats()
            mt5.shutdown()

    def monitor_and_display(self):
        while self.running:
            positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if positions and len(positions) > 0:
                pos = positions[0]
                current_price = self.get_current_price()
                if current_price:
                    if pos.type == mt5.ORDER_TYPE_BUY:
                        current_pnl = (current_price['bid'] - pos.price_open) * pos.volume
                        pnl_percent = ((current_price['bid'] - pos.price_open) / pos.price_open) * 100 if pos.price_open != 0 else 0
                        tp_pnl = (self.config['tp_distance'] * pos.volume)
                        tp_percent = (self.config['tp_distance'] / pos.price_open) * 100 if pos.price_open != 0 else 0
                    else:
                        current_pnl = (pos.price_open - current_price['ask']) * pos.volume
                        pnl_percent = ((pos.price_open - current_price['ask']) / pos.price_open) * 100 if pos.price_open != 0 else 0
                        tp_pnl = (-self.config['tp_distance'] * pos.volume)
                        tp_percent = (-self.config['tp_distance'] / pos.price_open) * 100 if pos.price_open != 0 else 0
                    
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"현재가: ${current_price['bid']:,.2f} | "
                          f"손익: ${current_pnl:+,.2f} ({pnl_percent:+.4f}%) | "
                          f"TP 예상: ${tp_pnl:+,.2f} ({tp_percent:+.2f}%)     ", end="")
            
            time.sleep(1.0)

def main():
    print("\n" + "="*80)
    print("  단 하나의 선 - 천문학적 수익 최종 (실시간 모니터링 완비)")
    print("="*80)
    
    bot = OneLineRevolution(CONFIG)
    
    if not bot.connect_mt5():
        sys.exit(1)
    
    answer = input("\n혁명 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        mt5.shutdown()
        sys.exit(0)
    
    bot.run()

if __name__ == "__main__":
    main()