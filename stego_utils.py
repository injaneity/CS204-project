from scapy.all import IP, TCP, IPOption, Raw
import random
import time

def encode_message(message):
    """Convert message to a binary string."""
    return format(message, '08b') 

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

def embed_with_noise(packet, data_bits, header_bit_fields, noise_type, noise_level, add_noise, verbose):
    """Embed data with customizable noise for better stealth."""
    packet = embed_data_into_packet(packet, data_bits, header_bit_fields, verbose)
    
    if add_noise:
        if noise_type == 'random_padding':
            random_padding = ''.join(random.choices(['A', 'B', 'C', 'D'], k=random.randint(0, noise_level)))
            if Raw in packet:
                packet[Raw].load += random_padding.encode()
        elif noise_type == 'delay':
            delay = random.uniform(0.05, 0.2) * noise_level
            time.sleep(delay)
    
    return packet

def embed_data_into_packet(packet, data_bits, header_bit_fields, verbose):
    """Embed data bits into specified packet fields."""
    bit_index = 0
    for header, num_bits in header_bit_fields:
        bits_to_embed = data_bits[bit_index:bit_index+num_bits]
        if verbose:
            print(f"embedding >{bits_to_embed}< in {header}")
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

def read_config():
    """Read the config.txt file and return header configurations and port."""
    config = {}
    port = None
    with open('config.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('Header:'):
                parts = line.strip().split(',')
                header = parts[0].split(':')[1].strip()
                bits = int(parts[1].split(':')[1].strip())
                config[header] = bits
            elif line.startswith('Port:'):
                port = int(line.strip().split(':')[1].strip())
            elif line.startswith('Destination IP:'):
                destination_ip = line.strip().split(':')[1].strip()
    return config, port, destination_ip

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