"""
🌟 완벽한 그리드 트레이딩 봇 - 수동 청산 기능 🌟
- H 키: 수익 포지션만 청산하고 종료
- L 키: 손실 포지션만 청산하고 종료
- Q 키: 모든 포지션 청산하고 종료
- S 키: 현재 통계 확인
"""
import MetaTrader5 as mt5
import time
from datetime import datetime
import sys
import threading
import msvcrt  # Windows용 키 입력
from collections import defaultdict

# ==================== 설정 ====================
GRID_CONFIG = {
    'symbol': 'BTCUSD',
    'magic_number': 999999,
    
    # 그리드 전략
    'grid_spacing': 0.01,
    'grid_levels': 100,
    'lot_per_order': 0.01,
    
    # 손실 관리
    'max_loss_per_position': 0.02,
    'flip_on_loss': True,
    
    # 수익 목표
    'take_profit_ticks': 0.01,
    
    # 기타
    'max_spread': 100,
    'check_interval': 0.3,
    'deviation': 20,
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
        
    def connect_mt5(self):
        """MT5 연결"""
        print("\n" + "="*80)
        print("  🌟 완벽한 그리드 봇 - 수동 청산 기능")
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
    
    def clear_existing_positions_and_orders(self):
        """시작 전 모든 기존 포지션과 대기 주문 청산/취소"""
        print(f"\n{'='*80}")
        print(f"  🔄 기존 포지션 및 주문 정리 중...")
        print(f"{'='*80}\n")
        
        # 기존 포지션 청산
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if positions:
            current_price = self.get_current_price()
            if current_price:
                closed = 0
                for position in positions:
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
                        "comment": "CLEAR_EXISTING",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    
                    result = mt5.order_send(close_request)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        closed += 1
                    time.sleep(0.05)
                
                print(f"✅ {closed}개 기존 포지션 청산 완료!")
        
        # 기존 대기 주문 취소
        orders = mt5.orders_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if orders:
            canceled = 0
            for order in orders:
                remove_request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                result = mt5.order_send(remove_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    canceled += 1
                time.sleep(0.05)
            
            print(f"✅ {canceled}개 기존 대기 주문 취소 완료!")
        
        print(f"\n{'='*80}\n")
    
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
        print(f"레벨: {self.config['grid_levels']} × 2 = {self.config['grid_levels'] * 2}개")
        print(f"{'='*80}\n")
        
        print("📊 그리드 배치 중...")
        
        # 매수 주문
        for i in range(1, self.config['grid_levels'] + 1):
            buy_price = round(self.center_price - (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('buy', buy_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['buy'][buy_price] = order_id
            if i % 20 == 0:
                print(f"  매수 {i}/{self.config['grid_levels']}")
            time.sleep(0.03)
        
        # 매도 주문
        for i in range(1, self.config['grid_levels'] + 1):
            sell_price = round(self.center_price + (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('sell', sell_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['sell'][sell_price] = order_id
            if i % 20 == 0:
                print(f"  매도 {i}/{self.config['grid_levels']}")
            time.sleep(0.03)
        
        total = len(self.grid_orders['buy']) + len(self.grid_orders['sell'])
        print(f"\n✅ 그리드 완료: {total}개\n")
        
        return True
    
    def flip_position(self, position):
        """손실 포지션 방향 전환 (더 빠르고 강력하게: 즉시 처리, 재전환 가능, 손실 계산 최적화)"""
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        # 손실 계산
        if position.type == mt5.ORDER_TYPE_BUY:
            current_loss = (current_price['bid'] - position.price_open) * position.volume
            original_direction = "매수"
            new_direction = "매도"
            new_type = mt5.ORDER_TYPE_SELL
            new_price = current_price['bid']
            close_type = mt5.ORDER_TYPE_SELL
            close_price = current_price['bid']
        else:
            current_loss = (position.price_open - current_price['ask']) * position.volume
            original_direction = "매도"
            new_direction = "매수"
            new_type = mt5.ORDER_TYPE_BUY
            new_price = current_price['ask']
            close_type = mt5.ORDER_TYPE_BUY
            close_price = current_price['ask']
        
        # 청산
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
            return False
        
        # 즉시 반대 방향 진입 (지연 최소화)
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
            
            print(f"\n🔄 방향 전환! {original_direction} → {new_direction} | 회피: ${abs(current_loss):.4f}")
            
            self.active_positions[flip_result.order] = {
                'type': new_type,
                'entry_price': new_price,
                'volume': position.volume,
                'flipped': True  # 재전환 가능하도록 플래그 유지
            }
            
            if position.ticket in self.active_positions:
                del self.active_positions[position.ticket]
            
            return True
        
        return False
    
    def check_and_manage_positions(self):
        """포지션 관리 (더 빈번한 손실 체크로 방향 전환 강화)"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        if not positions:
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        for position in positions:
            # 새 포지션
            if position.ticket not in self.active_positions:
                self.active_positions[position.ticket] = {
                    'type': position.type,
                    'entry_price': position.price_open,
                    'volume': position.volume,
                    'flipped': False
                }
                self.stats['grid_hits'] += 1
                self.refill_grid(position.price_open, position.type)
            
            # 손익 계산
            if position.type == mt5.ORDER_TYPE_BUY:
                profit_loss = (current_price['bid'] - position.price_open) * position.volume
                close_price = current_price['bid']
            else:
                profit_loss = (position.price_open - current_price['ask']) * position.volume
                close_price = current_price['ask']
            
            # 손실 체크 및 방향 전환 (강화: flipped 여부 상관없이 손실 초과 시 전환, 빈번 체크)
            if self.config['flip_on_loss'] and profit_loss < -self.config['max_loss_per_position']:
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
    
    def analyze_positions(self):
        """포지션 분석"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        if not positions:
            return {'profit_positions': [], 'loss_positions': [], 'total_profit': 0, 'total_loss': 0}
        
        current_price = self.get_current_price()
        if not current_price:
            return {'profit_positions': [], 'loss_positions': [], 'total_profit': 0, 'total_loss': 0}
        
        profit_positions = []
        loss_positions = []
        total_profit = 0
        total_loss = 0
        
        for position in positions:
            if position.type == mt5.ORDER_TYPE_BUY:
                pnl = (current_price['bid'] - position.price_open) * position.volume
            else:
                pnl = (position.price_open - current_price['ask']) * position.volume
            
            if pnl > 0:
                profit_positions.append({'position': position, 'profit': pnl})
                total_profit += pnl
            else:
                loss_positions.append({'position': position, 'loss': pnl})
                total_loss += pnl
        
        return {
            'profit_positions': profit_positions,
            'loss_positions': loss_positions,
            'total_profit': total_profit,
            'total_loss': total_loss
        }
    
    def close_profit_positions(self):
        """수익 포지션만 청산 (파란불)"""
        analysis = self.analyze_positions()
        
        if not analysis['profit_positions']:
            print("\n💡 수익 포지션이 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"  💙 수익 포지션 청산 (파란불)")
        print(f"{'='*80}")
        print(f"수익 포지션: {len(analysis['profit_positions'])}개")
        print(f"총 수익: ${analysis['total_profit']:,.4f}")
        print(f"{'='*80}\n")
        
        current_price = self.get_current_price()
        closed = 0
        
        for item in analysis['profit_positions']:
            position = item['position']
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
                "comment": "MANUAL_PROFIT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(close_request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed += 1
                print(f"✓ 청산: {'매수' if position.type == mt5.ORDER_TYPE_BUY else '매도'} "
                      f"@ ${position.price_open:,.2f} → ${close_price:,.2f} "
                      f"| 수익: ${item['profit']:,.4f}")
            
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 수익 포지션 청산 완료!")
        print(f"💰 실현 수익: ${analysis['total_profit']:,.4f}")
    
    def close_loss_positions(self):
        """손실 포지션만 청산 (빨간불)"""
        analysis = self.analyze_positions()
        
        if not analysis['loss_positions']:
            print("\n💡 손실 포지션이 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"  ❤️ 손실 포지션 청산 (빨간불)")
        print(f"{'='*80}")
        print(f"손실 포지션: {len(analysis['loss_positions'])}개")
        print(f"총 손실: ${analysis['total_loss']:,.4f}")
        print(f"{'='*80}\n")
        
        current_price = self.get_current_price()
        closed = 0
        
        for item in analysis['loss_positions']:
            position = item['position']
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
                "comment": "MANUAL_LOSS",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(close_request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed += 1
                print(f"✓ 청산: {'매수' if position.type == mt5.ORDER_TYPE_BUY else '매도'} "
                      f"@ ${position.price_open:,.2f} → ${close_price:,.2f} "
                      f"| 손실: ${item['loss']:,.4f}")
            
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 손실 포지션 청산 완료!")
        print(f"❌ 확정 손실: ${analysis['total_loss']:,.4f}")
    
    def close_all_positions(self):
        """모든 포지션 청산"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        
        if not positions:
            print("\n💡 포지션이 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"  🔴 모든 포지션 청산")
        print(f"{'='*80}")
        
        current_price = self.get_current_price()
        closed = 0
        
        for position in positions:
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
                "comment": "MANUAL_ALL",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(close_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed += 1
            
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 포지션 청산 완료!")
    
    def display_stats(self):
        """통계"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
        
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        analysis = self.analyze_positions()
        
        print(f"\n{'='*80}")
        print(f"  📊 실시간 통계")
        print(f"{'='*80}")
        print(f"운영: {int(runtime)}시간 {int((runtime % 1) * 60)}분")
        print(f"포지션: {len(positions) if positions else 0}개")
        print(f"  💙 수익: {len(analysis['profit_positions'])}개 (${analysis['total_profit']:+,.4f})")
        print(f"  ❤️ 손실: {len(analysis['loss_positions'])}개 (${analysis['total_loss']:+,.4f})")
        print(f"히트: {self.stats['grid_hits']} | 완료: {self.stats['total_trades']}")
        print(f"🔄 방향전환: {self.stats['flips']}회")
        print(f"💰 누적 수익: ${self.stats['total_profit']:,.2f}")
        print(f"✅ 회피 손실: ${self.stats['avoided_loss']:,.2f}")
        print(f"{'='*80}\n")
    
    def keyboard_listener(self):
        """키보드 입력 감지 (키 입력 문제 해결: 대기 루프 최적화, 즉시 반응)"""
        print("\n" + "="*80)
        print("  ⌨️  키보드 명령")
        print("="*80)
        print("  H = 수익 포지션만 청산하고 종료 (파란불 💙)")
        print("  L = 손실 포지션만 청산하고 종료 (빨간불 ❤️)")
        print("  Q = 모든 포지션 청산하고 종료")
        print("  S = 현재 통계 보기")
        print("  C = 계속 실행")
        print("="*80 + "\n")
        
        while self.running:
            if msvcrt.kbhit():
                key = msvcrt.getch().upper()  # decode 제거, bytes 직접 upper 처리
                
                if key == b'H':
                    self.manual_action = 'close_profit'
                    self.running = False
                    break
                elif key == b'L':
                    self.manual_action = 'close_loss'
                    self.running = False
                    break
                elif key == b'Q':
                    self.manual_action = 'close_all'
                    self.running = False
                    break
                elif key == b'S':
                    self.display_stats()
                elif key == b'C':
                    print("\n▶️ 계속 실행 중...\n")
            
            time.sleep(0.05)  # 지연 줄여서 키 입력 더 빠르게 감지
    
    def run(self):
        """메인 루프"""
        # 키보드 리스너 시작
        listener_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        listener_thread.start()
        
        last_stats = time.time()
        
        try:
            while self.running:
                self.check_and_manage_positions()
                
                # 통계 (30초마다)
                if time.time() - last_stats >= 30:
                    self.display_stats()
                    last_stats = time.time()
                
                # 실시간 표시
                price = self.get_current_price()
                if price:
                    positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
                    analysis = self.analyze_positions()
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"BTC: ${price['ask']:,.2f} | "
                          f"💙{len(analysis['profit_positions'])} "
                          f"❤️{len(analysis['loss_positions'])} | "
                          f"수익: ${self.stats['total_profit']:+,.2f}", end='\r')
                
                time.sleep(self.config['check_interval'])
            
            # 수동 명령 처리
            if self.manual_action == 'close_profit':
                self.close_profit_positions()
            elif self.manual_action == 'close_loss':
                self.close_loss_positions()
            elif self.manual_action == 'close_all':
                self.close_all_positions()
            
        except KeyboardInterrupt:
            print("\n\nCtrl+C 감지")
        
        finally:
            # 최종 통계
            self.display_stats()
            
            # 대기 주문 정리
            orders = mt5.orders_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if orders:
                for order in orders:
                    mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": order.ticket})
                print(f"✓ {len(orders)}개 대기 주문 취소")
            
            print(f"\n최종 수익: ${self.stats['total_profit']:+,.2f}")
            print(f"회피 손실: ${self.stats['avoided_loss']:.2f}")
            
            mt5.shutdown()

def main():
    print("\n" + "="*80)
    print("  🌟 완벽한 그리드 봇 - 수동 청산 기능")
    print("="*80)
    print("\n핵심 기능:")
    print("  ✅ 0.01 간격 그리드")
    print("  ✅ 손실 방향전환 (강화)")
    print("  ✅ H키: 수익 포지션만 청산 (파란불 💙)")
    print("  ✅ L키: 손실 포지션만 청산 (빨간불 ❤️)")
    print("  ✅ Q키: 모든 포지션 청산")
    
    bot = PerfectGridBotWithManualControl(GRID_CONFIG)
    
    if not bot.connect_mt5():
        sys.exit(1)
    
    if not bot.get_symbol_info():
        mt5.shutdown()
        sys.exit(1)
    
    # 시작 전 기존 포지션/주문 정리
    bot.clear_existing_positions_and_orders()
    
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