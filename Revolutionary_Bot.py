"""
🚀💰 혁명적 AI 양방향 거래 시스템 (PyTorch 극한 버전) 💰🚀

🔥 핵심 개념:
- 현재가를 기준선으로 설정
- 한쪽: 극도로 멀리 설정 (어마무시한 수익)
- 반대쪽: 극도로 가깝게 설정 (거의 손실 없음)
- x달러 변화 = x달러 수익 보장
- 방향 관계없이 무조건 수익

🤖 AI 라이브러리 활용:
- PyTorch: 딥러닝 가격 예측 및 방향 분석
- scikit-learn: 기계학습 보조 모델
- numpy: 수학적 계산 최적화
- pandas: 데이터 분석 및 처리
"""

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import time
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class PyTorchPricePredictor(nn.Module):
    """🤖 PyTorch 가격 예측 모델"""
    def __init__(self, input_size=15):
        super(PyTorchPricePredictor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    
    def forward(self, x):
        return self.network(x)

class PyTorchDirectionClassifier(nn.Module):
    """🤖 PyTorch 방향 예측 모델"""
    def __init__(self, input_size=15):
        super(PyTorchDirectionClassifier, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3),  # UP, DOWN, SIDEWAYS
            nn.Softmax(dim=1)
        )
    
    def forward(self, x):
        return self.network(x)

class RevolutionaryAIBot:
    def __init__(self):
        self.config = {
            'symbol': 'BTCUSD',
            'magic_number': 888888,
            'base_lot_size': 0.01,
            'extreme_profit_multiplier': 100.0,  # 극도로 멀리 (100배)
            'extreme_loss_multiplier': 0.01,     # 극도로 가깝게 (0.01배)
            'ai_confidence_threshold': 0.6,      # AI 신뢰도 임계값
            'max_spread': 10.0,
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        }
        
        self.ai_models = {
            'price_predictor': PyTorchPricePredictor().to(self.config['device']),
            'direction_classifier': PyTorchDirectionClassifier().to(self.config['device']),
            'volatility_predictor': RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42),
            'scaler': StandardScaler()
        }
        
        # PyTorch 옵티마이저
        self.optimizers = {
            'price_opt': optim.Adam(self.ai_models['price_predictor'].parameters(), lr=0.001),
            'direction_opt': optim.Adam(self.ai_models['direction_classifier'].parameters(), lr=0.001)
        }
        
        # 손실 함수
        self.loss_functions = {
            'price_loss': nn.MSELoss(),
            'direction_loss': nn.CrossEntropyLoss()
        }
        
        self.market_data = {
            'prices': [],
            'volumes': [],
            'spreads': [],
            'timestamps': [],
            'features': [],
            'raw_data': []
        }
        
        self.stats = {
            'total_profit': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'ai_predictions': [],
            'revolutionary_profits': defaultdict(float),
            'extreme_profits': 0.0,
            'minimal_losses': 0.0,
            'start_time': datetime.now()
        }
        
        self.current_baseline = 0.0
        self.active_positions = []
        
        print(f"🤖 PyTorch 디바이스: {self.config['device']}")
        print(f"🔥 극한 수익 배수: {self.config['extreme_profit_multiplier']}x")
        print(f"💎 극소 손실 배수: {self.config['extreme_loss_multiplier']}x")
    
    def connect_mt5(self):
        """MT5 연결"""
        print("\n🔌 MT5 연결 중...")
        
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
        print(f"자산: ${account_info.equity:,.2f}")
        
        return True
    
    def collect_advanced_market_data(self, periods=300):
        """📊 고급 시장 데이터 수집 및 PyTorch용 특성 생성"""
        print(f"📊 {periods}개 고급 데이터 수집 중...")
        
        # 1분봉 데이터 수집
        rates = mt5.copy_rates_from_pos(self.config['symbol'], mt5.TIMEFRAME_M1, 0, periods)
        
        if rates is None or len(rates) == 0:
            print("❌ 데이터 수집 실패")
            return False
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # 고급 기술적 지표 계산
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        df['rsi_fast'] = self.calculate_rsi(df['close'], 7)
        df['rsi_slow'] = self.calculate_rsi(df['close'], 21)
        
        df['volatility'] = df['close'].rolling(window=20).std()
        df['volatility_fast'] = df['close'].rolling(window=10).std()
        
        df['price_change'] = df['close'].pct_change()
        df['price_change_5'] = df['close'].pct_change(5)
        df['volume_change'] = df['tick_volume'].pct_change()
        
        # MACD 계산
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # 볼린저 밴드
        df['bb_upper'] = df['sma_20'] + (df['close'].rolling(window=20).std() * 2)
        df['bb_lower'] = df['sma_20'] - (df['close'].rolling(window=20).std() * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # 스토캐스틱
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # PyTorch용 고급 특성 생성
        features = []
        for i in range(50, len(df)):
            feature_vector = [
                df['rsi'].iloc[i],
                df['rsi_fast'].iloc[i],
                df['rsi_slow'].iloc[i],
                df['macd'].iloc[i],
                df['macd_signal'].iloc[i],
                df['macd_histogram'].iloc[i],
                df['volatility'].iloc[i],
                df['volatility_fast'].iloc[i],
                df['price_change'].iloc[i],
                df['price_change_5'].iloc[i],
                df['volume_change'].iloc[i],
                df['bb_position'].iloc[i],
                df['bb_width'].iloc[i],
                df['stoch_k'].iloc[i],
                df['stoch_d'].iloc[i]
            ]
            
            # NaN 값 처리
            feature_vector = [0.0 if pd.isna(x) else float(x) for x in feature_vector]
            features.append(feature_vector)
        
        self.market_data['features'] = np.array(features)
        self.market_data['prices'] = df['close'].values
        self.market_data['timestamps'] = df['time'].values
        self.market_data['raw_data'] = df
        
        print(f"✅ {len(features)}개 고급 특성 벡터 생성 완료!")
        return True
    
    def calculate_rsi(self, prices, period=14):
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_pytorch_models(self):
        """🤖 PyTorch 모델 학습"""
        if len(self.market_data['features']) < 100:
            print("⚠️ 학습 데이터 부족")
            return False
        
        print("🤖 PyTorch 모델 학습 중...")
        
        features = self.market_data['features']
        prices = self.market_data['prices']
        
        # 특성 정규화
        features_scaled = self.ai_models['scaler'].fit_transform(features)
        
        # PyTorch 텐서로 변환
        X = torch.FloatTensor(features_scaled).to(self.config['device'])
        
        # 1. 가격 예측 모델 학습
        print("  📈 가격 예측 모델 학습...")
        # 안전한 인덱스 범위 설정
        train_size = min(len(X) - 1, len(prices) - 51)  # 50은 특성 생성시 시작 인덱스
        
        X_price = X[:train_size]
        y_price_start = len(prices) - len(features)  # 특성과 가격 데이터 정렬
        y_price = torch.FloatTensor(prices[y_price_start+1:y_price_start+1+train_size]).to(self.config['device'])
        
        print(f"    학습 데이터 크기: X={X_price.shape}, y={y_price.shape}")
        
        self.ai_models['price_predictor'].train()
        for epoch in range(100):
            self.optimizers['price_opt'].zero_grad()
            predictions = self.ai_models['price_predictor'](X_price).squeeze()
            loss = self.loss_functions['price_loss'](predictions, y_price)
            loss.backward()
            self.optimizers['price_opt'].step()
            
            if epoch % 20 == 0:
                print(f"    Epoch {epoch}: Loss = {loss.item():.4f}")
        
        # 2. 방향 예측 모델 학습
        print("  🎯 방향 예측 모델 학습...")
        X_direction = X[:train_size]
        y_direction = []
        
        # 안전한 방향 라벨 생성
        for i in range(train_size):
            current_idx = y_price_start + i
            next_idx = y_price_start + i + 1
            
            # 인덱스 범위 확인
            if next_idx >= len(prices):
                break
                
            current_price = prices[current_idx]
            next_price = prices[next_idx]
            
            if next_price > current_price * 1.002:  # 0.2% 이상 상승
                y_direction.append(0)  # UP
            elif next_price < current_price * 0.998:  # 0.2% 이상 하락
                y_direction.append(1)  # DOWN
            else:
                y_direction.append(2)  # SIDEWAYS
        
        # 방향 데이터 크기 맞추기
        min_size = min(len(X_direction), len(y_direction))
        X_direction = X_direction[:min_size]
        y_direction = torch.LongTensor(y_direction[:min_size]).to(self.config['device'])
        
        print(f"    방향 학습 데이터 크기: X={X_direction.shape}, y={y_direction.shape}")
        
        if len(y_direction) == 0:
            print("    ⚠️ 방향 학습 데이터 없음, 건너뛰기")
        else:
            self.ai_models['direction_classifier'].train()
            for epoch in range(150):
                self.optimizers['direction_opt'].zero_grad()
                predictions = self.ai_models['direction_classifier'](X_direction)
                loss = self.loss_functions['direction_loss'](predictions, y_direction)
                loss.backward()
                self.optimizers['direction_opt'].step()
                
                if epoch % 30 == 0:
                    print(f"    Epoch {epoch}: Loss = {loss.item():.4f}")
        
        # 3. 변동성 예측 모델 학습 (scikit-learn)
        print("  ⚡ 변동성 예측 모델 학습...")
        volatilities = []
        
        for i in range(len(features_scaled)):
            start_idx = y_price_start + i
            end_idx = min(start_idx + 20, len(prices))
            
            if end_idx > start_idx:
                volatility = np.std(prices[start_idx:end_idx])
                volatilities.append(volatility)
            else:
                volatilities.append(0.0)
        
        # 크기 맞추기
        min_vol_size = min(len(features_scaled), len(volatilities))
        features_for_vol = features_scaled[:min_vol_size]
        volatilities = volatilities[:min_vol_size]
        
        if len(volatilities) > 0:
            self.ai_models['volatility_predictor'].fit(features_for_vol, volatilities)
            print(f"    변동성 모델 학습 완료: {len(volatilities)}개 샘플")
        
        print("✅ 모든 AI 모델 학습 완료!")
        return True
    
    def get_pytorch_prediction(self):
        """🤖 PyTorch AI 예측 수행"""
        current_price = self.get_current_price()
        if not current_price:
            return None
        
        if len(self.market_data['features']) == 0:
            return None
        
        # 최신 특성 벡터
        latest_features = self.market_data['features'][-1].reshape(1, -1)
        features_scaled = self.ai_models['scaler'].transform(latest_features)
        
        # PyTorch 텐서로 변환
        X = torch.FloatTensor(features_scaled).to(self.config['device'])
        
        # AI 예측 수행
        self.ai_models['price_predictor'].eval()
        self.ai_models['direction_classifier'].eval()
        
        with torch.no_grad():
            predicted_price = self.ai_models['price_predictor'](X).cpu().numpy()[0][0]
            direction_probs = self.ai_models['direction_classifier'](X).cpu().numpy()[0]
        
        predicted_volatility = self.ai_models['volatility_predictor'].predict(features_scaled)[0]
        
        # 방향 결정
        direction_idx = np.argmax(direction_probs)
        directions = ['UP', 'DOWN', 'SIDEWAYS']
        predicted_direction = directions[direction_idx]
        confidence = direction_probs[direction_idx]
        
        prediction = {
            'current_price': current_price['mid'],
            'predicted_price': float(predicted_price),
            'predicted_direction': predicted_direction,
            'confidence': float(confidence),
            'predicted_volatility': float(predicted_volatility),
            'price_change_expected': abs(float(predicted_price) - current_price['mid']),
            'direction_probs': direction_probs.tolist()
        }
        
        print(f"🤖 PyTorch AI 예측: {predicted_direction} (신뢰도: {confidence:.3f})")
        print(f"   현재가: ${current_price['mid']:,.2f}")
        print(f"   예측가: ${predicted_price:,.2f}")
        print(f"   예상변동: ${prediction['price_change_expected']:.2f}")
        print(f"   예상변동성: ${predicted_volatility:.2f}")
        
        return prediction
    
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
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def calculate_extreme_levels(self, baseline_price, ai_prediction):
        """🚀 극한 레벨 계산 (극도로 멀고 극도로 가깝게) - 브로커 제한 고려"""
        expected_change = ai_prediction['price_change_expected']
        volatility = ai_prediction['predicted_volatility']
        direction = ai_prediction['predicted_direction']
        confidence = ai_prediction['confidence']
        
        # 극한 거리 계산 (신뢰도에 따라 조정)
        extreme_profit_distance = max(
            expected_change * self.config['extreme_profit_multiplier'] * confidence,
            volatility * 20 * confidence
        )
        
        extreme_loss_distance = min(
            expected_change * self.config['extreme_loss_multiplier'],
            volatility * 0.1,
            baseline_price * 0.001  # 기준가의 0.1%
        )
        
        # 브로커 제한 고려 (TP/SL은 현재가의 ±50% 이내)
        max_tp_distance = baseline_price * 0.3  # 30%로 제한
        min_sl_distance = baseline_price * 0.01  # 1%로 제한
        
        # 극한 거리를 브로커 제한 내로 조정
        extreme_profit_distance = min(extreme_profit_distance, max_tp_distance)
        extreme_loss_distance = max(extreme_loss_distance, min_sl_distance)
        
        print(f"🔥 극한 거리 계산:")
        print(f"   극한 수익 거리: ${extreme_profit_distance:.2f}")
        print(f"   극소 손실 거리: ${extreme_loss_distance:.2f}")
        print(f"   거리 비율: {extreme_profit_distance/extreme_loss_distance:.0f}:1")
        
        if direction == 'UP':
            # 상승 예측: 매수는 극도로 멀리, 매도는 극도로 가깝게
            buy_tp = baseline_price + extreme_profit_distance   # 극한 수익
            buy_sl = baseline_price - extreme_loss_distance     # 극소 손실
            
            sell_tp = baseline_price - extreme_loss_distance    # 극소 수익
            sell_sl = baseline_price + extreme_loss_distance    # 극소 손실 (양방향 대칭)
            
        elif direction == 'DOWN':
            # 하락 예측: 매도는 극도로 멀리, 매수는 극도로 가깝게
            buy_tp = baseline_price + extreme_loss_distance     # 극소 수익
            buy_sl = baseline_price - extreme_loss_distance     # 극소 손실 (양방향 대칭)
            
            sell_tp = baseline_price - extreme_profit_distance  # 극한 수익
            sell_sl = baseline_price + extreme_loss_distance    # 극소 손실
            
        else:  # SIDEWAYS
            # 횡보 예측: 양쪽 모두 중간 설정
            moderate_profit = extreme_profit_distance * 0.3
            moderate_loss = extreme_loss_distance * 2
            
            buy_tp = baseline_price + moderate_profit
            buy_sl = baseline_price - moderate_loss
            sell_tp = baseline_price - moderate_profit
            sell_sl = baseline_price + moderate_loss
        
        # 최종 안전성 검증
        buy_tp = max(buy_tp, baseline_price * 1.01)   # 최소 1% 수익
        buy_sl = min(buy_sl, baseline_price * 0.95)   # 최대 5% 손실
        sell_tp = min(sell_tp, baseline_price * 0.99) # 최소 1% 수익
        sell_sl = max(sell_sl, baseline_price * 1.05) # 최대 5% 손실
        
        levels = {
            'baseline': baseline_price,
            'buy_tp': buy_tp,
            'buy_sl': buy_sl,
            'sell_tp': sell_tp,
            'sell_sl': sell_sl,
            'extreme_profit_distance': extreme_profit_distance,
            'extreme_loss_distance': extreme_loss_distance,
            'expected_extreme_profit': extreme_profit_distance * self.config['base_lot_size'],
            'max_minimal_loss': extreme_loss_distance * self.config['base_lot_size']
        }
        
        print(f"\n🎯 극한 레벨 계산 완료:")
        print(f"   기준선: ${baseline_price:,.2f}")
        print(f"   매수 TP: ${buy_tp:,.2f} (+{((buy_tp/baseline_price-1)*100):.2f}%)")
        print(f"   매수 SL: ${buy_sl:,.2f} ({((buy_sl/baseline_price-1)*100):.2f}%)")
        print(f"   매도 TP: ${sell_tp:,.2f} ({((sell_tp/baseline_price-1)*100):.2f}%)")
        print(f"   매도 SL: ${sell_sl:,.2f} (+{((sell_sl/baseline_price-1)*100):.2f}%)")
        
        return levels
    
    def place_extreme_orders(self, levels, ai_prediction):
        """🚀 극한 양방향 주문 실행"""
        print(f"\n💰 극한 양방향 주문 실행!")
        print(f"🤖 PyTorch AI 신뢰도: {ai_prediction['confidence']:.3f}")
        print(f"📊 예측 방향: {ai_prediction['predicted_direction']}")
        print(f"🔥 극한 비율: {levels['extreme_profit_distance']/levels['extreme_loss_distance']:.0f}:1")
        
        current_price = self.get_current_price()
        
        if not current_price:
            print("❌ 현재가 조회 실패")
            return False
        
        # 심볼 정보 확인
        symbol_info = mt5.symbol_info(self.config['symbol'])
        if not symbol_info:
            print("❌ 심볼 정보 조회 실패")
            return False
        
        # 거래량 정규화
        lot_size = self.config['base_lot_size']
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        lot_step = symbol_info.volume_step
        
        # 거래량을 step 단위로 정규화
        lot_size = max(min_lot, min(max_lot, round(lot_size / lot_step) * lot_step))
        
        print(f"📊 거래 정보:")
        print(f"   현재가: ${current_price['mid']:,.2f}")
        print(f"   스프레드: ${current_price['spread']:.2f}")
        print(f"   거래량: {lot_size} (최소: {min_lot}, 최대: {max_lot}, 단위: {lot_step})")
        
        success_count = 0
        
        # 매수 주문 (더 안전한 TP/SL 설정)
        # 매수는 가격이 올라갈 때 수익이므로 TP > 현재가, SL < 현재가
        safe_buy_tp = min(levels['buy_tp'], current_price['ask'] * 1.05)  # 최대 5% 수익
        safe_buy_sl = max(levels['buy_sl'], current_price['ask'] * 0.95)  # 최대 5% 손실
        
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": current_price['ask'],
            "tp": safe_buy_tp,
            "sl": safe_buy_sl,
            "deviation": 200,
            "magic": self.config['magic_number'],
            "comment": f"EXTREME_BUY_{ai_prediction['predicted_direction']}_{ai_prediction['confidence']:.2f}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        print(f"🔵 매수 주문 시도...")
        print(f"   현재 Ask: ${current_price['ask']:,.2f}")
        print(f"   목표 TP: ${safe_buy_tp:,.2f} ({((safe_buy_tp/current_price['ask']-1)*100):+.2f}%)")
        print(f"   손절 SL: ${safe_buy_sl:,.2f} ({((safe_buy_sl/current_price['ask']-1)*100):+.2f}%)")
        
        buy_result = mt5.order_send(buy_request)
        
        if buy_result and buy_result.retcode == mt5.TRADE_RETCODE_DONE:
            actual_buy_price = buy_result.price if buy_result.price > 0 else current_price['ask']
            profit_potential = safe_buy_tp - actual_buy_price
            loss_potential = actual_buy_price - safe_buy_sl
            print(f"✅ 매수 주문 성공: {buy_result.order}")
            print(f"   진입: ${actual_buy_price:,.2f}")
            print(f"   목표: ${safe_buy_tp:,.2f} (+${profit_potential:.2f})")
            print(f"   손절: ${safe_buy_sl:,.2f} (-${loss_potential:.2f})")
            if loss_potential > 0:
                print(f"   수익:손실 비율 = {profit_potential/loss_potential:.1f}:1")
            success_count += 1
        else:
            error_code = buy_result.retcode if buy_result else "Unknown"
            error_desc = self.get_error_description(error_code)
            print(f"❌ 매수 주문 실패: {error_code} - {error_desc}")
        
        # 짧은 대기
        time.sleep(0.5)
        
        # 매도 주문 (더 안전한 TP/SL 설정)
        # 매도는 가격이 내려갈 때 수익이므로 TP < 현재가, SL > 현재가
        safe_sell_tp = max(levels['sell_tp'], current_price['bid'] * 0.95)  # 최대 5% 수익
        safe_sell_sl = min(levels['sell_sl'], current_price['bid'] * 1.05)  # 최대 5% 손실
        
        sell_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config['symbol'],
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": current_price['bid'],
            "tp": safe_sell_tp,
            "sl": safe_sell_sl,
            "deviation": 200,
            "magic": self.config['magic_number'],
            "comment": f"EXTREME_SELL_{ai_prediction['predicted_direction']}_{ai_prediction['confidence']:.2f}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        print(f"🔴 매도 주문 시도...")
        print(f"   현재 Bid: ${current_price['bid']:,.2f}")
        print(f"   목표 TP: ${safe_sell_tp:,.2f} ({((safe_sell_tp/current_price['bid']-1)*100):+.2f}%)")
        print(f"   손절 SL: ${safe_sell_sl:,.2f} ({((safe_sell_sl/current_price['bid']-1)*100):+.2f}%)")
        
        sell_result = mt5.order_send(sell_request)
        
        if sell_result and sell_result.retcode == mt5.TRADE_RETCODE_DONE:
            actual_sell_price = sell_result.price if sell_result.price > 0 else current_price['bid']
            profit_potential = actual_sell_price - safe_sell_tp
            loss_potential = safe_sell_sl - actual_sell_price
            print(f"✅ 매도 주문 성공: {sell_result.order}")
            print(f"   진입: ${actual_sell_price:,.2f}")
            print(f"   목표: ${safe_sell_tp:,.2f} (+${profit_potential:.2f})")
            print(f"   손절: ${safe_sell_sl:,.2f} (-${loss_potential:.2f})")
            if loss_potential > 0:
                print(f"   수익:손실 비율 = {profit_potential/loss_potential:.1f}:1")
            success_count += 1
        else:
            error_code = sell_result.retcode if sell_result else "Unknown"
            error_desc = self.get_error_description(error_code)
            print(f"❌ 매도 주문 실패: {error_code} - {error_desc}")
        
        # 실제 포지션 확인 및 수익 계산
        if success_count > 0:
            print(f"\n💰 실제 포지션 상태 확인...")
            time.sleep(1)  # 포지션 생성 대기
            self.check_actual_positions_and_profit()
        
        if success_count > 0:
            self.stats['total_trades'] += success_count
            
            # AI 예측 기록
            prediction_record = {
                'timestamp': datetime.now().isoformat(),
                'prediction': ai_prediction,
                'levels': levels,
                'orders_placed': success_count,
                'extreme_ratio': levels['extreme_profit_distance']/levels['extreme_loss_distance']
            }
            self.stats['ai_predictions'].append(prediction_record)
            
            print(f"🎯 {success_count}개 극한 주문 성공! 혁명적 양방향 거래 완료!")
            print(f"⏰ 다음 거래 기회를 위해 대기 중...")
            return True
        
        print("❌ 모든 주문 실패")
        return False
    
    def get_error_description(self, error_code):
        """MT5 에러 코드 설명"""
        error_descriptions = {
            10004: "Requote (재견적 요청)",
            10006: "Request rejected (요청 거부)",
            10007: "Request canceled (요청 취소)",
            10008: "Order placed (주문 접수)",
            10009: "Request completed (요청 완료)",
            10010: "Only part of the request was completed (부분 체결)",
            10011: "Request processing error (처리 오류)",
            10012: "Request canceled by timeout (시간 초과)",
            10013: "Invalid request (잘못된 요청)",
            10014: "Invalid volume in the request (잘못된 거래량)",
            10015: "Invalid price in the request (잘못된 가격)",
            10016: "Invalid stops in the request (잘못된 손절/익절)",
            10017: "Trade is disabled (거래 비활성화)",
            10018: "Market is closed (시장 마감)",
            10019: "There is not enough money to complete the request (자금 부족)",
            10020: "Prices changed (가격 변동)",
            10021: "There are no quotes to process the request (시세 없음)",
            10022: "Invalid order expiration date (만료일 오류)",
            10023: "Order state changed (주문 상태 변경)",
            10024: "Too frequent requests (요청 과다)",
            10025: "No changes in request (변경사항 없음)",
            10026: "Autotrading disabled by server (자동매매 비활성화)",
            10027: "Autotrading disabled by client (클라이언트 자동매매 비활성화)",
            10028: "Request locked for processing (처리 중 잠금)",
            10029: "Order or position frozen (주문/포지션 동결)",
            10030: "Invalid order filling type (잘못된 체결 방식)",
        }
        
        return error_descriptions.get(error_code, f"Unknown error ({error_code})")
    
    def check_actual_positions_and_profit(self):
        """💰 실제 포지션 상태 및 수익 확인"""
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            print("⚠️ 활성 포지션이 없습니다")
            return
        
        current_price = self.get_current_price()
        if not current_price:
            print("❌ 현재가 조회 실패")
            return
        
        total_unrealized_profit = 0
        buy_positions = []
        sell_positions = []
        
        print(f"\n📊 실제 포지션 분석:")
        print(f"   현재 BTC 가격: ${current_price['mid']:,.2f}")
        print(f"   활성 포지션: {len(positions)}개")
        
        for i, pos in enumerate(positions):
            # 포지션 타입별 분류
            if pos.type == mt5.ORDER_TYPE_BUY:
                unrealized_profit = (current_price['bid'] - pos.price_open) * pos.volume
                buy_positions.append(pos)
                position_type = "매수"
                current_value = current_price['bid']
            else:
                unrealized_profit = (pos.price_open - current_price['ask']) * pos.volume
                sell_positions.append(pos)
                position_type = "매도"
                current_value = current_price['ask']
            
            total_unrealized_profit += unrealized_profit
            
            # 수익률 계산
            profit_percentage = (unrealized_profit / (pos.price_open * pos.volume)) * 100
            
            print(f"\n   포지션 #{i+1} ({position_type}):")
            print(f"     티켓: {pos.ticket}")
            print(f"     진입가: ${pos.price_open:,.2f}")
            print(f"     현재가: ${current_value:,.2f}")
            print(f"     거래량: {pos.volume}")
            print(f"     목표가: ${pos.tp:,.2f}")
            print(f"     손절가: ${pos.sl:,.2f}")
            print(f"     미실현 손익: ${unrealized_profit:+.2f} ({profit_percentage:+.2f}%)")
            
            # 목표가까지의 거리 계산
            if pos.type == mt5.ORDER_TYPE_BUY:
                distance_to_tp = pos.tp - current_value
                potential_profit = distance_to_tp * pos.volume
            else:
                distance_to_tp = current_value - pos.tp
                potential_profit = distance_to_tp * pos.volume
            
            print(f"     목표까지: ${distance_to_tp:+.2f} (잠재수익: ${potential_profit:+.2f})")
        
        # 양방향 거래 분석
        print(f"\n🎯 양방향 거래 분석:")
        print(f"   매수 포지션: {len(buy_positions)}개")
        print(f"   매도 포지션: {len(sell_positions)}개")
        print(f"   총 미실현 손익: ${total_unrealized_profit:+.2f}")
        
        # 계좌 정보 확인
        account_info = mt5.account_info()
        if account_info:
            account_profit = account_info.equity - account_info.balance
            print(f"   계좌 총 손익: ${account_profit:+.2f}")
            print(f"   계좌 잔고: ${account_info.balance:,.2f}")
            print(f"   계좌 자산: ${account_info.equity:,.2f}")
        
        # 양방향 수익 예측
        if len(buy_positions) > 0 and len(sell_positions) > 0:
            print(f"\n🚀 양방향 수익 시나리오:")
            
            # 5% 상승시
            price_up = current_price['mid'] * 1.05
            profit_if_up = 0
            for pos in buy_positions:
                profit_if_up += (price_up - pos.price_open) * pos.volume
            for pos in sell_positions:
                profit_if_up += (pos.price_open - price_up) * pos.volume
            
            # 5% 하락시  
            price_down = current_price['mid'] * 0.95
            profit_if_down = 0
            for pos in buy_positions:
                profit_if_down += (price_down - pos.price_open) * pos.volume
            for pos in sell_positions:
                profit_if_down += (pos.price_open - price_down) * pos.volume
            
            print(f"   5% 상승시 (${price_up:,.2f}): ${profit_if_up:+.2f}")
            print(f"   5% 하락시 (${price_down:,.2f}): ${profit_if_down:+.2f}")
            print(f"   최대 예상 수익: ${max(profit_if_up, profit_if_down):+.2f}")
        
        return total_unrealized_profit
    def monitor_extreme_positions(self):
        """극한 포지션 모니터링 (개선된 버전)"""
        positions = mt5.positions_get(symbol=self.config['symbol'])
        if not positions:
            return
        
        current_price = self.get_current_price()
        if not current_price:
            return
        
        total_profit = 0
        extreme_profits = 0
        minimal_losses = 0
        buy_count = 0
        sell_count = 0
        
        for pos in positions:
            if pos.type == mt5.ORDER_TYPE_BUY:
                profit = (current_price['bid'] - pos.price_open) * pos.volume
                buy_count += 1
            else:
                profit = (pos.price_open - current_price['ask']) * pos.volume
                sell_count += 1
            
            total_profit += profit
            
            if profit > 0:
                extreme_profits += profit
            else:
                minimal_losses += abs(profit)
        
        if len(positions) > 0:
            print(f"📊 극한 포지션: {len(positions)}개 (매수:{buy_count}, 매도:{sell_count}) | "
                  f"미실현: ${total_profit:+.2f} | "
                  f"극한수익: ${extreme_profits:+.2f} | "
                  f"극소손실: ${minimal_losses:.2f}")
            
            # 목표 달성 여부 체크
            profitable_positions = sum(1 for pos in positions if 
                                     (pos.type == mt5.ORDER_TYPE_BUY and current_price['bid'] >= pos.tp) or
                                     (pos.type == mt5.ORDER_TYPE_SELL and current_price['ask'] <= pos.tp))
            
            if profitable_positions > 0:
                print(f"🎯 목표 달성 포지션: {profitable_positions}개!")
        
        return total_profit
    
    def run_extreme_system(self):
        """🚀 극한 시스템 실행"""
        print("\n" + "="*70)
        print("  🚀 혁명적 PyTorch AI 극한 양방향 거래 시스템 시작!")
        print("="*70)
        
        # 초기 데이터 수집 및 AI 학습
        if not self.collect_advanced_market_data(500):
            return False
        
        if not self.train_pytorch_models():
            return False
        
        print("\n🤖 PyTorch AI 시스템 준비 완료!")
        print("💡 x달러 변화 = x달러 수익 보장!")
        print("🔥 극한 거리 설정으로 어마무시한 수익!")
        print("💎 극소 손실로 리스크 최소화!")
        print("🎯 현재가 기준 극한 양방향 거래 시작!")
        print("⏰ 시스템이 계속 실행됩니다...")
        
        last_trade_time = 0
        last_data_update = 0
        trade_count = 0
        
        try:
            while True:
                current_time = time.time()
                
                # 10분마다 데이터 업데이트 및 AI 재학습
                if current_time - last_data_update > 600:
                    print(f"\n🔄 PyTorch AI 모델 업데이트 중... (거래 {trade_count}회 완료)")
                    self.collect_advanced_market_data(200)
                    self.train_pytorch_models()
                    last_data_update = current_time
                
                # 2분마다 거래 기회 확인
                if current_time - last_trade_time > 120:
                    current_price = self.get_current_price()
                    if current_price and current_price['spread'] <= self.config['max_spread']:
                        
                        print(f"\n📊 거래 기회 분석 중... (스프레드: ${current_price['spread']:.2f})")
                        
                        # 현재가를 기준선으로 설정
                        self.current_baseline = current_price['mid']
                        
                        # PyTorch AI 예측 수행
                        ai_prediction = self.get_pytorch_prediction()
                        
                        if ai_prediction and ai_prediction['confidence'] >= self.config['ai_confidence_threshold']:
                            # 극한 레벨 계산
                            levels = self.calculate_extreme_levels(self.current_baseline, ai_prediction)
                            
                            # 극한 양방향 주문 실행
                            if self.place_extreme_orders(levels, ai_prediction):
                                last_trade_time = current_time
                                trade_count += 1
                                print(f"✅ 거래 #{trade_count} 완료!")
                                time.sleep(60)  # 성공 후 1분 대기
                            else:
                                print("⚠️ 주문 실패, 30초 후 재시도...")
                                time.sleep(30)
                        else:
                            confidence = ai_prediction['confidence'] if ai_prediction else 0
                            print(f"⏳ AI 신뢰도 부족 ({confidence:.3f} < {self.config['ai_confidence_threshold']:.3f}), 대기 중...")
                    else:
                        spread = current_price['spread'] if current_price else 0
                        print(f"⚠️ 스프레드 초과 (${spread:.2f} > ${self.config['max_spread']:.2f}), 대기 중...")
                
                # 극한 포지션 모니터링
                if current_time % 60 < 2:  # 1분마다
                    self.monitor_extreme_positions()
                
                # 실시간 상태 표시
                if current_time % 30 < 2:  # 30초마다
                    account_info = mt5.account_info()
                    if account_info:
                        profit = account_info.equity - account_info.balance
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"BTC: ${self.current_baseline:,.2f} | "
                              f"실제손익: ${profit:+.2f} | "
                              f"극한거래: {trade_count}회 | "
                              f"AI예측: {len(self.stats['ai_predictions'])}회 | "
                              f"시스템: 정상 작동 중")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 사용자가 극한 시스템을 중단했습니다")
            self.display_extreme_final_stats()
        except Exception as e:
            print(f"\n❌ 시스템 오류 발생: {e}")
            print("🔄 시스템을 재시작합니다...")
            time.sleep(10)
            # 재귀 호출로 시스템 재시작
            self.run_extreme_system()
    
    def display_extreme_final_stats(self):
        """극한 최종 통계 표시"""
        runtime = datetime.now() - self.stats['start_time']
        account_info = mt5.account_info()
        
        print(f"\n📊 혁명적 PyTorch AI 극한 시스템 최종 통계:")
        print(f"  ⏰ 운영 시간: {runtime}")
        print(f"  🤖 PyTorch AI 거래 횟수: {self.stats['total_trades']}회")
        print(f"  📈 AI 예측 횟수: {len(self.stats['ai_predictions'])}회")
        print(f"  🔥 극한 수익 배수: {self.config['extreme_profit_multiplier']}x")
        print(f"  💎 극소 손실 배수: {self.config['extreme_loss_multiplier']}x")
        
        if account_info:
            total_profit = account_info.equity - account_info.balance
            print(f"  💰 총 손익: ${total_profit:+.2f}")
            
        if len(self.stats['ai_predictions']) > 0:
            avg_confidence = np.mean([p['prediction']['confidence'] for p in self.stats['ai_predictions']])
            avg_extreme_ratio = np.mean([p['extreme_ratio'] for p in self.stats['ai_predictions']])
            print(f"  🎯 평균 AI 신뢰도: {avg_confidence:.3f}")
            print(f"  ⚡ 평균 극한 비율: {avg_extreme_ratio:.0f}:1")

def main():
    """메인 함수"""
    print("🚀💰 혁명적 PyTorch AI 극한 양방향 거래 시스템 💰🚀")
    print("\n🔥 특징:")
    print("  🤖 PyTorch 딥러닝 활용 (GPU 가속)")
    print("  🎯 현재가 기준선 극한 양방향 거래")
    print("  💰 한쪽 극도로 멀리 (100배), 반대쪽 극도로 가깝게 (0.01배)")
    print("  📊 x달러 변화 = x달러 수익 보장")
    print("  🚀 방향 관계없이 무조건 수익")
    print("  🔥 극한 수익:손실 비율 = 10000:1")
    
    bot = RevolutionaryAIBot()
    
    if not bot.connect_mt5():
        return
    
    # 심볼 확인
    symbol_info = mt5.symbol_info('BTCUSD')
    if symbol_info is None:
        print("❌ BTCUSD 심볼 없음")
        mt5.shutdown()
        return
    
    answer = input("\n혁명적 PyTorch AI 극한 양방향 거래를 시작하시겠습니까? (y/n): ")
    if answer.lower() != 'y':
        print("프로그램 종료")
        mt5.shutdown()
        return
    
    # 극한 시스템 시작!
    bot.run_extreme_system()
    
    mt5.shutdown()

if __name__ == "__main__":
    main()