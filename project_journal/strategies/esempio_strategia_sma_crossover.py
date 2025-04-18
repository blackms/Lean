# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from AlgorithmImports import *

class SMA_CrossOver(QCAlgorithm):
    '''Strategia di esempio che utilizza il crossover di due medie mobili semplici (SMA)'''

    def initialize(self):
        '''Inizializza i parametri dell'algoritmo, inclusi data range, cash, e asset'''
        
        # Imposta le date di inizio e fine del backtest
        self.set_start_date(2018, 1, 1)
        self.set_end_date(2020, 1, 1)
        
        # Imposta il capitale iniziale
        self.set_cash(100000)
        
        # Aggiungi il titolo da monitorare (SPY - S&P 500 ETF)
        self.symbol = self.add_equity("SPY", Resolution.DAILY)
        
        # Inizializza le medie mobili semplici
        self.sma_fast = self.SMA(self.symbol, 50)  # Media mobile a 50 giorni
        self.sma_slow = self.SMA(self.symbol, 200) # Media mobile a 200 giorni
        
        # Imposta il warm-up per gli indicatori
        self.set_warm_up(200)
        
        # Imposta il nome della strategia per i log
        self.debug(f"SMA CrossOver Strategy inizializzata - {self.symbol}")
        
        # Traccia gli indicatori
        self.plot_indicator("Indicatori", self.sma_fast, "SMA Fast")
        self.plot_indicator("Indicatori", self.sma_slow, "SMA Slow")

    def on_data(self, data):
        '''Elabora i dati in arrivo e prende decisioni di trading'''
        
        # Verifica se gli indicatori sono pronti
        if not self.sma_fast.is_ready or not self.sma_slow.is_ready:
            return
        
        # Ottieni i valori correnti delle medie mobili
        fast_value = self.sma_fast.current.value
        slow_value = self.sma_slow.current.value
        
        # Logica di trading
        if not self.portfolio.invested:
            # Se non siamo investiti e la media veloce supera quella lenta, compriamo
            if fast_value > slow_value:
                self.set_holdings(self.symbol, 1)  # Investi il 100% del portafoglio
                self.debug(f"SEGNALE DI ACQUISTO: SMA Fast ({fast_value:.2f}) sopra SMA Slow ({slow_value:.2f})")
        else:
            # Se siamo investiti e la media veloce scende sotto quella lenta, vendiamo
            if fast_value < slow_value:
                self.liquidate(self.symbol)
                self.debug(f"SEGNALE DI VENDITA: SMA Fast ({fast_value:.2f}) sotto SMA Slow ({slow_value:.2f})")