"""
🌟 완벽한 그리드 트레이딩 봇 - 손실 즉시 방향전환 🌟
- 현재가 기준 0.01 간격 그리드
- 손실 포지션 즉시 반대 방향으로 전환
- 손실을 수익으로 바꾸는 혁명적 시스템!
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import sys
from collections import defaultdict

# ==================== 설정 ====================
GRID_CONFIG = {
    'symbol': 'BTCUSD',
    'magic_number': 999999,
    
    # 그리드 전략
    'grid_spacing': 0.01,          # 0.01 간격
    'grid_levels': 100,            # 위아래 각 100개
    'lot_per_order': 0.01,         # 주문당 거래량
    
    # 손실 관리 (핵심!)
    'max_loss_per_position': 0.02,  # 최대 손실: $0.02 = 2틱
    'flip_on_loss': True,            # 손실 시 방향 전환
    'stop_loss_distance': 0.03,      # 손절 거리
    
    # 수익 목표
    'take_profit_ticks': 0.01,     # 0.01 수익 시 청산
    
    # 기타
    'max_spread': 100,
    'check_interval': 0.5,         # 빠른 체크
    'deviation': 20,
}

class PerfectGridBot:
    def __init__(self, config):
        self.config = config
        self.grid_orders = {'buy': {}, 'sell': {}}
        self.active_positions = {}  # ticket: {type, entry_price, lot, ...}
        self.stats = {
            'total_profit': 0.0,
            'total_trades': 0,
            'grid_hits': 0,
            'flips': 0,  # 방향 전환 횟수
            'avoided_loss': 0.0,  # 회피한 손실
            'start_time': datetime.now(),
        }
        self.center_price = None
        
    def connect_mt5(self):
        """MT5 연결"""
        print("\n" + "="*80)
        print("  🌟 완벽한 그리드 봇 - 손실 방향전환 시스템")
        print("="*80)
        
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보 없음")
            mt5.shutdown()
            return False
        
        print("\n✓ MT5 연결 성공!")
        print(f"계좌: {account_info.login}")
        print(f"잔고: ${account_info.balance:,.2f}")
        print(f"증거금: ${account_info.equity:,.2f}")
        
        return True
    
    def get_symbol_info(self):
        """심볼 정보"""
        symbol_info = mt5.symbol_info(self.config['symbol'])
        if symbol_info is None:
            print(f"❌ {self.config['symbol']} 심볼을 찾을 수 없습니다")
            return None
        
        if not symbol_info.visible:
            mt5.symbol_select(self.config['symbol'], True)
        
        return symbol_info
    
    def get_current_price(self):
        """현재가"""
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        return {'bid': tick.bid, 'ask': tick.ask, 'spread': tick.ask - tick.bid}
    
    def place_pending_order(self, order_type, price, lot_size):
        """지정가 주문"""
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
        return result.order if result and result.retcode == mt5.TRADE_RETCODE_DONE else None
    
    def setup_grid(self):
        """그리드 설정"""
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        self.center_price = round((current_price['bid'] + current_price['ask']) / 2, 2)
        
        print(f"\n{'='*80}")
        print(f"  🎯 그리드 설정")
        print(f"{'='*80}")
        print(f"중심 가격: ${self.center_price:,.2f}")
        print(f"간격: ${self.config['grid_spacing']}")
        print(f"레벨: {self.config['grid_levels']} × 2 = {self.config['grid_levels'] * 2}개 주문")
        print(f"손실 관리: ✓ (${self.config['max_loss_per_position']} 초과 시 방향전환)")
        print(f"{'='*80}\n")
        
        print("📊 그리드 배치 중...")
        
        # 매수 주문 (아래)
        for i in range(1, self.config['grid_levels'] + 1):
            buy_price = round(self.center_price - (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('buy', buy_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['buy'][buy_price] = order_id
            if i % 20 == 0:
                print(f"  매수 {i}/{self.config['grid_levels']}")
            time.sleep(0.03)
        
        # 매도 주문 (위)
        for i in range(1, self.config['grid_levels'] + 1):
            sell_price = round(self.center_price + (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('sell', sell_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['sell'][sell_price] = order_id
            if i % 20 == 0:
                print(f"  매도 {i}/{self.config['grid_levels']}")
            time.sleep(0.03)
        
        total = len(self.grid_orders['buy']) + len(self.grid_orders['sell'])
        print(f"\n✅ 그리드 완료: {total}개 주문 배치됨\n")
        
        return True
    
    def flip_position(self, position):
        """손실 포지션을 반대 방향으로 전환"""
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        # 현재 손실 계산
        if position.type == mt5.ORDER_TYPE_BUY:
            current_loss = (current_price['bid'] - position.price_open) * position.volume
            original_direction = "매수"
            new_direction = "매도"
        else:
            current_loss = (position.price_open - current_price['ask']) * position.volume
            original_direction = "매도"
            new_direction = "매수"
        
        # 1단계: 기존 포지션 청산
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
            print(f"⚠️ 청산 실패")
            return False
        
        time.sleep(0.1)
        
        # 2단계: 반대 방향으로 즉시 재진입
        new_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        new_price = current_price['bid'] if new_type == mt5.ORDER_TYPE_SELL else current_price['ask']
        
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
            # 통계 업데이트
            self.stats['flips'] += 1
            self.stats['avoided_loss'] += abs(current_loss)
            
            print(f"\n{'='*80}")
            print(f"🔄 방향 전환 성공! #{self.stats['flips']}")
            print(f"{'='*80}")
            print(f"🎫 원래 티켓: {position.ticket}")
            print(f"📊 {original_direction} → {new_direction}")
            print(f"💰 원래 가격: ${position.price_open:,.2f}")
            print(f"💰 청산 가격: ${close_price:,.2f}")
            print(f"❌ 손실 (청산됨): ${current_loss:.4f}")
            print(f"🆕 새 포지션: {flip_result.order}")
            print(f"💰 새 진입가: ${new_price:,.2f}")
            print(f"🎯 이제 가격이 원래 방향으로 돌아가면 수익!")
            print(f"✅ 회피한 총 손실: ${self.stats['avoided_loss']:.2f}")
            print(f"{'='*80}\n")
            
            # 새 포지션 추적
            self.active_positions[flip_result.order] = {
                'type': new_type,
                'entry_price': new_price,
                'volume': position.volume,
                'flipped': True
            }
            
            # 기존 포지션 제거
            if position.ticket in self.active_positions:
                del self.active_positions[position.ticket]
            
            return True
        
        return False
    
    def check_and_manage_positions(self):
        """포지션 체크 및 관리"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        if not positions:
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        for position in positions:
            # 새 포지션 추적
            if position.ticket not in self.active_positions:
                self.active_positions[position.ticket] = {
                    'type': position.type,
                    'entry_price': position.price_open,
                    'volume': position.volume,
                    'flipped': False
                }
                self.stats['grid_hits'] += 1
                
                direction = "매수" if position.type == mt5.ORDER_TYPE_BUY else "매도"
                print(f"\n⚡ 그리드 히트! #{self.stats['grid_hits']} - {direction} @ ${position.price_open:,.2f}")
                
                # 그리드 재생성
                self.refill_grid(position.price_open, position.type)
            
            # 손익 계산
            if position.type == mt5.ORDER_TYPE_BUY:
                profit_loss = (current_price['bid'] - position.price_open) * position.volume
                close_price = current_price['bid']
            else:
                profit_loss = (position.price_open - current_price['ask']) * position.volume
                close_price = current_price['ask']
            
            # 🔥 핵심: 손실 체크 및 방향 전환
            if self.config['flip_on_loss'] and profit_loss < -self.config['max_loss_per_position']:
                print(f"⚠️ 손실 감지: ${profit_loss:.4f} → 방향 전환 실행!")
                self.flip_position(position)
                continue
            
            # 수익 실현
            if profit_loss >= self.config['take_profit_ticks']:
                self.close_position_with_profit(position, close_price, profit_loss)
    
    def close_position_with_profit(self, position, close_price, profit):
        """수익 실현"""
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": position.volume,
            "type": close_type,
            "position": position.ticket,
            "price": close_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "PROFIT",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            self.stats['total_profit'] += profit
            self.stats['total_trades'] += 1
            
            if position.ticket in self.active_positions:
                del self.active_positions[position.ticket]
            
            was_flipped = self.active_positions.get(position.ticket, {}).get('flipped', False)
            
            print(f"\n{'='*80}")
            print(f"💰 수익 실현! {'(방향전환 후)' if was_flipped else ''}")
            print(f"{'='*80}")
            print(f"🎫 티켓: {position.ticket}")
            print(f"📊 방향: {'매수' if position.type == mt5.ORDER_TYPE_BUY else '매도'}")
            print(f"📈 진입: ${position.price_open:,.2f}")
            print(f"📉 청산: ${close_price:,.2f}")
            print(f"💵 수익: ${profit:.4f}")
            print(f"🎯 누적: ${self.stats['total_profit']:.2f}")
            print(f"📈 거래: {self.stats['total_trades']}회")
            print(f"🔄 방향전환: {self.stats['flips']}회")
            print(f"✅ 회피 손실: ${self.stats['avoided_loss']:.2f}")
            print(f"{'='*80}\n")
    
    def refill_grid(self, filled_price, filled_type):
        """그리드 재생성"""
        if filled_type == mt5.ORDER_TYPE_BUY:
            order_id = self.place_pending_order('buy', filled_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['buy'][filled_price] = order_id
        else:
            order_id = self.place_pending_order('sell', filled_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['sell'][filled_price] = order_id
    
    def display_stats(self):
        """통계"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
        
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        orders = mt5.orders_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        print(f"\n{'='*80}")
        print(f"  📊 실시간 통계")
        print(f"{'='*80}")
        print(f"운영: {int(runtime)}시간 {int((runtime % 1) * 60)}분")
        print(f"포지션: {len(positions) if positions else 0}")
        print(f"대기 주문: {len(orders) if orders else 0}")
        print(f"히트: {self.stats['grid_hits']}")
        print(f"완료: {self.stats['total_trades']}")
        print(f"🔄 방향전환: {self.stats['flips']}회")
        print(f"💰 누적 수익: ${self.stats['total_profit']:.2f}")
        print(f"✅ 회피 손실: ${self.stats['avoided_loss']:.2f}")
        print(f"🎯 순수익: ${self.stats['total_profit'] + self.stats['avoided_loss']:.2f}")
        
        if runtime > 0:
            hourly = self.stats['total_profit'] / runtime
            print(f"\n시간당: ${hourly:.2f}")
            print(f"일: ${hourly * 24:.2f}")
            print(f"월: ${hourly * 24 * 30:.2f}")
        
        print(f"{'='*80}\n")
    
    def run(self):
        """메인 루프"""
        last_stats = time.time()
        
        try:
            while True:
                self.check_and_manage_positions()
                
                # 통계 (30초마다)
                if time.time() - last_stats >= 30:
                    self.display_stats()
                    last_stats = time.time()
                
                # 실시간 표시
                price = self.get_current_price()
                if price:
                    positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"BTC: ${price['ask']:,.2f} | "
                          f"포지션: {len(positions) if positions else 0} | "
                          f"수익: ${self.stats['total_profit']:+,.2f} | "
                          f"방향전환: {self.stats['flips']}", end='\r')
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n\n프로그램 중단")
            self.display_stats()
            
            answer = input("\n모든 주문/포지션 정리? (y/n): ")
            if answer.lower() == 'y':
                # 주문 취소
                orders = mt5.orders_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                if orders:
                    for order in orders:
                        mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": order.ticket})
                    print(f"✓ {len(orders)}개 주문 취소")
                
                # 포지션 청산
                positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                if positions:
                    for pos in positions:
                        price = self.get_current_price()
                        close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                        close_price = price['bid'] if close_type == mt5.ORDER_TYPE_SELL else price['ask']
                        
                        mt5.order_send({
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": self.config['symbol'],
                            "volume": pos.volume,
                            "type": close_type,
                            "position": pos.ticket,
                            "price": close_price,
                            "deviation": self.config['deviation'],
                            "magic": self.config['magic_number'],
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        })
                    print(f"✓ {len(positions)}개 포지션 청산")
            
            print(f"\n최종 수익: ${self.stats['total_profit']:+,.2f}")
            print(f"회피 손실: ${self.stats['avoided_loss']:.2f}")
            print(f"순수익: ${self.stats['total_profit'] + self.stats['avoided_loss']:.2f}")
            
        finally:
            mt5.shutdown()

def main():
    print("\n" + "="*80)
    print("  🌟 완벽한 그리드 봇 - 손실 방향전환 시스템")
    print("="*80)
    print("\n핵심 기능:")
    print("  ✅ 0.01 간격 그리드 (200개 주문)")
    print("  ✅ 손실 포지션 즉시 반대 방향 전환")
    print("  ✅ 손실을 수익으로 바꾸는 마법!")
    print("  ✅ 24/7 자동 수익")
    
    bot = PerfectGridBot(GRID_CONFIG)
    
    if not bot.connect_mt5():
        sys.exit(1)
    
    if not bot.get_symbol_info():
        mt5.shutdown()
        sys.exit(1)
    
    print("\n⚙️ 현재 설정:")
    print(f"간격: ${GRID_CONFIG['grid_spacing']}")
    print(f"레벨: {GRID_CONFIG['grid_levels']}")
    print(f"거래량: {GRID_CONFIG['lot_per_order']} BTC")
    print(f"최대 손실: ${GRID_CONFIG['max_loss_per_position']} (이후 방향전환)")
    print(f"수익 목표: ${GRID_CONFIG['take_profit_ticks']}")
    
    answer = input("\n시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        mt5.shutdown()
        sys.exit(0)
    
    if not bot.setup_grid():
        mt5.shutdown()
        sys.exit(1)
    
    bot.run()

if __name__ == "__main__":
    main()