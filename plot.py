import matplotlib.pyplot as plt

# List of alert counts per message size
alerts = [
    1, 2, 4, 5, 6, 6, 7, 9, 10, 11, 17, 13, 14, 15, 17, 21, 19, 22, 23, 28, 
    26, 29, 27, 27, 29, 31, 31, 32, 34, 35, 35, 39, 40, 41, 42, 42, 42, 45, 
    48, 43, 48, 45, 48, 48, 49, 54, 53, 57, 54, 57, 58, 60, 64, 63, 62, 63, 
    70, 69, 71, 72, 73, 78, 69, 72, 72, 75, 80, 75, 76, 81, 83, 84, 81, 81, 
    86, 91, 87, 84, 91, 94, 99, 98, 96, 97, 97, 93, 102, 96, 111, 101, 108, 
    107, 110, 112, 114, 115, 109, 112, 109
]

# Generating message sizes (1 to 99)
message_sizes = list(range(1, 100))

# Plotting the data
plt.figure(figsize=(10, 6))
plt.plot(message_sizes, alerts, marker='o', linestyle='-')
plt.xlabel('Message Size')
plt.ylabel('Number of Alerts')
plt.title('Number of Alerts by Message Size')
plt.grid(True)
plt.show()