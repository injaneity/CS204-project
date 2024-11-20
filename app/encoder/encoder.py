from scapy.all import IP, TCP, send, Raw
from encoder.stego_utils import read_config
import encoder.stego_utils as stego_utils
import random
import time
import threading
import encoder.network_noise_generator as network_noise_generator  # Ensure this is in the same directory or properly installed

# Define available headers and their maximum bits
headers_info = {
    'ipid': {'max_bits': 16},
    'ttl': {'max_bits': 8},
    'window': {'max_bits': 16},
    'tcp_reserved': {'max_bits': 4},
    'tcp_options': {'max_bits': 320},  # Up to 40 bytes
    'ip_options': {'max_bits': 320},   # Up to 40 bytes
    'user_agent': {'max_bits': 8},     # Modifiable within the constraints
}
packet_counter_global = 1

def encode_message(message):
    """Convert message to a binary string."""
    return ''.join(format(ord(char), '08b') for char in message)

def split_into_chunks(data, chunk_size=8):
    """Split binary data into chunks of specified size."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def send_covert_message(destination_ip, destination_port, message, header_bit_fields, noise_type, noise_level, add_noise, verbose, delay=1):
    global packet_counter_global
    """Send a covert message to the destination IP and port with a delay between packets."""
    binary_message = encode_message(message)
    total_bits_per_packet = sum(bits for header, bits in header_bit_fields)
    chunks = split_into_chunks(binary_message, total_bits_per_packet)
    
    if verbose:
        print(f"message converted to bits: {chunks}")
    
    for i, chunk in enumerate(chunks):
        if verbose:
            print()
            print(f"embedding chunk >{chunk}< into packet {packet_counter_global}")
            packet_counter_global += 1
        
        if len(chunk) < total_bits_per_packet:
            chunk = chunk.ljust(total_bits_per_packet, '0')

        ip = IP(dst=destination_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=destination_port, flags='S', window=1024)
        unique_identifier = "AN21NY "
        http_payload = f"GET / HTTP/1.1\r\nHost: {destination_ip}\r\nUser-Agent: Mozilla/5.0 {unique_identifier}\r\n\r\n"
        pkt = ip / tcp / Raw(load=http_payload)

        pkt = stego_utils.embed_with_noise(pkt, chunk, header_bit_fields, noise_type, noise_level, add_noise, verbose)
        send(pkt, verbose=0)

        # Introduce delay between each packet
        time.sleep(delay)

def start_noise_generation(destination_ip, destination_port, server=False):
    """Start background noise generation."""
    network_noise_generator.start_noise(destination_ip, destination_port, server=server)

def get_user_configuration():
    print("Available headers for embedding:")
    for idx, (header, info) in enumerate(headers_info.items()):
        print(f"{idx+1}. {header} (max bits: {info['max_bits']})")
    
    selected_headers = {}
    while True:
        header_choice = input("Enter the number of a header to use (or 'done' to finish): ")
        if header_choice.lower() == 'done':
            break
        try:
            idx = int(header_choice) - 1
            if idx < 0 or idx >= len(headers_info):
                print("Invalid choice. Please try again.")
                continue
            header = list(headers_info.keys())[idx]
            if header in selected_headers:
                print(f"{header} is already selected.")
                continue
            max_bits = headers_info[header]['max_bits']
            bits = int(input(f"Enter number of bits to use for {header} (max {max_bits}): "))
            if bits <= 0 or bits > max_bits:
                print(f"Invalid number of bits. Please enter a value between 1 and {max_bits}.")
                continue
            selected_headers[header] = bits
        except ValueError:
            print("Invalid input. Please enter a number or 'done'.")
            continue
    if not selected_headers:
        print("No headers selected. Exiting.")
        exit()
    return selected_headers

def start_encoder(load_config=False, use_noise=None, messages=None, verbose=False, delay=1):
    if load_config:
        config, destination_port, destination_ip = read_config()
        header_bit_fields = []
        for header, bits in config.items():
            header_bit_fields.append((header, bits))
        print("Configuration loaded in encoder.")
    else:
        # Prompt for destination IP and port if not provided
        destination_ip = input("Enter destination IP address: ")
        destination_port = int(input("Enter destination port number: "))
    
        # Get user configuration for embedding if not provided
        selected_headers = get_user_configuration()
        header_bit_fields = []
        for header, bits in selected_headers.items():
            header_bit_fields.append((header, bits))
        stego_utils.save_to_config(destination_ip, destination_port, header_bit_fields)
        verbose = input("Verbose? (yes/no): ").lower() == 'yes'
        
    # Ask if the user wants to add noise at the start if not provided
    if use_noise is None:
        use_noise = input("Do you want to add noise? (yes/no): ").lower() == 'yes'
    
    if use_noise:
        if messages is None:
            noise_type = input("Enter noise type ('random_padding', 'delay', 'none'): ")
            noise_level = int(input("Enter noise level (integer value): "))
            add_noise = input("Add noise to each packet? (yes/no): ").lower() == 'yes'
            start_noise = input("Start background noise generation? (yes/no): ").lower() == 'yes'
            if start_noise:
                noise_server = input("Start noise as server? (yes/no): ").lower() == 'yes'
                noise_thread = threading.Thread(target=noise.start_noise_generation, args=(destination_ip, destination_port, noise_server))
                noise_thread.daemon = True
                noise_thread.start()
                print("Background noise generation started.")
        else:
            noise_type = 'random_padding'
            noise_level = 5
            add_noise = True
    else:
        noise_type = 'none'
        noise_level = 0
        add_noise = False
    
    # Message input loop
    if messages is None:
        while True:
            message = input("Enter covert message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                print("Exiting.")
                break
            send_covert_message(destination_ip, destination_port, message, header_bit_fields, noise_type, noise_level, add_noise, verbose, delay)
            print("Message sent successfully.\n")
    else:
        for message in messages:
            send_covert_message(destination_ip, destination_port, message, header_bit_fields, noise_type, noise_level, add_noise, verbose, delay)

if __name__ == "__main__":
    delay = float(input("Enter the delay between messages in seconds (e.g., 1 for 1 second, 5 for 5 seconds): "))
    start_encoder(delay=delay)
