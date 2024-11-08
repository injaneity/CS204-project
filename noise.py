import threading
import time
import random
import stego_utils
from scapy.all import *

def start_noise_generation(destination_ip, destination_port, server=False):
    """Start background noise generation."""
    # Implement the noise generation logic here.
    # For the sake of this example, let's simulate noise with dummy packets.
    def generate_noise():
        while True:
            pkt = IP(dst=destination_ip)/TCP(dport=destination_port)/Raw(load="Noise")
            send(pkt, verbose=0)
            time.sleep(random.uniform(0.1, 0.5))  # Adjust as needed

    noise_thread = threading.Thread(target=generate_noise)
    noise_thread.daemon = True
    noise_thread.start()
    print("Background noise generation started.")

def embed_with_noise(packet, data_bits, header_bit_fields, noise_type, noise_level, add_noise):
    """Embed data with customizable noise for better stealth."""
    packet = stego_utils.embed_data_into_packet(packet, data_bits, header_bit_fields)
    
    if add_noise:
        if noise_type == 'random_padding':
            random_padding = ''.join(random.choices(['A', 'B', 'C', 'D'], k=random.randint(0, noise_level)))
            if Raw in packet:
                packet[Raw].load += random_padding.encode()
        elif noise_type == 'delay':
            delay = random.uniform(0.05, 0.2) * noise_level
            time.sleep(delay)
    
    return packet

# Note: The function `embed_data_into_packet` should be accessible here.
# If it's in your main script, you need to import it or refactor accordingly.
