from scapy.all import IP, TCP, IPOption, send, Raw
import random
import noise
import time
import threading
import network_noise_generator  # Ensure this is in the same directory or properly installed

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

def encode_message(message):
    """Convert message to a binary string."""
    return ''.join(format(ord(char), '08b') for char in message)

def split_into_chunks(data, chunk_size=8):
    """Split binary data into chunks of specified size."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def embed_in_ipid(packet, bits, num_bits):
    """Embed num_bits into the IPID field."""
    original_ipid = packet[IP].id
    mask = (1 << (16 - num_bits)) - 1  # Mask to keep upper bits
    new_ipid = (original_ipid & (mask << num_bits)) | int(bits, 2)
    packet[IP].id = new_ipid
    return packet

def embed_in_ttl(packet, bits, num_bits):
    """Embed num_bits into the TTL field."""
    original_ttl = packet[IP].ttl
    mask = (1 << (8 - num_bits)) - 1  # Mask to keep upper bits
    new_ttl = (original_ttl & (mask << num_bits)) | int(bits, 2)
    packet[IP].ttl = new_ttl
    return packet

def embed_in_window(packet, bits, num_bits):
    """Embed num_bits into the TCP Window Size."""
    original_window = packet[TCP].window
    mask = (1 << (16 - num_bits)) - 1  # Mask to keep upper bits
    new_window = (original_window & (mask << num_bits)) | int(bits, 2)
    packet[TCP].window = new_window
    return packet

def embed_in_tcp_reserved(packet, bits, num_bits):
    """Embed num_bits into the TCP Reserved field."""
    original_reserved = packet[TCP].reserved
    mask = (1 << (4 - num_bits)) - 1  # Mask to keep upper bits
    new_reserved = (original_reserved & (mask << num_bits)) | int(bits, 2)
    packet[TCP].reserved = new_reserved
    return packet

def embed_in_tcp_options(packet, bits, num_bits):
    """Embed num_bits into TCP Options field."""
    num_bytes = (num_bits + 7) // 8  # Convert bits to bytes
    data_bytes = int(bits, 2).to_bytes(num_bytes, byteorder='big')
    option_kind = 254  # Experimental option kind
    option_data = data_bytes
    option = (option_kind, option_data)
    if 'options' in packet[TCP].fields:
        packet[TCP].options.append(option)
    else:
        packet[TCP].options = [option]
    return packet

def embed_in_ip_options(packet, bits, num_bits):
    """Embed num_bits into IP Options field."""
    num_bytes = (num_bits + 7) // 8  # Convert bits to bytes
    data_bytes = int(bits, 2).to_bytes(num_bytes, byteorder='big')
    option_number = 30  # Experimental option number
    
    # Define length: 2 bytes for type + length fields, plus the length of data_bytes
    length = 2 + len(data_bytes)
    
    # Create the IP option with all necessary fields
    option = IPOption(copy_flag=1, optclass=0, option=option_number, length=length, value=data_bytes)
    
    # Append the option to packet's IP options
    if 'options' in packet[IP].fields:
        packet[IP].options.append(option)
    else:
        packet[IP].options = [option]
        
    return packet

def embed_in_user_agent(packet, bits, num_bits):
    """Embed num_bits into the HTTP User-Agent Header."""
    if Raw in packet:
        try:
            payload = packet[Raw].load.decode()
            if "User-Agent: " in payload:
                parts = payload.split("User-Agent: ")
                user_agent = parts[1].split("\r\n")[0]
                # Modify the last character or extend the User-Agent string
                user_agent_binary = ''.join(format(ord(c), '08b') for c in user_agent)
                # Replace the last num_bits
                user_agent_binary = user_agent_binary[:-num_bits] + bits
                # Convert back to string
                new_user_agent = ''.join(chr(int(user_agent_binary[i:i+8], 2)) for i in range(0, len(user_agent_binary), 8))
                new_payload = parts[0] + "User-Agent: " + new_user_agent + "\r\n" + "\r\n".join(parts[1].split("\r\n")[1:])
                packet[Raw].load = new_payload.encode()
        except Exception as e:
            print(f"Error embedding in User-Agent: {e}")
    return packet

def embed_data_into_packet(packet, data_bits, header_bit_fields):
    """Embed data bits into specified packet fields."""
    bit_index = 0
    for header, num_bits in header_bit_fields:
        bits_to_embed = data_bits[bit_index:bit_index+num_bits]
        if len(bits_to_embed) < num_bits:
            bits_to_embed = bits_to_embed.ljust(num_bits, '0')
        if header == 'ipid':
            packet = embed_in_ipid(packet, bits_to_embed, num_bits)
        elif header == 'ttl':
            packet = embed_in_ttl(packet, bits_to_embed, num_bits)
        elif header == 'window':
            packet = embed_in_window(packet, bits_to_embed, num_bits)
        elif header == 'tcp_reserved':
            packet = embed_in_tcp_reserved(packet, bits_to_embed, num_bits)
        elif header == 'tcp_options':
            packet = embed_in_tcp_options(packet, bits_to_embed, num_bits)
        elif header == 'ip_options':
            packet = embed_in_ip_options(packet, bits_to_embed, num_bits)
        elif header == 'user_agent':
            packet = embed_in_user_agent(packet, bits_to_embed, num_bits)
        else:
            print(f"Unknown header: {header}")
        bit_index += num_bits
    return packet

def embed_with_noise(packet, data_bits, header_bit_fields, noise_type, noise_level, add_noise):
    """Embed data with customizable noise for better stealth."""
    packet = embed_data_into_packet(packet, data_bits, header_bit_fields)

    if add_noise:
        if noise_type == 'random_padding':
            random_padding = ''.join(random.choices(['A', 'B', 'C', 'D'], k=random.randint(0, noise_level)))
            if Raw in packet:
                packet[Raw].load += random_padding.encode()
        elif noise_type == 'delay':
            delay = random.uniform(0.05, 0.2) * noise_level
            time.sleep(delay)

    return packet

def send_covert_message(destination_ip, destination_port, message, header_bit_fields, noise_type, noise_level, add_noise):
    """Send a covert message to the destination IP and port."""
    binary_message = encode_message(message)
    total_bits_per_packet = sum(bits for header, bits in header_bit_fields)
    chunks = split_into_chunks(binary_message, total_bits_per_packet)

    for chunk in chunks:
        if len(chunk) < total_bits_per_packet:
            chunk = chunk.ljust(total_bits_per_packet, '0')

        ip = IP(dst=destination_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=destination_port, flags='S', window=1024)
        # Prepare HTTP payload if necessary
        unique_identifier = "AN21NY "
        http_payload = f"GET / HTTP/1.1\r\nHost: {destination_ip}\r\nUser-Agent: Mozilla/5.0 {unique_identifier}\r\n\r\n"
        pkt = ip / tcp / Raw(load=http_payload)

        # Call embed_with_noise from the noise module
        pkt = noise.embed_with_noise(pkt, chunk, header_bit_fields, noise_type, noise_level, add_noise)
        print("Chunk:")
        print(chunk)
        print(pkt.summary())
        send(pkt, verbose=0)

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

def main():
    # Prompt for destination IP and port
    destination_ip = input("Enter destination IP address: ")
    destination_port = int(input("Enter destination port number: "))
    
    # Get user configuration for embedding
    selected_headers = get_user_configuration()
    header_bit_fields = []
    for header, bits in selected_headers.items():
        header_bit_fields.append((header, bits))
    total_bits_per_packet = sum(bits for header, bits in selected_headers.items())
    
    # Output configuration
    print("\nConfiguration:")
    for header, bits in selected_headers.items():
        print(f"Header: {header}, Bits: {bits}")
    print(f"Total bits per packet: {total_bits_per_packet}\n")
    # Save configuration to a file
    with open('config.txt', 'w') as f:
        f.write("Configuration:\n")
        for header, bits in selected_headers.items():
            f.write(f"Header: {header}, Bits: {bits}\n")
        f.write(f"Total bits per packet: {total_bits_per_packet}\n")
        # **Add this line to save the port number**
        f.write(f"Port: {destination_port}\n")
    
    # Ask if the user wants to add noise at the start
    use_noise = input("Do you want to add noise? (yes/no): ").lower() == 'yes'

    if use_noise:
        # If the user wants to add noise, ask for noise settings
        noise_type = input("Enter noise type ('random_padding', 'delay', 'none'): ")
        noise_level = int(input("Enter noise level (integer value): "))
        add_noise = input("Add noise to each packet? (yes/no): ").lower() == 'yes'
        start_noise = input("Start background noise generation? (yes/no): ").lower() == 'yes'
        if start_noise:
            noise_server = input("Start noise as server? (yes/no): ").lower() == 'yes'
            # Start noise generation in a separate thread
            # Use noise.start_noise_generation from the noise module
            noise_thread = threading.Thread(target=noise.start_noise_generation, args=(destination_ip, destination_port, noise_server))
            noise_thread.daemon = True
            noise_thread.start()
            print("Background noise generation started.")
    else:
        # Set default values for noise parameters
        noise_type = 'none'
        noise_level = 0
        add_noise = False

    # Message input loop
    while True:
        message = input("Enter covert message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            print("Exiting.")
            break
        send_covert_message(destination_ip, destination_port, message, header_bit_fields, noise_type, noise_level, add_noise)
        print("Message sent successfully.\n")

if __name__ == "__main__":
    main()
