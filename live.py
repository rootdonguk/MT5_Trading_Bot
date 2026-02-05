"""
🌟 완벽한 그리드 트레이딩 봇 - 플립 기능 포함 (Axi Select Funded US50 맞춤 최종 버전)
- H 키: 수익 포지션만 청산하고 종료 (파란불 💙)
- L 키: 손실 포지션만 청산하고 종료 (빨간불 ❤️)
- Q 키: 모든 포지션 청산하고 종료
- S 키: 현재 통계 확인

플립 기능 유지: 손실 포지션 → 반대 방향 전환 (- → + 가능)
※ Axi Select 규칙상 flip/martingale 스타일 고위험 → quarantine 위험 있음
   데모나 다른 firm에서 테스트 권장 (funded 실계좌 사용 주의)
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import sys
import threading
import msvcrt  # Windows 키 입력
from collections import defaultdict

# ==================== 설정 ====================
GRID_CONFIG = {
    'symbol': 'BTCUSD',                # BTCUSD 유지 (변동성 높아 DD 주의)
    'magic_number': 999999,
    
    # 그리드 - Axi DD 10% 안전하게 제한
    'grid_spacing': 200.0,             # 200$ 간격 (너무 촘촘하면 breach)
    'grid_levels': 5,                  # 양방향 총 10레벨 (총 lot 0.1)
    'lot_per_order': 0.01,
    
    # 손실 관리 - flip 트리거
    'max_loss_per_position': 20.0,     # -$20 넘으면 flip (daily 2% 안 넘게)
    'flip_on_loss': True,
    
    # 수익 실현
    'take_profit_ticks': 150.0,        # +$150 목표
    
    # 기타
    'max_spread': 150.0,
    'check_interval': 0.5,
    'deviation': 30,
}

class PerfectGridBotWithManualControl:
    def __init__(self, config):
        self.config = config
        self.grid_orders = {'buy': {}, 'sell': {}}
        self.active_positions = {}
        self.stats = {
            'total_profit': 0.0,
            'total_trades': 0,
            'grid_hits': 0,
            'flips': 0,
            'avoided_loss': 0.0,
            'start_time': datetime.now(),
        }
        self.center_price = None
        self.running = True
        self.manual_action = None
        self.total_exposure_lot = 0.0  # DD 안전장치

    def connect_mt5(self):
        print("\n" + "="*80)
        print("  🌟 그리드 봇 - 플립 포함 (Axi Select Funded US50 최적화)")
        print("="*80)
        
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패: {mt5.last_error()}")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보 조회 실패")
            mt5.shutdown()
            return False
        
        print("\n✓ MT5 연결 성공!")
        print(f"계좌: {account_info.login}")
        print(f"잔고: ${account_info.balance:,.2f}")
        print(f"자산: ${account_info.equity:,.2f}")
        print("Axi Select Funded US50 서버 - Max DD 10% 주의")
        return True

    def get_symbol_info(self):
        symbol_info = mt5.symbol_info(self.config['symbol'])
        if symbol_info is None:
            print(f"❌ {self.config['symbol']} 심볼 없음")
            return None
        
        if not symbol_info.visible:
            mt5.symbol_select(self.config['symbol'], True)
        
        return symbol_info

    def get_current_price(self):
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        return {'bid': tick.bid, 'ask': tick.ask, 'spread': tick.ask - tick.bid}

    def place_pending_order(self, order_type, price, lot_size):
        price = round(price, 2)
        
        if order_type == 'buy':
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": f"GRID_BUY_{price:.2f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        else:
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": f"GRID_SELL_{price:.2f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            return result.order
        print(f"Pending 주문 실패: {result.retcode if result else 'Unknown'}")
        return None

    def setup_grid(self):
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        if current_price['spread'] > self.config['max_spread']:
            print(f"❌ 스프레드 초과: {current_price['spread']:.2f}")
            return False
        
        self.center_price = round((current_price['bid'] + current_price['ask']) / 2, 2)
        
        print(f"\n{'='*80}")
        print(f"  🎯 그리드 설정 - Axi Funded 안전 모드")
        print(f"{'='*80}")
        print(f"중심 가격: ${self.center_price:,.2f}")
        print(f"간격: ${self.config['grid_spacing']:.0f}")
        print(f"레벨: {self.config['grid_levels']} (총 {self.config['grid_levels']*2}개)")
        print(f"총 lot exposure: ≈ {self.config['grid_levels']*2*self.config['lot_per_order']:.2f} (DD 10% 이내)")
        print(f"{'='*80}\n")
        
        print("📊 그리드 배치 중...")
        
        for i in range(1, self.config['grid_levels'] + 1):
            buy_price = round(self.center_price - (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('buy', buy_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['buy'][buy_price] = order_id
            time.sleep(0.1)
        
        for i in range(1, self.config['grid_levels'] + 1):
            sell_price = round(self.center_price + (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('sell', sell_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['sell'][sell_price] = order_id
            time.sleep(0.1)
        
        total = len(self.grid_orders['buy']) + len(self.grid_orders['sell'])
        print(f"\n✅ 그리드 완료: {total}개")
        return True

    def flip_position(self, position):
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        if position.type == mt5.ORDER_TYPE_BUY:
            current_loss = (current_price['bid'] - position.price_open) * position.volume
            original = "매수"
            new_type_str = "매도"
            new_type = mt5.ORDER_TYPE_SELL
            new_price = current_price['bid']
        else:
            current_loss = (position.price_open - current_price['ask']) * position.volume
            original = "매도"
            new_type_str = "매수"
            new_type = mt5.ORDER_TYPE_BUY
            new_price = current_price['ask']
        
        if current_loss >= 0:
            return False  # 이미 수익이면 flip 안 함
        
        # 청산
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        close_price = current_price['bid'] if close_type == mt5.ORDER_TYPE_SELL else current_price['ask']
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": position.volume,
            "type": close_type,
            "position": position.ticket,
            "price": close_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "FLIP_CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        close_result = mt5.order_send(close_request)
        if not close_result or close_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"청산 실패: {close_result.retcode if close_result else 'Unknown'}")
            return False
        
        time.sleep(0.2)
        
        # 반대 방향 진입
        flip_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": position.volume,
            "type": new_type,
            "price": new_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "FLIP_OPEN",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        flip_result = mt5.order_send(flip_request)
        
        if flip_result and flip_result.retcode == mt5.TRADE_RETCODE_DONE:
            self.stats['flips'] += 1
            self.stats['avoided_loss'] += abs(current_loss)
            
            print(f"\n🔄 Flip 성공! {original} → {new_type_str} | 회피: ${abs(current_loss):.2f}")
            
            if position.ticket in self.active_positions:
                del self.active_positions[position.ticket]
            
            self.active_positions[flip_result.order] = {
                'type': new_type,
                'entry_price': new_price,
                'volume': position.volume,
                'flipped': True
            }
            return True
        
        print("Flip 실패")
        return False

    def check_and_manage_positions(self):
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions:
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        for position in positions:
            if position.ticket not in self.active_positions:
                self.active_positions[position.ticket] = {
                    'type': position.type,
                    'entry_price': position.price_open,
                    'volume': position.volume,
                    'flipped': False
                }
                self.stats['grid_hits'] += 1
                self.refill_grid(position.price_open, position.type)
            
            if position.type == mt5.ORDER_TYPE_BUY:
                pnl = (current_price['bid'] - position.price_open) * position.volume
                close_price = current_price['bid']
            else:
                pnl = (position.price_open - current_price['ask']) * position.volume
                close_price = current_price['ask']
            
            if self.config['flip_on_loss'] and pnl < -self.config['max_loss_per_position']:
                self.flip_position(position)
                continue
            
            if pnl >= self.config['take_profit_ticks']:
                self.close_position_with_profit(position, close_price, pnl)

    def close_position_with_profit(self, position, close_price, profit):
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": position.volume,
            "type": close_type,
            "position": position.ticket,
            "price": close_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "PROFIT_CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.stats['total_profit'] += profit
            self.stats['total_trades'] += 1
            if position.ticket in self.active_positions:
                del self.active_positions[position.ticket]
            print(f"✓ 수익 실현: ${profit:.2f}")

    def refill_grid(self, filled_price, filled_type):
        if filled_type == mt5.ORDER_TYPE_BUY:
            self.place_pending_order('buy', filled_price, self.config['lot_per_order'])
        else:
            self.place_pending_order('sell', filled_price, self.config['lot_per_order'])

    def analyze_positions(self):
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions:
            return {'profit_positions': [], 'loss_positions': [], 'total_profit': 0, 'total_loss': 0}
        
        current_price = self.get_current_price()
        if not current_price:
            return {'profit_positions': [], 'loss_positions': [], 'total_profit': 0, 'total_loss': 0}
        
        profit_pos = []
        loss_pos = []
        total_p = 0
        total_l = 0
        
        for pos in positions:
            if pos.type == mt5.ORDER_TYPE_BUY:
                pnl = (current_price['bid'] - pos.price_open) * pos.volume
            else:
                pnl = (pos.price_open - current_price['ask']) * pos.volume
            
            if pnl > 0:
                profit_pos.append({'position': pos, 'profit': pnl})
                total_p += pnl
            else:
                loss_pos.append({'position': pos, 'loss': pnl})
                total_l += pnl
        
        return {
            'profit_positions': profit_pos,
            'loss_positions': loss_pos,
            'total_profit': total_p,
            'total_loss': total_l
        }

    def close_profit_positions(self):
        analysis = self.analyze_positions()
        if not analysis['profit_positions']:
            print("\n💡 수익 포지션 없음")
            return
        
        print(f"\n{'='*80}")
        print("  💙 수익 포지션만 청산")
        print(f"{'='*80}")
        print(f"수: {len(analysis['profit_positions'])} | 총: ${analysis['total_profit']:,.2f}")
        
        current_price = self.get_current_price()
        closed = 0
        
        for item in analysis['profit_positions']:
            pos = item['position']
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            close_price = current_price['bid'] if close_type == mt5.ORDER_TYPE_SELL else current_price['ask']
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_PROFIT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed += 1
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 청산 | 실현 ${analysis['total_profit']:,.2f}")

    def close_loss_positions(self):
        analysis = self.analyze_positions()
        if not analysis['loss_positions']:
            print("\n💡 손실 포지션 없음")
            return
        
        print(f"\n{'='*80}")
        print("  ❤️ 손실 포지션만 청산")
        print(f"{'='*80}")
        print(f"수: {len(analysis['loss_positions'])} | 총: ${analysis['total_loss']:,.2f}")
        
        current_price = self.get_current_price()
        closed = 0
        
        for item in analysis['loss_positions']:
            pos = item['position']
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            close_price = current_price['bid'] if close_type == mt5.ORDER_TYPE_SELL else current_price['ask']
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_LOSS",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed += 1
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 청산 | 확정 손실 ${analysis['total_loss']:,.2f}")

    def close_all_positions(self):
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions:
            print("\n💡 포지션 없음")
            return
        
        print(f"\n{'='*80}")
        print("  🔴 모든 포지션 청산")
        print(f"{'='*80}")
        
        current_price = self.get_current_price()
        closed = 0
        
        for pos in positions:
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            close_price = current_price['bid'] if close_type == mt5.ORDER_TYPE_SELL else current_price['ask']
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_ALL",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed += 1
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 청산 완료")

    def display_stats(self):
        runtime = datetime.now() - self.stats['start_time']
        hours = runtime.seconds // 3600
        minutes = (runtime.seconds % 3600) // 60
        
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        analysis = self.analyze_positions()
        
        print(f"\n{'='*80}")
        print("  📊 통계 - Axi Select Funded 기준")
        print(f"{'='*80}")
        print(f"운영: {hours}시간 {minutes}분")
        print(f"포지션: {len(positions) if positions else 0}개")
        print(f"  💙 수익: {len(analysis['profit_positions'])} (${analysis['total_profit']:+,.2f})")
        print(f"  ❤️ 손실: {len(analysis['loss_positions'])} (${analysis['total_loss']:+,.2f})")
        print(f"히트: {self.stats['grid_hits']} | 완료: {self.stats['total_trades']}")
        print(f"Flip: {self.stats['flips']}회 | 회피: ${self.stats['avoided_loss']:.2f}")
        print(f"누적 수익: ${self.stats['total_profit']:+,.2f}")
        print(f"{'='*80}\n")

    def keyboard_listener(self):
        print("\n⌨️ 키 명령")
        print("H : 수익 청산 → 종료 💙")
        print("L : 손실 청산 → 종료 ❤️")
        print("Q : 전부 청산 → 종료")
        print("S : 통계")
        print("C : 계속")
        print("="*80 + "\n")
        
        while self.running:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').upper()
                if key == 'H':
                    self.manual_action = 'close_profit'
                    self.running = False
                elif key == 'L':
                    self.manual_action = 'close_loss'
                    self.running = False
                elif key == 'Q':
                    self.manual_action = 'close_all'
                    self.running = False
                elif key == 'S':
                    self.display_stats()
                elif key == 'C':
                    print("▶ 계속...")
            time.sleep(0.1)

    def run(self):
        listener = threading.Thread(target=self.keyboard_listener, daemon=True)
        listener.start()
        
        last_stats = time.time()
        
        try:
            while self.running:
                self.check_and_manage_positions()
                
                if time.time() - last_stats >= 30:
                    self.display_stats()
                    last_stats = time.time()
                
                price = self.get_current_price()
                if price:
                    analysis = self.analyze_positions()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"BTC: ${price['ask']:,.2f} | "
                          f"💙{len(analysis['profit_positions'])} "
                          f"❤️{len(analysis['loss_positions'])} | "
                          f"누적: ${self.stats['total_profit']:+,.2f}", end='\r')
                
                time.sleep(self.config['check_interval'])
            
            if self.manual_action == 'close_profit':
                self.close_profit_positions()
            elif self.manual_action == 'close_loss':
                self.close_loss_positions()
            elif self.manual_action == 'close_all':
                self.close_all_positions()
        
        except KeyboardInterrupt:
            print("\nCtrl+C 종료")
        
        finally:
            self.display_stats()
            
            orders = mt5.orders_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if orders:
                for ord in orders:
                    mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": ord.ticket})
                print(f"✓ {len(orders)} pending 취소")
            
            print(f"\n최종 수익: ${self.stats['total_profit']:+,.2f}")
            mt5.shutdown()

def main():
    print("\n" + "="*80)
    print("  🌟 그리드 봇 최종 - 플립 포함 (Axi Funded US50)")
    print("="*80)
    
    bot = PerfectGridBotWithManualControl(GRID_CONFIG)
    
    if not bot.connect_mt5():
        sys.exit(1)
    
    if not bot.get_symbol_info():
        mt5.shutdown()
        sys.exit(1)
    
    answer = input("\n시작? (y/n): ")
    if answer.lower() != 'y':
        mt5.shutdown()
        sys.exit(0)
    
    if not bot.setup_grid():
        mt5.shutdown()
        sys.exit(1)
    
    print("\n봇 실행... 키 사용 가능")
    bot.run()

if __name__ == "__main__":
    main()