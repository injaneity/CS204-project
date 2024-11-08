# evaluate.py
import threading
import time
import random
import string
import encoder
import decoder

def save_to_config(destination_ip, destination_port, header_bit_fields):
    total_bits_per_packet = sum(bits for header, bits in header_bit_fields)
    # Output configuration
    print("\nConfiguration saved:")
    for header, bits in header_bit_fields:
        print(f"Header: {header}, Bits: {bits}")
    print(f"Total bits per packet: {total_bits_per_packet}\n")
    # Save configuration to a file
    with open('config.txt', 'w') as f:
        f.write("Configuration:\n")
        for header, bits in header_bit_fields:
            f.write(f"Header: {header}, Bits: {bits}\n")
        f.write(f"Total bits per packet: {total_bits_per_packet}\n")
        f.write(f"Port: {destination_port}\n")
        f.write(f"Destination IP: {destination_ip}\n")

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

    for header, info in headers_info.items():
        for bits in range(8, info['max_bits'] + 1, 8):
            print(f"Current Header: {header}, Bits: {bits}")  # Print the current header and bits
            header_bit_fields = [(header, bits)]
            save_to_config(destination_ip, destination_port, header_bit_fields)
            # Generate random messages to send
            messages = [generate_random_message(20) for _ in range(1)]
            
            for i, message in enumerate(messages):
                print(f"Message {i + 1}: {message}")
            print()


            # Run the encoder with the specified settings and messages
            encoder.start_encoder(
                load_config=True,
                use_noise=False,
                messages=messages
            )

            # Give some time for the messages to be processed
            time.sleep(2)

            print("\nEvaluation completed.")

if __name__ == '__main__':
    main()