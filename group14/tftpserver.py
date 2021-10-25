"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 051
- Fall 2021
- Lab 07
- Names:
  - Elisha Hamp
  - Josiah Clausen

A Trivial File Transfer Protocol Server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

# import modules -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket
import os
import math

# Helpful constants used by TFTP
from os.path import exists

TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


def main():
    """
    Processes a single TFTP request
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    message, address = receive_request(client_socket)
    op_code, file_name, mode, error = parse_request(message)
    if not error:
        read_file(file_name, client_socket, address)
    else:
        send_error(client_socket, address, 1)

    ################################################JOSIAH ^ ELI

    ####################################################
    # Your code ends here                              #
    ####################################################

    client_socket.close()


def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: THe name of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        #   This function throws an exception if the file doesn't exist
        file_size = os.stat(filename).st_size
        return math.ceil(file_size / TFTP_BLOCK_SIZE)
    except:
        return -1


def get_file_block(filename, block_number):
    """
    Get the file block data for the given file and block number
    :param filename: The name of the file to read
    :param block_number: The block number (1 based)
    :return: The data contents (as a bytes object) of the file block
    """
    file = open(filename, 'rb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    block_data = file.read(TFTP_BLOCK_SIZE)
    file.close()
    return block_data


def put_file_block(filename, block_data, block_number):
    """
    Writes a block of data to the given file
    :param filename: The name of the file to save the block to
    :param block_data: The bytes object containing the block data
    :param block_number: The block number (1 based)
    :return: Nothing
    """
    file = open(filename, 'wb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    file.write(block_data)
    file.close()


def socket_setup():
    """
    Sets up a UDP socket to listen on the TFTP port
    :return: The created socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', TFTP_PORT))
    return s


####################################################
# Write additional helper functions starting here  #
####################################################
def receive_request(receive_request):
    """
    This method recives the request from a client
    :param receive_request: the socket that is used to receive from the client
    TFTP
    :return: the request from the client in bytes
    """
    byte, address = receive_request.recvfrom(MAX_UDP_PACKET_SIZE)
    return byte, address


def parse_request(request):
    """
    Gets the request and determines what to do with it
    :param request:
    :return: the opcode of the packet and whether it is an error request.
    it also returns the file name mode as well as if it needs to throw an error
    """
    op_code = 5
    file_name = b''
    mode = b''
    error = False
    if verify_request(request):
        print(str(type) + "THIS IS THE FIRST BYTE")
        op_code = 1
        code = request.replace(b'\x00\01', b'')
        print("GETFILE HAS BEEN CHOSEN")
        file_name = code[0: code.index(b'\x00')]
        print(file_name)
        code = code.replace(file_name + b'\x00', b'')
        mode = code[0: code.index(b'\x00')]
        print(mode)
    else:
        error = True
    return op_code, file_name, mode, error


def verify_request(request_line):
    """
    This method checks if the request line is a read request and that it has
    the proper amount of breaks in it
    :param request_line:
    :return: a boolean on weather the request is a valid read request
    """
    is_request = True
    if request_line.count(b'\x00') != 3:
        is_request = False
    type = request_line[0: 2]
    if type != b'\x00\x01':
        is_request = False
    return is_request


def send_error(client_socket, address, error_code):
    """
    This method is designed to send an error to the client if something goes wrong
    it can send three errors right now. If the user enters a request that is not
    covered. If the user tries to get a file that does not exist or we don't have
    access to. Finally a error for any unexpected problems
    :param client_socket: the client socket that the error will be send to
    :param address: the address to know where the request came from
    :param error_code: the code given by the program to tell which error it is
    """
    if error_code == 1:
        client_socket.sendto(b'\x00\x05\x00\x04\x40The '
                             b'request was invalid or not covered by this server\x00', address)
    elif error_code == 2:
        client_socket.sendto(b'\x00\x05\x00\x04\x40The file you requested does not exist\x00', address)
    else:
        client_socket.sendto(b'\x00\x05\x00\x04\x40Something went wrong we dont know what\x00', address)



############################################### JOSIAH


def read_file(file_name, data_socket, address):
    """
    :author: Elisha Hamp
    Takes in a file_name and uses it to create blocks
    :param file_name:
    :return:
    """
    file_exists = exists(file_name)
    if file_exists:
        count = get_file_block_count(file_name)+1
        for i in range(1, count):
            block = get_file_block(file_name, i)
            send_block(i, block, data_socket, address)
            if not wait_for_ack(i, data_socket):
                i -= 1
    else:
        send_error(data_socket, address, 2)

def send_block(b_num, block, data_socket, address):
    """
    :author: Elisha Hamp
    Takes in the block number and the block of bits to send,
    and assembles a message to be sent using the info provided.
    :param b_num:
    :param block:
    :return:
    """
    code = b'\x00\x03'
    block_num = b_num.to_bytes(2, 'big')
    response = code + block_num + block
    print(response)
    data_socket.sendto(response, address)


def wait_for_ack(b_num, data_socket):
    """
    Takes in the block number of the block which was just sent, then waits
    for the client ack message. It then either times out or receives an ack.
    If it receives an ack, it then compares the ack number to the param number.
    :param b_num:
    :return:
    """
    data_socket.settimeout(10)
    positive_ack = False
    try:
        ack, address = data_socket.recvfrom(MAX_UDP_PACKET_SIZE)
        code, received_b_num = parse_ack(ack)
        if int.from_bytes(code,'big') == 4 and received_b_num == b_num:
            positive_ack = True
    except TimeoutError:
        return False
    return positive_ack


def parse_ack(ack):
    """
    :author: Elisha Hamp
    parses the acknowledgement response.
    :param ack:
    :return:
    """
    code = ack[0: 2]
    print(code)
    b_num = ack[2: 4]
    print(b_num)

    return code, b_num


main()
