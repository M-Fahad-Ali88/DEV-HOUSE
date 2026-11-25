import numpy as np

prices = np.array([
    100, 102, 101, 105, 107,
    104, 108, 110, 109, 113,
    115, 112, 116, 120, 118
], dtype=np.float64)

print("STOCK PRICES")
print(prices)

log_returns = np.log(prices[1:] / prices[:-1])

print("\nLOGARITHMIC RETURNS")
print(log_returns)

window_size = 3

windows = np.lib.stride_tricks.sliding_window_view(
    log_returns, window_size
)

window_means = np.mean(windows, axis=1)

deviations = windows - window_means[:, np.newaxis]

squared_deviations = deviations ** 2

variance = np.sum(squared_deviations, axis=1) / (window_size - 1)

rolling_volatility = np.sqrt(variance)

print("\nROLLING WINDOWS")
print(windows)

print("\nWINDOW MEANS")
print(window_means)

print("\nROLLING VOLATILITY")
print(rolling_volatility)
