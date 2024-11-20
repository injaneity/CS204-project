#!/bin/bash

# Sample Commands for Testing Encoder with Different Parameters

# 1. Basic Test with Simple Message
echo "Testing basic encoding with 'hello'"
python3 encoder.py 192.168.1.100 80 "hello"

# 2. Longer Message Test
echo "Testing with a longer message"
python3 encoder.py 192.168.1.100 80 "this is a longer test message"

# 3. Test with Special Characters
echo "Testing with special characters"
python3 encoder.py 192.168.1.100 80 "hello! this message has symbols: @$#*&"

# 4. Custom Encoding Fields (IPID and TTL only)
echo "Testing with custom encoding fields (IPID and TTL only)"
python3 encoder.py 192.168.1.100 80 "custom fields test" --encoding_fields ipid ttl

# 5. Test with Random Padding Noise
echo "Testing with random padding noise"
python3 encoder.py 192.168.1.100 80 "noise test" --add_noise --noise_type random_padding --noise_level 5

# 6. Test with Delay Noise
echo "Testing with delay noise"
python3 encoder.py 192.168.1.100 80 "delay noise test" --add_noise --noise_type delay --noise_level 3

# 7. Test with All Encoding Fields and Maximum Noise
echo "Testing with all encoding fields and maximum noise"
python3 encoder.py 192.168.1.100 80 "full encoding and noise test" --encoding_fields ipid ttl window user_agent --add_noise --noise_type random_padding --noise_level 10

# 8. Edge Case Test with Minimal Message
echo "Testing with a single character message"
python3 encoder.py 192.168.1.100 80 "A"

# 9. Different Encoding Field Combination (TTL and Window only)
echo "Testing with TTL and Window encoding fields only"
python3 encoder.py 192.168.1.100 80 "partial fields test" --encoding_fields ttl window

# 10. Stress Test with Repeated Short Message and High Noise
echo "Stress testing with repeated short message and high noise"
python3 encoder.py 192.168.1.100 80 "repeat" --add_noise --noise_type random_padding --noise_level 7

# End of sample commands
echo "All tests complete."
