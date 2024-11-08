import matplotlib.pyplot as plt

# Data for the number of alerts, as given in your previous question
alerts = [20, 10, 20, 20, 10, 20, 10, 7, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 20, 10, 7, 5, 4, 
          4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 20]

# Configuration for each alert
configurations = {
    0: ('ipid', 8), 1: ('ipid', 16), 2: ('ttl', 8), 3: ('window', 8), 4: ('window', 16), 
    5: ('tcp_options', 8), 6: ('tcp_options', 16), 7: ('tcp_options', 24), 8: ('tcp_options', 32), 
    9: ('tcp_options', 40), 10: ('tcp_options', 48), 11: ('tcp_options', 56), 12: ('tcp_options', 64), 
    13: ('tcp_options', 72), 14: ('tcp_options', 80), 15: ('tcp_options', 88), 16: ('tcp_options', 96), 
    17: ('tcp_options', 104), 18: ('tcp_options', 112), 19: ('tcp_options', 120), 20: ('tcp_options', 128), 
    21: ('tcp_options', 136), 22: ('tcp_options', 144), 23: ('tcp_options', 152), 24: ('tcp_options', 160), 
    25: ('tcp_options', 168), 26: ('tcp_options', 176), 27: ('tcp_options', 184), 28: ('tcp_options', 192), 
    29: ('tcp_options', 200), 30: ('tcp_options', 208), 31: ('tcp_options', 216), 32: ('tcp_options', 224), 
    33: ('tcp_options', 232), 34: ('tcp_options', 240), 35: ('tcp_options', 248), 36: ('tcp_options', 256), 
    37: ('tcp_options', 264), 38: ('tcp_options', 272), 39: ('tcp_options', 280), 40: ('tcp_options', 288), 
    41: ('tcp_options', 296), 42: ('tcp_options', 304), 43: ('tcp_options', 312), 44: ('tcp_options', 320), 
    45: ('ip_options', 8), 46: ('ip_options', 16), 47: ('ip_options', 24), 48: ('ip_options', 32), 
    49: ('ip_options', 40), 50: ('ip_options', 48), 51: ('ip_options', 56), 52: ('ip_options', 64), 
    53: ('ip_options', 72), 54: ('ip_options', 80), 55: ('ip_options', 88), 56: ('ip_options', 96), 
    57: ('ip_options', 104), 58: ('ip_options', 112), 59: ('ip_options', 120), 60: ('ip_options', 128), 
    61: ('ip_options', 136), 62: ('ip_options', 144), 63: ('ip_options', 152), 64: ('ip_options', 160), 
    65: ('ip_options', 168), 66: ('ip_options', 176), 67: ('ip_options', 184), 68: ('ip_options', 192), 
    69: ('ip_options', 200), 70: ('ip_options', 208), 71: ('ip_options', 216), 72: ('ip_options', 224), 
    73: ('ip_options', 232), 74: ('ip_options', 240), 75: ('ip_options', 248), 76: ('ip_options', 256), 
    77: ('ip_options', 264), 78: ('ip_options', 272), 79: ('ip_options', 280), 80: ('ip_options', 288), 
    81: ('ip_options', 296), 82: ('ip_options', 304), 83: ('ip_options', 312), 84: ('ip_options', 320), 
    85: ('user_agent', 8)
}

# Extract headers and bits for the x-axis labels
x_labels = [f"{config[0]} {config[1]} bits" for config in configurations.values()]

# Plotting the data
plt.figure(figsize=(16, 8))
plt.bar(x_labels, alerts, color='skyblue')
plt.xlabel('Header Configuration (Field and Bits)')
plt.ylabel('Number of Alerts')
plt.title('Number of Alerts Based on Header Configuration')
plt.xticks(rotation=90)  # Rotate x-axis labels for readability
plt.tight_layout()
plt.show()