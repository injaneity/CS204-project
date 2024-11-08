import json
from datetime import datetime, timedelta

# Initialize variables
clusters = []
cluster_count = 0
prev_timestamp = None
TIME_APART_THRESHOLD = 2
ZERO_ENTRY_THRESHOLD = 6
MAX_THRESHOLD = 11

# Open and read the text file
with open('alert_json2.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        
        # Parse the JSON object from the line
        entry = json.loads(line)
        
        # Extract and parse the timestamp
        timestamp_str = entry['timestamp']
        # The format is "MM/DD-HH:MM:SS.microsecond", assuming the current year
        timestamp = datetime.strptime(timestamp_str, "%m/%d-%H:%M:%S.%f")
        timestamp = timestamp.replace(year=datetime.now().year)
        
        if prev_timestamp is None:
            # First entry, start a new cluster
            cluster_count = 1
        else:
            # Calculate the time difference from the previous timestamp
            time_diff = timestamp - prev_timestamp
            seconds_diff = time_diff.total_seconds()
            
            if seconds_diff < TIME_APART_THRESHOLD:
                # Within 2 seconds, continue the current cluster
                cluster_count += 1
            else:
                # Add the current cluster count to the clusters list
                clusters.append(cluster_count)
                
                # Insert `0` entries based on the time difference
                if ZERO_ENTRY_THRESHOLD <= seconds_diff < MAX_THRESHOLD:
                    clusters.append(0)  # One `0` entry if time_diff is between 6 and 11 seconds
                elif seconds_diff >= MAX_THRESHOLD:
                    # Calculate the number of `0` entries based on the time difference
                    zero_entries = int((seconds_diff - TIME_APART_THRESHOLD) // TIME_APART_THRESHOLD)
                    clusters.extend([0] * zero_entries)
                
                # Start a new cluster
                cluster_count = 1
        
        # Update the previous timestamp
        prev_timestamp = timestamp

# After processing all entries, append the last cluster count
clusters.append(cluster_count)

# Output the array of cluster counts
print(clusters)

# Print size of clusters
print(len(clusters))