import sys
import socket
import random
import string

# Create a TCP/IP socket
sock_alpine_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_alpine_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address_alpine_1 = ('192.168.122.156', 10000)
server_address_alpine_2 = ('192.168.122.181', 10000)
print(f"connecting to {server_address_alpine_1}")
print(f"connecting to {server_address_alpine_2}")
sock_alpine_1.connect(server_address_alpine_1)
sock_alpine_2.connect(server_address_alpine_2)

try:
    # Random string sebesar 2097152 bit ~ 2MB
    message_alpine_1 = ''.join(random.choices(string.ascii_lowercase, k = 2097152))
    message_alpine_2 = ''.join(random.choices(string.ascii_lowercase, k = 2097152))
    print(f"sending {message_alpine_1}")
    print(f"sending {message_alpine_2}")

    # sendall ke alpine 1 dan alpine 2
    sock_alpine_1.sendall(message_alpine_1.encode())
    sock_alpine_2.sendall(message_alpine_2.encode())

    # Respon dari alpine 1
    amount_received_alpine_1 = 0
    amount_expected_alpine_1 = len(message_alpine_1)
    while amount_received_alpine_1 < amount_expected_alpine_1:
        data_alpine_1 = sock_alpine_1.recv(1024)
        amount_received_alpine_1 += len(data_alpine_1)
        print("dari alpine 1: ", f"{data_alpine_1}")

    # Respon dari alpine 1
    amount_received_alpine_2 = 0
    amount_expected_alpine_2 = len(message_alpine_2)
    while amount_received_alpine_2 < amount_expected_alpine_2:
        data_alpine_2 = sock_alpine_2.recv(1024)
        amount_received_alpine_2 += len(data_alpine_2)
        print("dari alpine 2: ", f"{data_alpine_2}")
finally:
    print("closing")
    sock_alpine_1.close()
    sock_alpine_2.close()