from scapy.all import *
import argparse

def decode_covert_message(packets):
    """Decode covert message from captured packets."""
    binary_message = ""
    for pkt in packets:
        if IP in pkt and TCP in pkt:
            # extracts from all header fields
            ipid_bits = format(pkt[IP].id, '016b')[-2:]
            ttl_bits = format(pkt[IP].ttl, '08b')[-2:]
            window_bits = format(pkt[TCP].window, '016b')[-2:]
            ua_bits = "00"
            if Raw in pkt:
                try:
                    payload = pkt[Raw].load.decode()
                    if "User-Agent: " in payload:
                        parts = payload.split("User-Agent: ")
                        user_agent = parts[1].split("\r\n")[0]
                        if len(user_agent) > 0:
                            last_char_ord = ord(user_agent[-1])
                            ua_bits = format(last_char_ord, '08b')[-2:]
                except:
                    pass
            data_bits = ipid_bits + ttl_bits + window_bits + ua_bits
            binary_message += data_bits
    
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) < 8:
            continue
        try:
            message += chr(int(byte, 2))
        except:
            continue
    
    return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Steganography Decoder")
    parser.add_argument("--port", type=int, default=80, help="Port number to sniff (default: 80)")
    parser.add_argument("--timeout", type=int, default=30, help="Sniffing duration in seconds (default: 30)")
    args = parser.parse_args()

    print(f"Sniffing packets on port {args.port} for {args.timeout} seconds...")
    try:
        captured_packets = sniff(filter=f"tcp port {args.port}", timeout=args.timeout)
        message = decode_covert_message(captured_packets)
        print("Decoded Message:", message)
    except KeyboardInterrupt:
        print("\nSniffing interrupted by user.")
