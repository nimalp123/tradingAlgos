import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Assuming your CSV file is named 'qqq_stock_data.csv'
df = pd.read_csv('/Users/nimalperiasamy/AlgoTrade/QQQ Stock data since inception.csv')

# For this example, since we don't have the CSV file, let's create a DataFrame
# with the data you provided as an example.



# df = pd.DataFrame(data)

# Calculate percent change in price for each day
df['Percent Change'] = ((df['Close'] - df['Open']) / df['Open']) *100

# Convert the percent changes to a list
percent_changes = df['Percent Change'].tolist()

# Calculate the average percent change
average_percent_change = sum(percent_changes) / len(percent_changes)

# Calculate the median percent change
median_percent_change = np.median(percent_changes)

# Calculate the mode of percent changes
mode_values, mode_counts = np.unique(percent_changes, return_counts=True)

# Sort the modes by their frequency in descending order
sorted_indices = np.argsort(-mode_counts)  # Negative for descending order
top_5_modes = mode_values[sorted_indices][:5]
top_5_frequencies = mode_counts[sorted_indices][:5]

# Remove outliers to calculate a second average
Q1 = np.percentile(percent_changes, 25)
Q3 = np.percentile(percent_changes, 75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter out outliers
filtered_percent_changes = [x for x in percent_changes if lower_bound <= x <= upper_bound]

# Calculate the average percent change with outliers removed
average_percent_change_no_outliers = sum(filtered_percent_changes) / len(filtered_percent_changes)

# Calculate the median percent change
median_percent_change_no_outliers = np.median(filtered_percent_changes)

# Calculate the standard deviation of the percent changes with outliers removed
std_dev_no_outliers = np.std(filtered_percent_changes, ddof=1)

# Output the results
print("List of daily percent changes:")
print(percent_changes)

print("\nAverage percent change:")
print(average_percent_change)

print("\nMedian percent change:")
print(median_percent_change)


print("\nTop 5 modes and their frequencies:")
for i in range(len(top_5_modes)):
    print(f"Mode: {top_5_modes[i]}, Frequency: {top_5_frequencies[i]}")

print("\nAverage percent change with outliers removed:")
print(average_percent_change_no_outliers)

print("\nStandard deviation (using mean with outliers removed):")
print(std_dev_no_outliers)

print("\nMedian percent change    with outliers removed:")
print(median_percent_change_no_outliers)

# # Determine the range of the data
# min_change = min(percent_changes)
# max_change = max(percent_changes)

# # Create bins with intervals of 0.0001
# bins = np.arange(min_change, max_change + 0.0001, 0.0001)

# # Plot the histogram
# plt.figure(figsize=(10, 6))
# plt.hist(percent_changes, bins=bins, edgecolor='black')
# plt.title('Distribution of Daily Percent Changes')
# plt.xlabel('Percent Change (%)')
# plt.ylabel('Frequency')
# plt.grid(True)
# plt.show()

# plt.figure(figsize=(10, 6))
# plt.hist(percent_changes, bins=10, edgecolor='black')
# plt.title('Distribution of Daily Percent Changes')
# plt.xlabel('Percent Change (%)')
# plt.ylabel('Frequency')
# plt.grid(True)
# plt.show()



# # Plotting the data
# plt.figure(figsize=(10, 6))
# plt.plot(df['Date'], df['Percent Change'], marker='o', linestyle='-', color='b')

# # Adding titles and labels
# plt.title('Daily Percent Change in Stock Prices')
# plt.xlabel('Date')
# plt.ylabel('Percent Change (%)')
# plt.xticks(rotation=45)
# plt.grid(True)

# # Show the plot
# plt.tight_layout()
# plt.show()