from scapy.all import *
import random
import time
import argparse
import threading
import network_noise_generator  # Ensure this is in the same directory or properly installed

def encode_message(message):
    """Convert message to a binary string."""
    return ''.join(format(ord(char), '08b') for char in message)

def split_into_chunks(data, chunk_size=8):
    """Split binary data into chunks of specified size."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def embed_in_ipid(packet, bits):
    """Embed 2 bits into the IPID field."""
    original_ipid = packet[IP].id
    new_ipid = (original_ipid & 0xFFFC) | int(bits, 2)
    packet[IP].id = new_ipid
    return packet

def embed_in_ttl(packet, bits):
    """Embed 2 bits into the TTL field."""
    original_ttl = packet[IP].ttl
    new_ttl = (original_ttl & 0xFC) | int(bits, 2)
    packet[IP].ttl = new_ttl
    return packet

def embed_in_window(packet, bits):
    """Embed 2 bits into the TCP Window Size."""
    original_window = packet[TCP].window
    new_window = (original_window & 0xFFFC) | int(bits, 2)
    packet[TCP].window = new_window
    return packet

def embed_in_user_agent(packet, bits):
    """Embed 2 bits into the HTTP User-Agent Header."""
    if Raw in packet:
        try:
            payload = packet[Raw].load.decode()
            if "User-Agent: " in payload:
                parts = payload.split("User-Agent: ")
                user_agent = parts[1].split("\r\n")[0]
                if len(user_agent) > 0:
                    last_char = user_agent[-1]
                    last_char_ord = ord(last_char)
                    new_last_char_ord = (last_char_ord & 0xFFFC) | int(bits, 2)
                    new_last_char = chr(new_last_char_ord)
                    new_user_agent = user_agent[:-1] + new_last_char
                    new_payload = parts[0] + "User-Agent: " + new_user_agent + "\r\n" + "\r\n".join(parts[1].split("\r\n")[1:])
                    packet[Raw].load = new_payload.encode()
        except:
            pass  # Ignore decoding errors
    return packet

def embed_data_into_packet(packet, data_bits, encoding_fields):
    """Embed 8 bits of data into specified packet fields."""
    if 'ipid' in encoding_fields:
        packet = embed_in_ipid(packet, data_bits[0:2])
    if 'ttl' in encoding_fields:
        packet = embed_in_ttl(packet, data_bits[2:4])
    if 'window' in encoding_fields:
        packet = embed_in_window(packet, data_bits[4:6])
    if 'user_agent' in encoding_fields:
        packet = embed_in_user_agent(packet, data_bits[6:8])
    return packet

def embed_with_noise(packet, data_bits, noise_type, noise_level, add_noise):
    """Embed data with customizable noise for better stealth."""
    packet = embed_data_into_packet(packet, data_bits, encoding_fields=['ipid', 'ttl', 'window', 'user_agent'])

    if add_noise:
        if noise_type == 'random_padding':
            random_padding = ''.join(random.choices(['A', 'B', 'C', 'D'], k=random.randint(0, noise_level)))
            if Raw in packet:
                packet[Raw].load += random_padding.encode()
        elif noise_type == 'delay':
            delay = random.uniform(0.05, 0.2) * noise_level
            time.sleep(delay)

    return packet

def send_covert_message(destination_ip, destination_port, message, encoding_fields, noise_type, noise_level, add_noise):
    """Send a covert message to the destination IP and port."""
    binary_message = encode_message(message)
    chunks = split_into_chunks(binary_message, 8)

    for chunk in chunks:
        if len(chunk) < 8:
            chunk = chunk.ljust(8, '0')
        
        ip = IP(dst=destination_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=destination_port, flags='S', window=1024)
        unique_identifier = "AN21NY "
        http_payload = f"GET / HTTP/1.1\r\nHost: {destination_ip}\r\nUser-Agent: Mozilla/5.0 {unique_identifier}\r\n\r\n"
        pkt = ip / tcp / Raw(load=http_payload)
        
        pkt = embed_with_noise(pkt, chunk, noise_type, noise_level, add_noise)
        send(pkt, verbose=0)

def start_noise_generation(destination_ip, destination_port, server=False):
    """Start background noise generation."""
    network_noise_generator.start_noise(destination_ip, destination_port, server=server)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Steganography Encoder")
    parser.add_argument("destination_ip", help="Destination IP address")
    parser.add_argument("destination_port", type=int, help="Destination port number")
    parser.add_argument("message", help="Covert message to send")
    parser.add_argument("--encoding_fields", nargs='+', default=['ipid', 'ttl', 'window', 'user_agent'],
                        help="Specify fields for encoding (e.g., ipid ttl window user_agent)")
    parser.add_argument("--noise_type", choices=['random_padding', 'delay', 'none'], default='random_padding',
                        help="Type of noise to add")
    parser.add_argument("--noise_level", type=int, default=5, help="Amount of noise to add")
    parser.add_argument("--add_noise", action='store_true', help="Include noise in the embedding process")
    parser.add_argument("--start_noise_gen", action='store_true', help="Start background network noise generation")
    parser.add_argument("--noise_server", action='store_true', help="Start an HTTP server for noise generation")
    args = parser.parse_args()

    if args.start_noise_gen:
        # Start network noise generation in a separate thread
        noise_thread = threading.Thread(target=start_noise_generation, args=(args.destination_ip, args.destination_port, args.noise_server))
        noise_thread.daemon = True
        noise_thread.start()
        print("Background noise generation started.")

    print(f"Sending covert message to {args.destination_ip}:{args.destination_port}")
    send_covert_message(args.destination_ip, args.destination_port, args.message, args.encoding_fields, args.noise_type, args.noise_level, args.add_noise)
    print("Message sent successfully.")
