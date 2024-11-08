import json
from datetime import datetime, timedelta

# Initialize variables
clusters = []
cluster_count = 0
prev_timestamp = None
TIME_APART_THRESHOLD = 2

# Open and read the JSON file
with open('logs.json', 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        
        # Parse the JSON object from the line
        entry = json.loads(line)
        
        # Extract and parse the timestamp
        timestamp_str = entry['timestamp']
        # The format is "MM/DD-HH:MM:SS.microsecond", we assume the current year
        timestamp = datetime.strptime(timestamp_str, "%m/%d-%H:%M:%S.%f")
        timestamp = timestamp.replace(year=datetime.now().year)
        
        if prev_timestamp is None:
            # First entry, start a new cluster
            cluster_count = 1
        else:
            # Calculate the time difference from the previous timestamp
            time_diff = timestamp - prev_timestamp
            if time_diff.total_seconds() < TIME_APART_THRESHOLD:
                # Within 2 seconds, continue the current cluster
                cluster_count += 1
            else:
                # More than 2 seconds apart, save the current cluster count and start a new cluster
                clusters.append(cluster_count)
                cluster_count = 1
        
        # Update the previous timestamp
        prev_timestamp = timestamp

# After processing all entries, append the last cluster count
clusters.append(cluster_count)

# Output the array of cluster counts
print(clusters)