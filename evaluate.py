# evaluate.py
import threading
import time
import random
import string
import encoder
import decoder

def generate_random_message(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    # Define the destination IP and port
    destination_ip = '127.0.0.1'  # Use localhost for testing
    destination_port = 12345      # Use a test port

    # Define headers and bits to use (4 bits from each header)
    headers_to_use = ['ipid', 'ttl', 'window', 'tcp_reserved']
    header_bit_fields = [(header, 4) for header in headers_to_use]

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