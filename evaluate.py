# evaluate.py
import threading
import time
import random
import string
import encoder
import decoder
import stego_utils

def generate_random_message(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# For reference
headers_info = {
    'ipid': {'max_bits': 16},
    'ttl': {'max_bits': 8},
    'window': {'max_bits': 16},
    'tcp_reserved': {'max_bits': 4},
    'tcp_options': {'max_bits': 320},  # Up to 40 bytes
    'ip_options': {'max_bits': 320},   # Up to 40 bytes
    'user_agent': {'max_bits': 8},     # Modifiable within the constraints
}

def main(msg_len=20, msg_count=2, verbose=False, buffer_time_to_load=5):
    # Define the destination IP and port
    destination_ip = '192.168.1.100'  # Use localhost for testing
    destination_port = 80      # Use a test port

    # Sum must be multiple of 8
    header_bit_fields = [
        ('ipid', 3),            # Up to 16 bits
        ('ttl', 4),             # Up to 8 bits
        ('window', 5),         # Up to 16 bits
        ('tcp_reserved', 3),    # Up to 4 bits
        ('tcp_options', 6),     # Up to 320 bits
        ('ip_options', 6),      # Up to 320 bits
        ('user_agent', 5),      # Up to 8 bits
    ]

    stego_utils.save_to_config(destination_ip, destination_port, header_bit_fields)
    # # Generate random messages to send using method parameters
    # messages = [generate_random_message(msg_len) for _ in range(msg_count)]
    
    # Generate custom message
    messages = ["Hello this is a secret message. I only want to send it once" for _ in range(1)]
    
    for i, message in enumerate(messages):
        print(f"Message {i + 1}: {message}")
    print()
    
    # Start the decoder in a separate thread
    # May need to adjust timeout if verbose is on
    decoder_thread = threading.Thread(target=lambda: decoder.start_decoder(timeout=buffer_time_to_load, verbose=verbose))
    decoder_thread.daemon = True
    decoder_thread.start()

    # Give the decoder some time to start
    time.sleep(1)

    # Run the encoder with the specified settings and messages
    encoder.start_encoder(
        load_config=True,
        use_noise=True,
        messages=messages,
        verbose=verbose
    )

    # Give some time for the messages to be processed
    time.sleep(buffer_time_to_load)

    print("\nEvaluation completed.")

if __name__ == '__main__':
    main(msg_len=8, msg_count=1,verbose=True,buffer_time_to_load=5)