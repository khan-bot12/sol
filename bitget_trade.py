//@version=6
strategy("EMA Scalping with Only Trailing Stop", overlay=true, default_qty_type=strategy.cash, default_qty_value=2500)

// === Inputs ===
trailPerc = input.float(1.2, title="Trailing Stop %", minval=0.1)

// === Indicators ===
emaFast = ta.ema(close, 7)
emaSlow = ta.ema(close, 21)
emaSlope = emaFast - emaFast[1]

macdLine = ta.ema(close, 12) - ta.ema(close, 26)
macdSignal = ta.ema(macdLine, 9)
macdHist = macdLine - macdSignal
macdHistSlope = macdHist - macdHist[1]

rsi = ta.rsi(close, 14)

// === Entry Conditions ===
longCondition = ta.crossover(emaFast, emaSlow) and macdHist > 0 and macdHistSlope > 0 and rsi > 55 and close > emaFast and close > emaSlow
shortCondition = ta.crossunder(emaFast, emaSlow) and macdHist < 0 and macdHistSlope < 0 and rsi < 45 and close < emaFast and close < emaSlow

// === Trailing Stop Logic Only ===
var float longTrailStop = na
var float shortTrailStop = na

if (strategy.position_size > 0)
    longTrailStop := na(longTrailStop) ? close * (1 - trailPerc/100) : math.max(longTrailStop, high * (1 - trailPerc/100))
    strategy.exit("Exit Long", from_entry="Long", stop=longTrailStop)
else
    longTrailStop := na

if (strategy.position_size < 0)
    shortTrailStop := na(shortTrailStop) ? close * (1 + trailPerc/100) : math.min(shortTrailStop, low * (1 + trailPerc/100))
    strategy.exit("Exit Short", from_entry="Short", stop=shortTrailStop)
else
    shortTrailStop := na

// === Execute Trades ===
if (longCondition)
    strategy.entry("Long", strategy.long)

if (shortCondition)
    strategy.entry("Short", strategy.short)

// === Plotting ===
plot(emaFast, color=color.orange, title="EMA 7")
plot(emaSlow, color=color.blue, title="EMA 21")
