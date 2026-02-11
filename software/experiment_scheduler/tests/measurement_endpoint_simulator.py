"""
This module simulates the execution of the PS firmware of an FPGA. sending acknowledgements, measurements and ready signals
allowing to simulate the interaction with the scheduler.
To run this in the current implementation make sure you set the NIC_SUFFIX and SCHEDULER_IP accordingly, e.g.
NIC_SUFFIX = "127.0.0."
SCHEDULER_IP = "localhost"
in the current sample.
"""

import socket
import json
import time


HOST = "127.0.0.1"
PORT = 5024

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_send.bind((HOST, 5053))

    print(f"Listening for UDP packets on {HOST}:{PORT} ... (Mock Device Simulator)")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            decoded_data = data.decode(errors='replace')
            print(f"Received from {addr}: {decoded_data}")

            try:
                msg = json.loads(decoded_data)
                if msg.get('cmd') == 'start_measurement' or 'puf_type' in msg:
                    # 1. Send processing status
                    response_processing = {
                        "msg_type": "response",
                        "cmd": "start_measurement",
                        "cmd_status": "processing"
                    }
                    print(f"Sending processing response to {addr[0]}:5023...")
                    sock_send.sendto(json.dumps(response_processing).encode(), (addr[0], 5023))

                    # Sends measurement data for 50.000 addresses in chunks of 100 each
                    print(f"Sending 500 measurement tuples to {addr[0]}:5023...")
                    for batch_idx in range(500):
                        batch_data = []
                        for i in range(100):
                            addr_val = batch_idx * 100 + i
                            data_val = (addr_val * 7) % 256  # Some dummy data
                            checksum = (addr_val + data_val) % 256
                            batch_data.append((addr_val, data_val, checksum))
                        
                        measurement_msg = {
                            "msg_type": "m",
                            "d": batch_data
                        }
                        print("SEND BATCH")
                        sock_send.sendto(json.dumps(measurement_msg).encode(), (addr[0], 5023))
                        time.sleep(0.1)  # small delay between batches

                    time.sleep(1)

                    # Send ready status to indicate that new data can be scheduled.
                    response_ready = {
                        "msg_type": "response",
                        "cmd": "start_measurement",
                        "cmd_status": "ready"
                    }
                    print(f"Sending ready response to {addr[0]}:5023...")
                    sock_send.sendto(json.dumps(response_ready).encode(), (addr[0], 5023))
            except json.JSONDecodeError:
                print("Received non-JSON data, ignoring.")

        except KeyboardInterrupt:
            print("\nStopping listener.")
            break

    sock.close()

if __name__ == "__main__":
    main()

