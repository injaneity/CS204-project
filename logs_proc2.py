import json
from datetime import datetime, timedelta

# Initialize variables
clusters = []
cluster_count = 0
prev_timestamp = None
TIME_APART_THRESHOLD = 1  # Entries within 1 second are in the same cluster
SEPARATE_CLUSTER_THRESHOLD = 5  # Separate clusters should be at least 5 seconds apart

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
            
            if seconds_diff <= TIME_APART_THRESHOLD:
                # Within 1 second, continue the current cluster
                cluster_count += 1
            else:
                # Add the current cluster count to the clusters list
                clusters.append(cluster_count)
                
                # Only add zero entries if the difference is 5 seconds or more
                if seconds_diff >= SEPARATE_CLUSTER_THRESHOLD:
                    # Calculate the number of `0` entries needed (one for every 5-second interval)
                    zero_entries = int((seconds_diff - 1) // SEPARATE_CLUSTER_THRESHOLD)
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