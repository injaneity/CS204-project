from scapy.all import IP, TCP, IPOption, sniff, Raw
from encoder.stego_utils import read_config

# Global variables to store the accumulated binary message
binary_message = ""
bit_accumulator = ""
callback_global = None
verbose_global = False
str_accumulator= ""
packet_counter_global = 1

def packet_handler(pkt):
    global binary_message, bit_accumulator, header_bit_fields, callback_global, verbose_global, str_accumulator, packet_counter_global
    if IP in pkt and TCP in pkt:
        try: 
            payload = pkt[Raw].load.decode()
            if "AN21NY" not in payload:
                return
        except Exception as e:
            return
        
        data_bits = ""
        # print("\n--- Debug Info ---")  # Start of debug information
        # print(f"Packet {packet_counter_global}: Source IP {pkt[IP].src}, Destination IP {pkt[IP].dst}")

        total_bits = sum(num_bits for _, num_bits in header_bit_fields)
        
        # Extract bits based on headers specified in config
        for header, num_bits in header_bit_fields:
            if header == 'ipid':
                ipid_bits = format(pkt[IP].id, '016b')[-num_bits:]
                print(f"IPID bits: {ipid_bits} (last {num_bits} bits)")
                data_bits += ipid_bits
            elif header == 'ttl':
                ttl_bits = format(pkt[IP].ttl, '08b')[-num_bits:]
                print(f"TTL bits: {ttl_bits} (last {num_bits} bits)")
                data_bits += ttl_bits
            elif header == 'window':
                window_bits = format(pkt[TCP].window, '016b')[-num_bits:]
                print(f"Window bits: {window_bits} (last {num_bits} bits)")
                data_bits += window_bits
            elif header == 'tcp_reserved':
                reserved_bits = format(pkt[TCP].reserved, '04b')[-num_bits:]
                print(f"TCP Reserved bits: {reserved_bits} (last {num_bits} bits)")
                data_bits += reserved_bits
            elif header == 'tcp_options':
                # Extract data from TCP Options
                options = pkt[TCP].options
                for opt in options:
                    if isinstance(opt, tuple) and opt[0] == 254:  # Our experimental option kind
                        option_data = opt[1]
                        option_data_bits = ''.join(format(byte, '08b') for byte in option_data)
                        option_data_bits = option_data_bits[-num_bits:]
                        print(f"TCP Option bits: {option_data_bits} (last {num_bits} bits)")
                        data_bits += option_data_bits
                        break
            elif header == 'ip_options':
                # Extract data from IP Options
                options = pkt[IP].options
                for opt in options:
                    if isinstance(opt, IPOption) and opt.option == 30:  # Our experimental option number
                        option_data = opt.value
                        option_data_bits = ''.join(format(byte, '08b') for byte in option_data)
                        option_data_bits = option_data_bits[-num_bits:]
                        print(f"IP Option bits: {option_data_bits} (last {num_bits} bits)")
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
                            print(f"User-Agent bits: {ua_bits} (last {num_bits} bits)")
                            data_bits += ua_bits
                    except Exception as e:
                        print(f"Error processing User-Agent: {e}")
                        return
            else:
                print(f"Unknown header: {header}")

        print(f"Extracted data bits from packet: {data_bits}")  # Debug print for accumulated bits
        print("--- End Debug Info ---\n")  # End of debug information

        if (len(data_bits) != total_bits):
            return
        if verbose_global:
            print(f"packet {packet_counter_global} received! bits extracted: >{data_bits}<")
            packet_counter_global += 1
        
        # Accumulate bits
        bit_accumulator += data_bits

        if verbose_global:
            # Accumulate all bits without decoding in verbose mode until all messages are received
            while len(bit_accumulator) >= 8:
                byte_bits = bit_accumulator[:8]
                bit_accumulator = bit_accumulator[8:]
                try:
                    char = chr(int(byte_bits, 2))
                    if callback_global:
                        callback_global(char)
                    str_accumulator += char
                except ValueError:
                    print(f"Invalid byte sequence: {byte_bits}")
        else:
            # Decode bytes from accumulated bits immediately in non-verbose mode
            while len(bit_accumulator) >= 8:
                byte_bits = bit_accumulator[:8]
                bit_accumulator = bit_accumulator[8:]
                try:
                    char = chr(int(byte_bits, 2))
                    if callback_global:
                        callback_global(char)
                    print(char, end='', flush=True)
                except ValueError:
                    print(f"Invalid byte sequence: {byte_bits}")
                    continue  # Ignore incomplete or invalid byte sequences

def start_decoder(config_file='config.txt', sniff_filter=None, timeout=None, callback=None, verbose=False):
    global header_bit_fields, bit_accumulator, binary_message, callback_global, verbose_global, str_accumulator
    verbose_global = verbose
    callback_global = callback
    # Read configuration from config.txt
    config, port, _ = read_config()
    header_bit_fields = []
    for header, bits in config.items():
        header_bit_fields.append((header, bits))
    
    # Print the configuration being used
    print("Configuration loaded in decoder:")
    for header, bits in header_bit_fields:
        print(f"Header: {header}, Bits: {bits}")
    
    print(f"Listening on port: {port}")
    print("Decoding messages... Press Ctrl+C to stop.\n")

    # Build the sniff filter if not provided
    if sniff_filter is None:
        sniff_filter = f"tcp port {port}"

    try:
        # Start sniffing packets and process each packet with packet_handler
        sniff(filter=sniff_filter, prn=packet_handler, store=0, timeout=timeout)
    except KeyboardInterrupt:
        print("\nSniffing stopped by user.")
    
    if verbose_global:
        print(f"final accumulated message > {str_accumulator}")

if __name__ == "__main__":
    start_decoder()
