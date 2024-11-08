from scapy.all import IP, TCP, IPOption, sniff, Raw
from stego_utils import read_config

# Global variables to store the accumulated binary message
binary_message = ""
bit_accumulator = ""

def packet_handler(pkt):
    global binary_message, bit_accumulator, header_bit_fields
    if IP in pkt and TCP in pkt:
        data_bits = ""
        # Extract bits based on headers specified in config
        for header, num_bits in header_bit_fields:
            if header == 'ipid':
                ipid_bits = format(pkt[IP].id, '016b')[-num_bits:]
                data_bits += ipid_bits
            elif header == 'ttl':
                ttl_bits = format(pkt[IP].ttl, '08b')[-num_bits:]
                data_bits += ttl_bits
            elif header == 'window':
                window_bits = format(pkt[TCP].window, '016b')[-num_bits:]
                data_bits += window_bits
            elif header == 'tcp_reserved':
                reserved_bits = format(pkt[TCP].reserved, '04b')[-num_bits:]
                data_bits += reserved_bits
            elif header == 'tcp_options':
                # Extract data from TCP Options
                options = pkt[TCP].options
                for opt in options:
                    if isinstance(opt, tuple) and opt[0] == 254:  # Our experimental option kind
                        option_data = opt[1]
                        # Convert the option data bytes to bits
                        option_data_bits = ''.join(format(byte, '08b') for byte in option_data)
                        # Truncate to the specified number of bits
                        option_data_bits = option_data_bits[-num_bits:]
                        data_bits += option_data_bits
                        break  # Exit after finding the option data
            elif header == 'ip_options':
                # Extract data from IP Options
                options = pkt[IP].options
                for opt in options:
                    if isinstance(opt, IPOption) and opt.option == 30:  # Our experimental option number
                        option_data = opt.value
                        option_data_bits = ''.join(format(byte, '08b') for byte in option_data)
                        option_data_bits = option_data_bits[-num_bits:]
                        data_bits += option_data_bits
                        break
            elif header == 'user_agent':
                if Raw in pkt:
                    try:
                        payload = pkt[Raw].load.decode()
                        if "AN21NY" not in payload:
                            return
                        if "User-Agent: " in payload:
                            parts = payload.split("User-Agent: ")
                            user_agent = parts[1].split("\r\n")[0]
                            user_agent_binary = ''.join(format(ord(c), '08b') for c in user_agent)
                            ua_bits = user_agent_binary[-num_bits:]
                            data_bits += ua_bits
                    except:
                        return
            else:
                print(f"Unknown header: {header}")
        # Accumulate bits
        bit_accumulator += data_bits
        # Try to decode bytes from the accumulated bits
        while len(bit_accumulator) >= 8:
            byte_bits = bit_accumulator[:8]
            bit_accumulator = bit_accumulator[8:]
            try:
                char = chr(int(byte_bits, 2))
                print(char, end='', flush=True)
            except ValueError:
                continue

def start_decoder(config_file='config.txt', sniff_filter=None, timeout=None):
    global header_bit_fields, bit_accumulator, binary_message
    # Read configuration from config.txt
    config, port, _ = read_config()
    header_bit_fields = []
    for header, bits in config.items():
        header_bit_fields.append((header, bits))
    total_bits_per_packet = sum(bits for header, bits in header_bit_fields)
    print("Configuration loaded in decoder.")
    # for header, bits in header_bit_fields:
    #     print(f"Header: {header}, Bits: {bits}")
    # print(f"Total bits per packet: {total_bits_per_packet}")
    print(f"Listening on port: {port}\n")
    print("Decoding messages... Press Ctrl+C to stop.")

    # Build the sniff filter if not provided
    if sniff_filter is None:
        sniff_filter = f"tcp port {port}"

    try:
        # Start sniffing packets and process each packet with packet_handler
        sniff(filter=sniff_filter, prn=packet_handler, store=0, timeout=timeout)
    except KeyboardInterrupt:
        print("\nSniffing stopped by user.")

if __name__ == "__main__":
    start_decoder()
