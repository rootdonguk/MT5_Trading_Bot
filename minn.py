"""
🌟 완벽한 양방향 그리드 트레이딩 봇 - 수동 청산 + 동적 중심 🌟
- H 키: 수익 포지션만 청산하고 종료 (파란불 💙)
- L 키: 손실 포지션만 청산하고 종료 (빨간불 ❤️)
- Q 키: 모든 포지션 청산하고 종료
- S 키: 현재 통계 확인
- C 키: 계속 실행
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import sys
import threading
import msvcrt  # Windows 전용 키 입력
from collections import defaultdict

# ==================== 설정 ====================
GRID_CONFIG = {
    'symbol': 'BTCUSD',
    'magic_number': 999999,
    
    # 그리드 전략
    'grid_spacing': 100.0,          # BTCUSD 기준으로 100달러 간격 추천
    'grid_levels_below': 50,        # 아래쪽 (매수 Limit) 레벨 수
    'grid_levels_above': 50,        # 위쪽   (매도 Limit) 레벨 수
    'lot_per_order': 0.01,
    
    # 동적 중심가격 (가격이 많이 움직이면 그리드 중심 이동)
    'dynamic_center': True,
    'center_update_interval': 300,   # 초 단위 (5분)
    'center_move_threshold': 5,      # grid_spacing × 이 값 이상 움직이면 중심 이동
    
    # 손실 관리
    'max_loss_per_position': 200.0,  # 달러 단위 손실 허용치 (BTCUSD 기준 조정 필요)
    'flip_on_loss': True,
    
    # 수익 목표
    'take_profit_ticks': 150.0,      # 달러 단위
    
    # 기타
    'max_spread': 200,
    'check_interval': 0.4,
    'deviation': 30,
}

class PerfectGridBot:
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
        self.last_center_update = time.time()
        self.running = True
        self.manual_action = None

    def connect_mt5(self):
        print("\n" + "="*80)
        print("  🌟 양방향 그리드 봇 - 동적 중심 + 수동 청산")
        print("="*80)
        
        if not mt5.initialize():
            print("❌ MT5 초기화 실패")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보 없음")
            mt5.shutdown()
            return False
        
        print("\n✓ MT5 연결 성공")
        print(f"계좌: {account_info.login}")
        print(f"잔고: ${account_info.balance:,.2f}")
        print(f"증거금: ${account_info.equity:,.2f}")
        return True

    def get_current_price(self):
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        return {'bid': tick.bid, 'ask': tick.ask, 'spread': tick.ask - tick.bid}

    def place_pending_order(self, side, price, volume):
        if side == 'buy':
            req = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": f"GRID_BUY_{price:.1f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        else:
            req = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.config['symbol'],
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": price,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": f"GRID_SELL_{price:.1f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
        
        result = mt5.order_send(req)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            return result.order
        return None

    def clear_all_existing(self):
        print("\n🔄 기존 포지션 및 주문 정리 중...")
        
        positions = mt5.positions_get(symbol=self.config['symbol'])
        closed = 0
        if positions:
            price = self.get_current_price()
            if price:
                for pos in positions:
                    close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                    close_price = price['bid'] if close_type == mt5.ORDER_TYPE_SELL else price['ask']
                    req = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.config['symbol'],
                        "volume": pos.volume,
                        "type": close_type,
                        "position": pos.ticket,
                        "price": close_price,
                        "deviation": self.config['deviation'],
                        "magic": self.config['magic_number'],
                        "comment": "CLEAR_START",
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    mt5.order_send(req)
                    closed += 1
                    time.sleep(0.04)
            print(f"✓ {closed}개 기존 포지션 청산")

        orders = mt5.orders_get(symbol=self.config['symbol'])
        canceled = 0
        if orders:
            for ord in orders:
                mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": ord.ticket})
                canceled += 1
                time.sleep(0.04)
            print(f"✓ {canceled}개 대기 주문 취소")

    def setup_grid(self):
        price = self.get_current_price()
        if not price:
            return False
        
        self.center_price = round((price['bid'] + price['ask']) / 2, 1)
        print(f"\n🎯 그리드 중심 가격: ${self.center_price:,.1f}")
        print(f"간격: ${self.config['grid_spacing']:,.1f}")
        print(f"아래 매수 레벨: {self.config['grid_levels_below']}")
        print(f"위   매도 레벨: {self.config['grid_levels_above']}\n")

        # 아래 매수 Limit
        for i in range(1, self.config['grid_levels_below'] + 1):
            p = round(self.center_price - i * self.config['grid_spacing'], 1)
            oid = self.place_pending_order('buy', p, self.config['lot_per_order'])
            if oid:
                self.grid_orders['buy'][p] = oid
            time.sleep(0.025)

        # 위 매도 Limit
        for i in range(1, self.config['grid_levels_above'] + 1):
            p = round(self.center_price + i * self.config['grid_spacing'], 1)
            oid = self.place_pending_order('sell', p, self.config['lot_per_order'])
            if oid:
                self.grid_orders['sell'][p] = oid
            time.sleep(0.025)

        total = len(self.grid_orders['buy']) + len(self.grid_orders['sell'])
        print(f"✅ 그리드 배치 완료: {total}개 주문\n")
        return True

    def update_center_if_needed(self):
        if not self.config['dynamic_center']:
            return False
        
        if time.time() - self.last_center_update < self.config['center_update_interval']:
            return False

        price = self.get_current_price()
        if not price:
            return False
        
        new_center = round((price['bid'] + price['ask']) / 2, 1)
        diff = abs(new_center - self.center_price) / self.config['grid_spacing']
        
        if diff >= self.config['center_move_threshold']:
            print(f"\n🔄 중심 가격 이동: ${self.center_price:,.1f} → ${new_center:,.1f} (변동 {diff:.1f}배)")
            self.center_price = new_center
            self.last_center_update = time.time()
            return True
        return False

    def flip_position(self, pos):
        price = self.get_current_price()
        if not price:
            return False

        if pos.type == mt5.ORDER_TYPE_BUY:
            loss = (price['bid'] - pos.price_open) * pos.volume
            close_type = mt5.ORDER_TYPE_SELL
            close_price = price['bid']
            new_type = mt5.ORDER_TYPE_SELL
            new_price = price['bid']
            orig = "매수"
            new_dir = "매도"
        else:
            loss = (pos.price_open - price['ask']) * pos.volume
            close_type = mt5.ORDER_TYPE_BUY
            close_price = price['ask']
            new_type = mt5.ORDER_TYPE_BUY
            new_price = price['ask']
            orig = "매도"
            new_dir = "매수"

        # 청산
        close_req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": pos.volume,
            "type": close_type,
            "position": pos.ticket,
            "price": close_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "FLIP_CLOSE",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        r = mt5.order_send(close_req)
        if not r or r.retcode != mt5.TRADE_RETCODE_DONE:
            return False

        # 즉시 반대 진입
        open_req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": pos.volume,
            "type": new_type,
            "price": new_price,
            "deviation": self.config['deviation'],
            "magic": self.config['magic_number'],
            "comment": "FLIP_OPEN",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        r2 = mt5.order_send(open_req)
        
        if r2 and r2.retcode == mt5.TRADE_RETCODE_DONE:
            self.stats['flips'] += 1
            self.stats['avoided_loss'] += abs(loss)
            print(f"🔄 FLIP 성공 | {orig} → {new_dir} | 회피 ${abs(loss):,.2f}")
            
            self.active_positions[r2.order] = {
                'type': new_type,
                'entry_price': new_price,
                'volume': pos.volume
            }
            if pos.ticket in self.active_positions:
                del self.active_positions[pos.ticket]
            return True
        return False

    def check_and_manage_positions(self):
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return

        price = self.get_current_price()
        if not price:
            return

        for pos in positions:
            if pos.magic != self.config['magic_number']:
                continue

            ticket = pos.ticket
            if ticket not in self.active_positions:
                self.active_positions[ticket] = {
                    'type': pos.type,
                    'entry_price': pos.price_open,
                    'volume': pos.volume
                }
                self.stats['grid_hits'] += 1
                # refill은 생략하거나 원하는 대로 (현재는 재배치 안 함)

            # PnL 계산
            if pos.type == mt5.ORDER_TYPE_BUY:
                pnl = (price['bid'] - pos.price_open) * pos.volume
            else:
                pnl = (pos.price_open - price['ask']) * pos.volume

            # 손실 → flip
            if self.config['flip_on_loss'] and pnl < -self.config['max_loss_per_position']:
                self.flip_position(pos)
                continue

            # 수익 실현
            if pnl >= self.config['take_profit_ticks']:
                close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                close_price = price['bid'] if close_type == mt5.ORDER_TYPE_SELL else price['ask']
                
                req = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.config['symbol'],
                    "volume": pos.volume,
                    "type": close_type,
                    "position": pos.ticket,
                    "price": close_price,
                    "deviation": self.config['deviation'],
                    "magic": self.config['magic_number'],
                    "comment": "TP",
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                r = mt5.order_send(req)
                if r and r.retcode == mt5.TRADE_RETCODE_DONE:
                    self.stats['total_profit'] += pnl
                    self.stats['total_trades'] += 1
                    if ticket in self.active_positions:
                        del self.active_positions[ticket]

    def analyze_pnl(self):
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return {'profit': [], 'loss': [], 'total_p': 0, 'total_l': 0}

        price = self.get_current_price()
        if not price:
            return {'profit': [], 'loss': [], 'total_p': 0, 'total_l': 0}

        profit_list = []
        loss_list = []
        tp = 0
        tl = 0

        for pos in positions:
            if pos.magic != self.config['magic_number']:
                continue
            if pos.type == mt5.ORDER_TYPE_BUY:
                pnl = (price['bid'] - pos.price_open) * pos.volume
            else:
                pnl = (pos.price_open - price['ask']) * pos.volume
            
            if pnl > 0:
                profit_list.append({'pos': pos, 'pnl': pnl})
                tp += pnl
            else:
                loss_list.append({'pos': pos, 'pnl': pnl})
                tl += pnl

        return {'profit': profit_list, 'loss': loss_list, 'total_p': tp, 'total_l': tl}

    def close_profit_only(self):
        data = self.analyze_pnl()
        if not data['profit']:
            print("\n수익 포지션 없음")
            return
        
        print(f"\n💙 수익 포지션 청산 ({len(data['profit'])}개 | +${data['total_p']:,.2f})")
        price = self.get_current_price()
        count = 0
        for item in data['profit']:
            pos = item['pos']
            ctype = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            cprice = price['bid'] if ctype == mt5.ORDER_TYPE_SELL else price['ask']
            req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": ctype,
                "position": pos.ticket,
                "price": cprice,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_PROFIT",
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            r = mt5.order_send(req)
            if r and r.retcode == mt5.TRADE_RETCODE_DONE:
                count += 1
            time.sleep(0.04)
        print(f"→ {count}개 청산 완료")

    def close_loss_only(self):
        data = self.analyze_pnl()
        if not data['loss']:
            print("\n손실 포지션 없음")
            return
        
        print(f"\n❤️ 손실 포지션 청산 ({len(data['loss'])}개 | ${data['total_l']:,.2f})")
        price = self.get_current_price()
        count = 0
        for item in data['loss']:
            pos = item['pos']
            ctype = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            cprice = price['bid'] if ctype == mt5.ORDER_TYPE_SELL else price['ask']
            req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": ctype,
                "position": pos.ticket,
                "price": cprice,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_LOSS",
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            r = mt5.order_send(req)
            if r and r.retcode == mt5.TRADE_RETCODE_DONE:
                count += 1
            time.sleep(0.04)
        print(f"→ {count}개 청산 완료")

    def close_all(self):
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            print("\n포지션 없음")
            return
        
        print(f"\n🔴 모든 포지션 청산 ({len(positions)}개)")
        price = self.get_current_price()
        count = 0
        for pos in positions:
            if pos.magic != self.config['magic_number']:
                continue
            ctype = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            cprice = price['bid'] if ctype == mt5.ORDER_TYPE_SELL else price['ask']
            req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": pos.volume,
                "type": ctype,
                "position": pos.ticket,
                "price": cprice,
                "deviation": self.config['deviation'],
                "magic": self.config['magic_number'],
                "comment": "MANUAL_ALL",
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            r = mt5.order_send(req)
            if r and r.retcode == mt5.TRADE_RETCODE_DONE:
                count += 1
            time.sleep(0.04)
        print(f"→ {count}개 청산 완료")

    def show_stats(self):
        runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
        pos_count = len(mt5.positions_get(symbol=self.config['symbol']) or [])
        data = self.analyze_pnl()
        
        print(f"\n{'='*70}")
        print(f"📊 통계  |  운영시간: {int(runtime)}시간 {int(runtime%1*60)}분")
        print(f"{'='*70}")
        print(f"포지션 수: {pos_count}개")
        print(f"  💙 수익: {len(data['profit'])}개  (${data['total_p']:+,.2f})")
        print(f"  ❤️ 손실: {len(data['loss'])}개  (${data['total_l']:+,.2f})")
        print(f"그리드 히트: {self.stats['grid_hits']}")
        print(f"방향전환: {self.stats['flips']}회")
        print(f"누적 실현: ${self.stats['total_profit']:+,.2f}")
        print(f"회피한 손실: ${self.stats['avoided_loss']:,.2f}")
        print(f"{'='*70}\n")

    def keyboard_listener(self):
        print("키 명령:")
        print("  H → 수익만 청산 후 종료")
        print("  L → 손실만 청산 후 종료")
        print("  Q → 전부 청산 후 종료")
        print("  S → 통계 보기")
        print("  C → 계속 실행\n")

        while self.running:
            if msvcrt.kbhit():
                key = msvcrt.getch().upper()
                if key == b'H':
                    self.manual_action = 'profit'
                    self.running = False
                elif key == b'L':
                    self.manual_action = 'loss'
                    self.running = False
                elif key == b'Q':
                    self.manual_action = 'all'
                    self.running = False
                elif key == b'S':
                    self.show_stats()
                elif key == b'C':
                    print("▶ 계속 실행...\n")
            time.sleep(0.05)

    def run(self):
        threading.Thread(target=self.keyboard_listener, daemon=True).start()
        last_stats = time.time()

        try:
            while self.running:
                if self.update_center_if_needed():
                    # 필요 시 그리드 일부 재배치 로직 추가 가능 (현재는 단순 중심 이동만)
                    pass

                self.check_and_manage_positions()

                if time.time() - last_stats >= 25:
                    self.show_stats()
                    last_stats = time.time()

                price = self.get_current_price()
                if price:
                    data = self.analyze_pnl()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"{self.config['symbol']} ${price['ask']:,.1f} | "
                          f"💙{len(data['profit'])} ❤️{len(data['loss'])} | "
                          f"P/L ${self.stats['total_profit']:+,.2f}", end='\r')

                time.sleep(self.config['check_interval'])

            # 수동 액션 실행
            if self.manual_action == 'profit':
                self.close_profit_only()
            elif self.manual_action == 'loss':
                self.close_loss_only()
            elif self.manual_action == 'all':
                self.close_all()

        except KeyboardInterrupt:
            print("\nCtrl+C 감지")

        finally:
            self.show_stats()
            
            # 남은 대기 주문 정리
            orders = mt5.orders_get(symbol=self.config['symbol'])
            if orders:
                for o in orders:
                    mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket})
                print(f"✓ {len(orders)}개 대기 주문 취소")

            print(f"\n최종 실현 손익: ${self.stats['total_profit']:+,.2f}")
            print(f"회피한 손실 합계: ${self.stats['avoided_loss']:,.2f}")
            mt5.shutdown()

def main():
    bot = PerfectGridBot(GRID_CONFIG)
    
    if not bot.connect_mt5():
        sys.exit(1)
    
    bot.clear_all_existing()
    
    if input("\n그리드 시작? (y/n): ").lower() != 'y':
        mt5.shutdown()
        sys.exit(0)
    
    if not bot.setup_grid():
        mt5.shutdown()
        sys.exit(1)
    
    bot.run()

if __name__ == "__main__":
    main()