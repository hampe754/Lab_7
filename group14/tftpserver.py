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
        send_error(client_socket, address)

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
    :param receive_request:
    :return: the request from the client in bytes
    """
    byte, address = receive_request.recvfrom(MAX_UDP_PACKET_SIZE)
    return byte, address


def parse_request(request):
    """
    Gets the request and determines what to do with it
    :param request:
    :return:
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
    :return:
    """
    is_request = True
    if request_line.count(b'\x00') != 3:
        is_request = False
    type = request_line[0: 2]
    if type != b'\x00\x01':
        is_request = False
    return is_request


def send_error(client_socket, address):
    #is_response = b''

    #run = True
    #while run:
    client_socket.sendto(b'\x00\x05\x00\x04\x40sfdsadsfa\x00', address)
        #is_response, address = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)
        #if is_response == b'\x00\x04\x00\x01':
          #  run = False
   # print(is_response)


############################################### JOSIAH


def read_file(file_name, data_socket, address):
    """
    :author: Elisha Hamp
    Takes in a file_name and uses it to create blocks
    :param file_name:
    :return:
    """
    count = get_file_block_count(file_name)+1
    for i in range(1, count):
        block = get_file_block(file_name, i)
        send_block(i, block, data_socket, address)
        wait_for_ack(i, data_socket)


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
    :param number:
    :return:
    """
    data_socket.settimeout(10)
    parse_ack(data_socket.recv(4), b_num)


def parse_ack(ack, b_num):
    """
    :author: Elisha Hamp
    parses the ack
    :param ack:
    :return:
    """
    print(ack[0: 2])


main()
