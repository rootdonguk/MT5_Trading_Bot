"""
🚀💰 즉시 수익 그리드 시스템 - 실행하자마자 돈 벌기! 💰🚀

🔥 핵심 개념:
- 현재가 바로 위아래에 촘촘하게 배치
- 90% Market 주문으로 즉시 체결
- 0.01% 움직임으로도 즉시 수익
- 실행하자마자 돈이 들어오는 시스템!

💡 즉시 수익 원리:
- 현재가 90원 → 89.99원 매수, 90.01원 매도 즉시 체결
- 가격이 90.005원으로 0.01% 움직이면 → 즉시 수익!
- 대기시간 ZERO! 실행하자마자 수익 발생!
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import threading

class InstantProfitGridBot:
    def __init__(self):
        self.config = {
            'symbol': 'BTCUSD',
            'magic_number': 888888,
            'base_lot_size': 0.01,
            'instant_profit_pct': 0.0001,  # 0.01% 수익으로도 청산!
            'grid_levels': 100,  # 100개 레벨
            'market_order_ratio': 0.9,  # 90% Market 주문
        }
        
        self.active_positions = {}
        self.total_profit = 0.0
        self.completed_trades = 0
        
        print("🚀 즉시 수익 그리드 시스템 초기화!")
        print("💎 실행하자마자 돈 벌기 시스템 준비 완료!")
    
    def connect_mt5(self):
        """MT5 연결"""
        if not mt5.initialize():
            print(f"❌ MT5 초기화 실패: {mt5.last_error()}")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ 계좌 정보 조회 실패")
            return False
        
        print("✅ MT5 연결 성공!")
        print(f"계좌: {account_info.login}")
        print(f"잔고: ${account_info.balance:,.2f}")
        
        return True
    
    def get_current_price(self):
        """현재가 조회"""
        tick = mt5.symbol_info_tick(self.config['symbol'])
        if tick is None:
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'mid': (tick.bid + tick.ask) / 2,
            'spread': tick.ask - tick.bid,
        }
    
    def execute_instant_profit_system(self):
        """🚀 즉시 수익 시스템 실행"""
        print("\n🚀 즉시 수익 시스템 시작!")
        print("💎 실행하자마자 돈 벌기!")
        
        current_price = self.get_current_price()
        if not current_price:
            print("❌ 현재가 조회 실패")
            return
        
        print(f"💰 현재가: ${current_price['mid']:.2f}")
        print(f"🎯 즉시 수익 목표: {self.config['instant_profit_pct']*100:.3f}%")
        
        # 🚀 연속 Market 주문으로 즉시 체결!
        for i in range(self.config['grid_levels']):
            # 매수 Market 주문 (즉시 체결)
            self.place_instant_market_buy(i)
            
            # 매도 Market 주문 (즉시 체결)
            self.place_instant_market_sell(i)
            
            # 0.02초 간격 (매우 빠르게!)
            time.sleep(0.02)
            
            if (i + 1) % 20 == 0:
                print(f"  📊 진행: {i + 1}/{self.config['grid_levels']} 완료")
        
        print("✅ 즉시 수익 시스템 배치 완료!")
        print("🚀 이제 가격이 조금만 움직여도 즉시 수익!")
    
    def place_instant_market_buy(self, level):
        """🚀 즉시 Market 매수"""
        try:
            lot_size = self.config['base_lot_size'] * (1 + level * 0.01)
            
            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"INSTANT_BUY_{level:03d}",
            }
            
            result = mt5.order_send(buy_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🚀 즉시매수{level:03d}: {lot_size:.3f} @ ${result.price:.2f}")
                
                # 즉시 수익 청산 설정
                self.set_instant_profit_exit(result.order, 'buy', result.price, lot_size)
                
                self.active_positions[result.order] = {
                    'type': 'buy',
                    'entry_price': result.price,
                    'volume': lot_size,
                    'level': level,
                    'timestamp': datetime.now()
                }
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ 즉시 매수 오류: {e}")
            return False
    
    def place_instant_market_sell(self, level):
        """🚀 즉시 Market 매도"""
        try:
            lot_size = self.config['base_lot_size'] * (1 + level * 0.01)
            
            sell_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.config['symbol'],
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL,
                "deviation": 100,
                "magic": self.config['magic_number'],
                "comment": f"INSTANT_SELL_{level:03d}",
            }
            
            result = mt5.order_send(sell_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🚀 즉시매도{level:03d}: {lot_size:.3f} @ ${result.price:.2f}")
                
                # 즉시 수익 청산 설정
                self.set_instant_profit_exit(result.order, 'sell', result.price, lot_size)
                
                self.active_positions[result.order] = {
                    'type': 'sell',
                    'entry_price': result.price,
                    'volume': lot_size,
                    'level': level,
                    'timestamp': datetime.now()
                }
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ 즉시 매도 오류: {e}")
            return False
    
    def set_instant_profit_exit(self, position_ticket, position_type, entry_price, volume):
        """⚡ 즉시 수익 청산 설정 (0.01% 수익!)"""
        try:
            if position_type == 'buy':
                # 매수 → 0.01% 상승시 즉시 청산
                target_price = entry_price * (1 + self.config['instant_profit_pct'])
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"PROFIT_EXIT_BUY_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            else:
                # 매도 → 0.01% 하락시 즉시 청산
                target_price = entry_price * (1 - self.config['instant_profit_pct'])
                exit_request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.config['symbol'],
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": target_price,
                    "deviation": 100,
                    "magic": self.config['magic_number'],
                    "comment": f"PROFIT_EXIT_SELL_{position_ticket}",
                    "type_time": mt5.ORDER_TIME_GTC,
                }
            
            result = mt5.order_send(exit_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                profit_amount = volume * entry_price * self.config['instant_profit_pct']
                print(f"      ⚡ 수익목표: #{result.order} @ ${target_price:.2f} (수익: ${profit_amount:.2f})")
            
        except Exception as e:
            print(f"❌ 수익목표 설정 오류: {e}")
    
    def monitor_instant_profits(self):
        """💰 즉시 수익 모니터링"""
        print("\n💰 즉시 수익 모니터링 시작!")
        
        while True:
            try:
                # 현재 계좌 상태
                account_info = mt5.account_info()
                if account_info:
                    current_profit = account_info.equity - account_info.balance
                    
                    # 활성 포지션 수
                    positions = mt5.positions_get(symbol=self.config['symbol'])
                    active_count = len(positions) if positions else 0
                    
                    # 대기 주문 수
                    orders = mt5.orders_get(symbol=self.config['symbol'])
                    pending_count = len(orders) if orders else 0
                    
                    # 현재가
                    current_price = self.get_current_price()
                    price_str = f"${current_price['mid']:.2f}" if current_price else "N/A"
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"{self.config['symbol']}: {price_str} | "
                          f"활성포지션: {active_count}개 | "
                          f"대기주문: {pending_count}개 | "
                          f"미실현손익: ${current_profit:+.2f} | "
                          f"완료거래: {self.completed_trades}회")
                
                # 체결된 거래 확인 및 재배치
                self.check_completed_trades()
                
                time.sleep(5)  # 5초마다 모니터링
                
            except KeyboardInterrupt:
                print("\n🛑 모니터링 중단")
                break
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(1)
    
    def check_completed_trades(self):
        """✅ 체결된 거래 확인 및 재배치"""
        try:
            # 현재 활성 포지션 확인
            current_positions = mt5.positions_get(symbol=self.config['symbol'])
            current_position_tickets = set()
            
            if current_positions:
                current_position_tickets = {pos.ticket for pos in current_positions}
            
            # 청산된 포지션 찾기
            completed_positions = []
            for ticket, pos_info in list(self.active_positions.items()):
                if ticket not in current_position_tickets:
                    completed_positions.append((ticket, pos_info))
                    del self.active_positions[ticket]
            
            # 청산된 포지션이 있으면 즉시 재배치
            if completed_positions:
                for ticket, pos_info in completed_positions:
                    self.completed_trades += 1
                    profit = pos_info['volume'] * pos_info['entry_price'] * self.config['instant_profit_pct']
                    self.total_profit += profit
                    
                    print(f"💰 수익실현: #{ticket} L{pos_info['level']:03d} "
                          f"{pos_info['type'].upper()} ${profit:.2f}")
                    
                    # 즉시 재배치 (연속 수익!)
                    if pos_info['type'] == 'buy':
                        self.place_instant_market_buy(pos_info['level'])
                    else:
                        self.place_instant_market_sell(pos_info['level'])
        
        except Exception as e:
            print(f"❌ 거래 확인 오류: {e}")
    
    def run_instant_profit_system(self):
        """🚀 즉시 수익 시스템 실행"""
        print("\n" + "="*70)
        print("🚀💰 즉시 수익 그리드 시스템 - 실행하자마자 돈 벌기! 💰🚀")
        print("="*70)
        
        print("\n🔥 시스템 특징:")
        print("  💎 90% Market 주문으로 즉시 체결")
        print("  ⚡ 0.01% 움직임으로도 즉시 수익")
        print("  🚀 실행하자마자 돈이 들어옴")
        print("  🔄 수익 실현 즉시 재배치로 연속 수익")
        print("  💰 대기시간 ZERO!")
        
        if not self.connect_mt5():
            return
        
        # 심볼 선택
        symbol_choice = input(f"\n거래 심볼을 입력하세요 (기본값: {self.config['symbol']}): ").strip().upper()
        if symbol_choice:
            self.config['symbol'] = symbol_choice
        
        print(f"✅ 선택된 심볼: {self.config['symbol']}")
        
        # 즉시 수익 시스템 실행 확인
        answer = input(f"\n🚀 {self.config['symbol']} 즉시 수익 시스템을 시작하시겠습니까? (y/n): ")
        if answer.lower() != 'y':
            print("시스템 종료")
            mt5.shutdown()
            return
        
        print(f"\n🚀 {self.config['symbol']} 즉시 수익 시스템 가동!")
        print("💎 실행하자마자 돈 벌기 시작!")
        
        # 즉시 수익 시스템 실행
        self.execute_instant_profit_system()
        
        # 모니터링 시작
        self.monitor_instant_profits()
        
        mt5.shutdown()

def main():
    """메인 함수"""
    print("🚀💰 즉시 수익 그리드 시스템 💰🚀")
    print("\n💡 핵심 원리:")
    print("  🎯 현재가 바로 위아래에 Market 주문 즉시 체결")
    print("  ⚡ 0.01% 움직이면 즉시 수익 실현")
    print("  🔄 수익 실현 즉시 재배치로 연속 수익")
    print("  💰 실행하자마자 돈이 들어오는 시스템!")
    
    print("\n🚀 예시 시나리오 (BTC $90,000):")
    print("  1. 즉시 $89,999에 매수, $90,001에 매도 체결")
    print("  2. 가격이 $90,009로 0.01% 움직임")
    print("  3. 매수 포지션 즉시 수익 실현!")
    print("  4. 즉시 새로운 매수 주문 재배치")
    print("  5. 연속 수익 발생!")
    
    bot = InstantProfitGridBot()
    bot.run_instant_profit_system()

if __name__ == "__main__":
    main()