import numpy as np
import matplotlib.pyplot as plt

# Constants
daily_percent_change = 0.0003984849776223669
leverage_factor = 2
trading_days_per_year = 252
sp500_annual_growth = 1.08  # 8% annual return for S&P 500

# Formula for calculating leveraged growth
def leveraged_growth(years, daily_percent_change, leverage_factor):
    return (1 + daily_percent_change * leverage_factor) ** (trading_days_per_year * years)

# Formula for calculating S&P 500 growth
def sp500_growth(years):
    return (1.08) ** years

# Years to consider for the plot
years = np.linspace(0, 10, 100)  # Considering growth over 10 years

# Calculate the growth for each year for both leveraged and S&P 500
leveraged_growth_values = leveraged_growth(years, daily_percent_change, leverage_factor)
sp500_growth_values = sp500_growth(years)

# Convert growth factors to percentages
leveraged_growth_percent = (leveraged_growth_values - 1) * 100
sp500_growth_percent = (sp500_growth_values - 1) * 100

# Plotting the comparison
plt.figure(figsize=(10, 6))

# Plot the 2x leveraged index growth as a percentage
plt.plot(years, leveraged_growth_percent, label='2x Leveraged Index', color='b')

# Plot the S&P 500 growth as a percentage
plt.plot(years, sp500_growth_percent, label='S&P 500', color='r', linestyle='--')

# Add titles and labels
plt.title('Growth Comparison: 2x Leveraged Index 100 vs S&P 500 (Percent Growth)')
plt.xlabel('Years')
plt.ylabel('Percent Growth (%)')
plt.grid(True)

# Add a legend
plt.legend()

# Display the plot
plt.tight_layout()
plt.show()
