"""
SERVER SIDE CODE
Christopher Kevin Hamdajani
15995114
"""
import socket
import sys
import datetime
import os.path
SERVER = socket.gethostbyname(socket.gethostname())
def check_port(port_num):
    #check if port_num is in range between 1024 and 64000(including)
    if port_num < 1024 or port_num > 64000:
        return False
    return True

def create_file_response(status_code, filename = None):
    magic_no = 18814
    type_no = 2
    data_length = None
    if status_code == 0:
        data_length = 0
        header_temp = 0xFFFFFFFFFFFFFFFF
        header_temp = (header_temp & 0x0000FFFFFFFFFFFF) | (magic_no << 48)
        header_temp = (header_temp & 0xFFFF00FFFFFFFFFF) | (type_no << 40)
        header_temp = (header_temp & 0xFFFFFF00FFFFFFFF) | (status_code << 32)
        header_temp = (header_temp & 0xFFFFFFFF00000000) | (data_length)
        header_hex = hex(header_temp)[2:]
        fixed_header_barray = bytearray.fromhex(header_hex)
        return fixed_header_barray
    else:
        filedata = bytearray()
        try:
            with open(filename, "rb") as f:
                byte = f.read()
            filedata.extend(byte)
        except IOError:
            print('Error While Opening the file!')        
        data_length = len(filedata)
        header_temp = 0xFFFFFFFFFFFFFFFF
        header_temp = (header_temp & 0x0000FFFFFFFFFFFF) | (magic_no << 48)
        header_temp = (header_temp & 0xFFFF00FFFFFFFFFF) | (type_no << 40)
        header_temp = (header_temp & 0xFFFFFF00FFFFFFFF) | (status_code << 32)
        header_temp = (header_temp & 0xFFFFFFFF00000000) | (data_length)
        header_hex = hex(header_temp)[2:]
        fixed_header_barray = bytearray.fromhex(header_hex)
        full_barray = fixed_header_barray+(filedata)
        print("[FILE SENT] Actual number of bytes transfered :", len(full_barray))
        return full_barray

def check_header(magic_no, type_no, filenamelen):
    if magic_no != '0x497e':
        print("[HEADER ERROR] Magic number is not 0x497E")
        return False
    elif type_no != 1:
        print("[HEADER ERROR] type is wrong")
        return False
    elif filenamelen < 1 or filenamelen > 1024:
        print("[HEADER ERROR] The length of filename is not between between 1 and 1024(including)")
        return False
    return True

def logging(addr):
    ip, port = addr
    print("[INCOMING CONNECTION]")
    print("Current time : ", datetime.datetime.now())
    print("IP address : ", ip)
    print("Port number : ", port)
    
def main():
    port_num = int(sys.argv[1])
    connected = True
    if check_port(port_num):
        #create socket
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (SERVER, port_num)
        #server try to bind
        try:
            new_socket.bind(address)
        except:
            conected = False
            print("[BINDING ERROR] Failed to bind!")
            sys.exit()
        else:
            #server try to listen
            try:
                new_socket.listen()
            except:
                conected = False
                print("[LISTEN ERROR] Failed to listen")
                new_socket.close()
                sys.exit()
        if connected:
            print("[SERVER LISTENING] server is running on ", SERVER, " on port ", port_num)
        while connected:
            conn, addr = new_socket.accept()
            logging(addr)
            conn.settimeout(1.0)
            state_timeout = True           
            try:
                file_request = conn.recv(2048)
            except socket.timeout:
                state_timeout = False
                print("[TIMEOUT ERROR] Exceed 1 second time limit when receiving data")
            fixed_header = file_request[:5]
            hex_fheader = fixed_header.hex()
            temp_list=[hex_fheader[i:i+2] for i in range(0, len(hex_fheader), 2)]
            magic_no = "0x" + temp_list[0] + temp_list[1]
            type_no = int(temp_list[2])
            filenamelen = int('0x'+ temp_list[3] + temp_list[4], 16)
            header_state = check_header(magic_no, type_no, filenamelen)
            if header_state == False or state_timeout == False:
                conn.close()
            else:
                filename = file_request[5:].decode('utf-8')
                if os.path.isfile(filename):
                    try:
                        infile = open(filename)
                        infile.close()
                    except OSerror:
                        print("[FILE ERROR] Cannot open the file")
                        response_barray = create_file_response(0)
                        conn.send(response_barray)                        
                        conn.close()
                    else:
                        response_barray = create_file_response(1, filename)
                        conn.send(response_barray)
                        conn.close()                    
                else:
                    response_barray = create_file_response(0)
                    conn.send(response_barray)
                    conn.close()
                    print("[FILE NOT FOUND] The file requested is not available!")  
    else:
        print("[PORT NUMBER ERROR] The port number that has been entered was not between 1024 and 64000(including)")
        sys.exit()
        
        
main()