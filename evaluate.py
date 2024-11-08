# evaluate.py
import threading
import time
import random
import string
import encoder
import decoder

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

def main():
    # Define the destination IP and port
    destination_ip = '192.168.1.100'  # Use localhost for testing
    destination_port = 80      # Use a test port

    # Define headers and bits to use (4 bits from each header)
    headers_to_use = ['ipid', 'ttl', 'window', 'tcp_options', 'ip_options', 'user_agent']
    header_bit_fields = [(header, 8) for header in headers_to_use]

    # Start the decoder in a separate thread
    decoder_thread = threading.Thread(target=decoder.start_decoder)
    decoder_thread.daemon = True
    decoder_thread.start()

    # Give the decoder some time to start
    time.sleep(2)

    # Generate random messages to send
    messages = [generate_random_message(10) for _ in range(5)]

    # Run the encoder with the specified settings and messages
    encoder.start_encoder(
        destination_ip=destination_ip,
        destination_port=destination_port,
        selected_headers=header_bit_fields,
        use_noise=False,
        messages=messages
    )

    # Give some time for the messages to be processed
    time.sleep(5)

    print("\nEvaluation completed.")

if __name__ == '__main__':
    main()