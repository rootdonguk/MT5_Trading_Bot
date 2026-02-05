import MetaTrader5 as mt5
import time

symbol = "BTCUSD"
lot = 1.0          # 계좌 크기에 따라 조정 (전체 80~90% 몰빵)
direction = "buy"  # 또는 "sell" – 여기서 방향 한 번만 결정

mt5.initialize()

price = mt5.symbol_info_tick(symbol)
entry = price.ask if direction == "buy" else price.bid

sl_distance = 50.0   # 달러 단위 (0.07% 정도)
tp_distance = 300000 # 천문학적 목표 (현재가 +300,000$)

sl = entry - sl_distance if direction == "buy" else entry + sl_distance
tp = entry + tp_distance if direction == "buy" else entry - tp_distance

request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
    "price": entry,
    "sl": sl,
    "tp": tp,
    "deviation": 20,
    "magic": 777777,
    "comment": "ONE_LINE_REVOLUTION",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

result = mt5.order_send(request)

if result.retcode == mt5.TRADE_RETCODE_DONE:
    print("혁명 시작: 단 하나의 선으로 천문학적 수익을 향해...")
    print(f"진입: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
else:
    print("실패:", result)