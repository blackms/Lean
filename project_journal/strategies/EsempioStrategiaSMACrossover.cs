/*
 * QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
 * Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

using System;
using System.Collections.Generic;
using QuantConnect.Data;
using QuantConnect.Indicators;

namespace QuantConnect.Algorithm.CSharp
{
    /// <summary>
    /// Strategia di esempio che utilizza il crossover di due medie mobili semplici (SMA)
    /// </summary>
    public class SMACrossover : QCAlgorithm
    {
        private Symbol _symbol;
        private SimpleMovingAverage _smaFast;
        private SimpleMovingAverage _smaSlow;
        
        /// <summary>
        /// Inizializza i parametri dell'algoritmo, inclusi data range, cash, e asset
        /// </summary>
        public override void Initialize()
        {
            // Imposta le date di inizio e fine del backtest
            SetStartDate(2018, 1, 1);
            SetEndDate(2020, 1, 1);
            
            // Imposta il capitale iniziale
            SetCash(100000);
            
            // Aggiungi il titolo da monitorare (SPY - S&P 500 ETF)
            _symbol = AddEquity("SPY", Resolution.Daily).Symbol;
            
            // Inizializza le medie mobili semplici
            _smaFast = SMA(_symbol, 50);  // Media mobile a 50 giorni
            _smaSlow = SMA(_symbol, 200); // Media mobile a 200 giorni
            
            // Imposta il warm-up per gli indicatori
            SetWarmUp(200);
            
            // Imposta il nome della strategia per i log
            Debug($"SMA CrossOver Strategy inizializzata - {_symbol}");
            
            // Traccia gli indicatori
            PlotIndicator("Indicatori", _smaFast, "SMA Fast");
            PlotIndicator("Indicatori", _smaSlow, "SMA Slow");
        }
        
        /// <summary>
        /// Elabora i dati in arrivo e prende decisioni di trading
        /// </summary>
        /// <param name="data">Slice object contenente i dati di mercato</param>
        public override void OnData(Slice data)
        {
            // Verifica se gli indicatori sono pronti
            if (!_smaFast.IsReady || !_smaSlow.IsReady)
                return;
            
            // Ottieni i valori correnti delle medie mobili
            var fastValue = _smaFast.Current.Value;
            var slowValue = _smaSlow.Current.Value;
            
            // Logica di trading
            if (!Portfolio.Invested)
            {
                // Se non siamo investiti e la media veloce supera quella lenta, compriamo
                if (fastValue > slowValue)
                {
                    SetHoldings(_symbol, 1);  // Investi il 100% del portafoglio
                    Debug($"SEGNALE DI ACQUISTO: SMA Fast ({fastValue:F2}) sopra SMA Slow ({slowValue:F2})");
                }
            }
            else
            {
                // Se siamo investiti e la media veloce scende sotto quella lenta, vendiamo
                if (fastValue < slowValue)
                {
                    Liquidate(_symbol);
                    Debug($"SEGNALE DI VENDITA: SMA Fast ({fastValue:F2}) sotto SMA Slow ({slowValue:F2})");
                }
            }
        }
    }
}