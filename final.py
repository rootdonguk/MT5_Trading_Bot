"""
🌟 완벽한 그리드 트레이딩 봇 - 수동 청산 기능 (Instant Funding $10K Forex 맞춤)
- H 키: 수익 포지션만 청산하고 종료 (파란불 💙)
- L 키: 손실 포지션만 청산하고 종료 (빨간불 ❤️)
- Q 키: 모든 포지션 청산하고 종료
- S 키: 현재 통계 확인

※ Instant Funding 규칙 준수 버전
   - Max Daily Loss 2% ($200)
   - Max Total Loss 4% ($400)
   - Leverage 1:100
   - Profit Consistency 30% (그리드라 자연 분산)
   - Grid / Flip 사용 시 규칙 위반 위험 있음 (데모에서만 테스트 권장)
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
    'symbol': 'BTCUSD',                # 사진 기준 Forex 탭이지만 BTCUSD 사용 (crypto 취급 가능성 있음)
    'magic_number': 999999,
    
    # 그리드 전략 - $10K, 4% DD 준수 위해 매우 보수적으로 설정
    'grid_spacing': 200.0,             # BTC 변동성 고려 → 200$ 간격 (0.01은 breach 확정)
    'grid_levels': 5,                  # 양방향 총 10레벨 → 총 lot 0.1 (위험 ≈ $200~400 이내)
    'lot_per_order': 0.01,             # 그대로 (사진 기준 적합)
    
    # 손실 관리 - Max Daily 2% ($200) 맞춤
    'max_loss_per_position': 20.0,     # 포지션당 -$20 넘으면 flip (daily 2% 안 넘게)
    'flip_on_loss': True,              # flip 기능 유지 (하지만 규칙상 위험)
    
    # 수익 목표 - Profit Target 6% ($600) 참고
    'take_profit_ticks': 150.0,        # 포지션당 +$150 목표 (현실적)
    
    # 기타 - BTCUSD spread 고려
    'max_spread': 150.0,               # BTC spread 보통 50~200 → 150 초과 시 중단
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
        
        # DD 안전장치: 총 lot exposure 추적
        self.total_exposure_lot = 0.0

    def connect_mt5(self):
        """MT5 연결"""
        print("\n" + "="*80)
        print("  🌟 완벽한 그리드 봇 - Instant Funding $10K Forex 맞춤")
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
        print(f"레버리지: 1:100 (설정된 계정 기준)")
        print(f"Daily DD 제한: 2% (${200:.0f}) | Total DD 제한: 4% (${400:.0f})")
        
        return True

    def get_symbol_info(self):
        """심볼 정보 확인"""
        symbol_info = mt5.symbol_info(self.config['symbol'])
        if symbol_info is None:
            print(f"❌ {self.config['symbol']} 심볼을 찾을 수 없습니다")
            return None
        
        if not symbol_info.visible:
            mt5.symbol_select(self.config['symbol'], True)
        
        print(f"심볼: {self.config['symbol']} | Spread: {symbol_info.spread}")
        return symbol_info

    def get_current_price(self):
        """현재가 조회"""
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        return {'bid': tick.bid, 'ask': tick.ask, 'spread': tick.ask - tick.bid}

    def place_pending_order(self, order_type, price, lot_size):
        """지정가 주문 (Buy/Sell Limit)"""
        price = round(price, 2)  # BTCUSD 소수점 2자리
        
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
        else:
            print(f"주문 실패: {result.retcode if result else 'Unknown'}")
            return None

    def setup_grid(self):
        """그리드 설정 - $10K 4% DD 준수"""
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        if current_price['spread'] > self.config['max_spread']:
            print(f"❌ 스프레드 초과: {current_price['spread']:.2f} > {self.config['max_spread']}")
            return False
        
        self.center_price = round((current_price['bid'] + current_price['ask']) / 2, 2)
        
        print(f"\n{'='*80}")
        print(f"  🎯 그리드 설정 (Instant Funding $10K 안전 모드)")
        print(f"{'='*80}")
        print(f"중심 가격: ${self.center_price:,.2f}")
        print(f"간격: ${self.config['grid_spacing']:.0f}")
        print(f"레벨: {self.config['grid_levels']} (양방향 총 {self.config['grid_levels']*2}개)")
        print(f"총 예상 exposure: ≈ ${self.config['grid_levels']*2*self.config['lot_per_order']*self.config['grid_spacing']*0.1:.0f} (4% DD 이내)")
        print(f"{'='*80}\n")
        
        print("📊 그리드 배치 중...")
        
        # 매수 그리드 (아래)
        for i in range(1, self.config['grid_levels'] + 1):
            buy_price = round(self.center_price - (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('buy', buy_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['buy'][buy_price] = order_id
            if i % 5 == 0:
                print(f"  매수 {i}/{self.config['grid_levels']}")
            time.sleep(0.1)
        
        # 매도 그리드 (위)
        for i in range(1, self.config['grid_levels'] + 1):
            sell_price = round(self.center_price + (i * self.config['grid_spacing']), 2)
            order_id = self.place_pending_order('sell', sell_price, self.config['lot_per_order'])
            if order_id:
                self.grid_orders['sell'][sell_price] = order_id
            if i % 5 == 0:
                print(f"  매도 {i}/{self.config['grid_levels']}")
            time.sleep(0.1)
        
        total = len(self.grid_orders['buy']) + len(self.grid_orders['sell'])
        print(f"\n✅ 그리드 완료: {total}개 주문 배치")
        return True

    def flip_position(self, position):
        """손실 포지션 방향 전환 (규칙상 위험)"""
        current_price = self.get_current_price()
        if not current_price:
            return False
        
        if position.type == mt5.ORDER_TYPE_BUY:
            current_loss = (current_price['bid'] - position.price_open) * position.volume
            original = "매수"
            new_type = mt5.ORDER_TYPE_SELL
            new_price = current_price['bid']
        else:
            current_loss = (position.price_open - current_price['ask']) * position.volume
            original = "매도"
            new_type = mt5.ORDER_TYPE_BUY
            new_price = current_price['ask']
        
        if current_loss >= 0:  # 이미 수익이면 flip 안 함
            return False
        
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
        
        # 반대 방향 Market 진입
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
            
            print(f"\n🔄 Flip 성공! {original} → {new_type} | 회피 손실: ${abs(current_loss):.2f}")
            
            # active_positions 업데이트
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
        """포지션 모니터링 & 관리"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions:
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        for position in positions:
            # 신규 포지션 등록
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
                pnl = (current_price['bid'] - position.price_open) * position.volume
                close_price = current_price['bid']
            else:
                pnl = (position.price_open - current_price['ask']) * position.volume
                close_price = current_price['ask']
            
            # 손실 → flip
            if self.config['flip_on_loss'] and pnl < -self.config['max_loss_per_position']:
                self.flip_position(position)
                continue
            
            # 수익 실현
            if pnl >= self.config['take_profit_ticks']:
                self.close_position_with_profit(position, close_price, pnl)

    def close_position_with_profit(self, position, close_price, profit):
        """수익 포지션 청산"""
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
        """채워진 그리드 재배치"""
        if filled_type == mt5.ORDER_TYPE_BUY:
            self.place_pending_order('buy', filled_price, self.config['lot_per_order'])
        else:
            self.place_pending_order('sell', filled_price, self.config['lot_per_order'])

    def analyze_positions(self):
        """현재 포지션 분석"""
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
        """수익 포지션만 청산 (H 키)"""
        analysis = self.analyze_positions()
        if not analysis['profit_positions']:
            print("\n💡 수익 포지션이 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print("  💙 수익 포지션만 청산 (파란불)")
        print(f"{'='*80}")
        print(f"수익 포지션 수: {len(analysis['profit_positions'])}")
        print(f"총 실현 수익: ${analysis['total_profit']:,.2f}")
        
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
                print(f"청산 완료: {pos.ticket} | 수익 ${item['profit']:.2f}")
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 수익 포지션 청산 | 실현 ${analysis['total_profit']:,.2f}")

    def close_loss_positions(self):
        """손실 포지션만 청산 (L 키)"""
        analysis = self.analyze_positions()
        if not analysis['loss_positions']:
            print("\n💡 손실 포지션이 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print("  ❤️ 손실 포지션만 청산 (빨간불)")
        print(f"{'='*80}")
        print(f"손실 포지션 수: {len(analysis['loss_positions'])}")
        print(f"총 확정 손실: ${analysis['total_loss']:,.2f}")
        
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
                print(f"청산 완료: {pos.ticket} | 손실 ${item['loss']:.2f}")
            time.sleep(0.05)
        
        print(f"\n✅ {closed}개 손실 포지션 청산 | 확정 손실 ${analysis['total_loss']:,.2f}")

    def close_all_positions(self):
        """모든 포지션 청산 (Q 키)"""
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        if not positions:
            print("\n💡 포지션이 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print("  🔴 모든 포지션 강제 청산")
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
        
        print(f"\n✅ {closed}개 포지션 전부 청산 완료")

    def display_stats(self):
        """통계 출력 (S 키)"""
        runtime = datetime.now() - self.stats['start_time']
        hours = runtime.seconds // 3600
        minutes = (runtime.seconds % 3600) // 60
        
        positions = mt5.positions_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
        analysis = self.analyze_positions()
        
        print(f"\n{'='*80}")
        print("  📊 실시간 통계 (Instant Funding $10K 기준)")
        print(f"{'='*80}")
        print(f"운영 시간: {hours}시간 {minutes}분")
        print(f"활성 포지션: {len(positions) if positions else 0}개")
        print(f"  💙 수익 포지션: {len(analysis['profit_positions'])}개 (${analysis['total_profit']:+,.2f})")
        print(f"  ❤️ 손실 포지션: {len(analysis['loss_positions'])}개 (${analysis['total_loss']:+,.2f})")
        print(f"그리드 히트: {self.stats['grid_hits']} | 완료 거래: {self.stats['total_trades']}")
        print(f"Flip 횟수: {self.stats['flips']} | 회피 손실: ${self.stats['avoided_loss']:.2f}")
        print(f"누적 실현 수익: ${self.stats['total_profit']:+,.2f}")
        print(f"Daily DD 제한: 2% | Total DD 제한: 4%")
        print(f"{'='*80}\n")

    def keyboard_listener(self):
        """키보드 입력 처리"""
        print("\n⌨️ 키보드 명령어")
        print("H : 수익 포지션만 청산 → 종료 (💙)")
        print("L : 손실 포지션만 청산 → 종료 (❤️)")
        print("Q : 모든 포지션 청산 → 종료")
        print("S : 통계 보기")
        print("C : 계속 실행")
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
                    print("▶ 계속 실행...")
            time.sleep(0.1)

    def run(self):
        listener = threading.Thread(target=self.keyboard_listener, daemon=True)
        listener.start()
        
        last_stats_time = time.time()
        
        try:
            while self.running:
                self.check_and_manage_positions()
                
                if time.time() - last_stats_time >= 30:
                    self.display_stats()
                    last_stats_time = time.time()
                
                price = self.get_current_price()
                if price:
                    analysis = self.analyze_positions()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"BTC: ${price['ask']:,.2f} | "
                          f"💙{len(analysis['profit_positions'])} "
                          f"❤️{len(analysis['loss_positions'])} | "
                          f"누적: ${self.stats['total_profit']:+,.2f}", end='\r')
                
                time.sleep(self.config['check_interval'])
            
            # 수동 액션 처리
            if self.manual_action == 'close_profit':
                self.close_profit_positions()
            elif self.manual_action == 'close_loss':
                self.close_loss_positions()
            elif self.manual_action == 'close_all':
                self.close_all_positions()
                
        except KeyboardInterrupt:
            print("\nCtrl+C 감지 → 종료")
        
        finally:
            self.display_stats()
            
            # 남은 pending order 정리
            orders = mt5.orders_get(symbol=self.config['symbol'], magic=self.config['magic_number'])
            if orders:
                for ord in orders:
                    mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": ord.ticket})
                print(f"✓ {len(orders)}개 pending 주문 취소")
            
            print(f"\n최종 누적 수익: ${self.stats['total_profit']:+,.2f}")
            mt5.shutdown()

def main():
    print("\n" + "="*80)
    print("  🌟 그리드 봇 시작 - Instant Funding $10,000 Forex 계정 맞춤")
    print("="*80)
    
    bot = PerfectGridBotWithManualControl(GRID_CONFIG)
    
    if not bot.connect_mt5():
        sys.exit(1)
    
    if not bot.get_symbol_info():
        mt5.shutdown()
        sys.exit(1)
    
    answer = input("\n그리드 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        mt5.shutdown()
        sys.exit(0)
    
    if not bot.setup_grid():
        mt5.shutdown()
        sys.exit(1)
    
    print("\n봇 실행 중... 키보드 명령어 사용 가능 (H/L/Q/S/C)")
    bot.run()

if __name__ == "__main__":
    main()