"""
CLIENT SIDE CODE
Christopher Kevin Hamdajani
15995114
"""
import socket
import sys
import os.path

def check_header(magic_no, type_no, status_code):
    if magic_no != '0x497e':
        print("[HEADER ERROR] Magic number is not 0x497E")
        return False
    elif type_no != 2:
        print("[HEADER ERROR] Type is wrong")
        return False
    elif status_code != 0:
        if status_code != 1:
            print("[HEADER ERROR] Unknown status code")
            return False
    return True

def create_fixed_header(name_file):
    len_msg = len(name_file.encode('utf-8'))
    magic_no = 18814
    type_no = 1
    header_temp = 0xFFFFFFFFFF
    header_temp = (header_temp & 0x0000FFFFFF) | (magic_no << 24)
    header_temp = (header_temp & 0xFFFF00FFFF) | (type_no << 16)
    header_temp = (header_temp & 0xFFFFFF0000) | (len_msg)
    header_hex = hex(header_temp)[2:]    
    fixed_header_barray = bytearray.fromhex(header_hex)
    return fixed_header_barray

def main():
    state= True
    if (len(sys.argv) != 4):
        print("[PARAMETER ERROR] Only need 3 paramaeters which are IP address, port number, and name of the file")
        state = False
    else:
        if (int(sys.argv[2]) < 1024 or int(sys.argv[2]) > 64000):
            print("[PARAMETER ERROR] The port number that has been entered was not between 1024 and 64000(including)")
            state = False
        elif os.path.isfile(sys.argv[3]):
            state = False
            print('[FILE ERROR] File already exist')
        try:
            addrInfo = socket.getaddrinfo(sys.argv[1], sys.argv[2])
        except:
            print("[PARAMETER ERROR] Failed to identify ip address!")
            state = False
        else:
            ipaddress = addrInfo[0][4][0] 
    if state:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.0)
        except:
            print("[SOCKET ERROR] Failed to create socket")
            sys.exit()
        else:
            #server try to listen
            try:
                address = (ipaddress, int(sys.argv[2]))
                client.connect(address)
            except:
                client.close()
                print("[SOCKET ERROR] Socket failed to connect")
                sys.exit()
        fixed_header_barray = create_fixed_header(sys.argv[3])
        client.send(fixed_header_barray)
        client.send(sys.argv[3].encode('utf-8'))
        #begin recv proces
        try:
            fixed_header = client.recv(8)
        except socket.timeout:
            print("[TIMEOUT ERROR] Exceed 1 second time limit when receiving data")
            client.close()
            sys.exit()
        else:
            if(len(fixed_header) != 0):
                hex_fheader = fixed_header.hex()
                temp_list=[hex_fheader[i:i+2] for i in range(0, len(hex_fheader), 2)]
                magic_no = "0x" + temp_list[0] + temp_list[1]
                type_no = int(temp_list[2])
                status_code = int(temp_list[3])
                data_length = int(temp_list[4]+temp_list[5]+temp_list[6]+temp_list[7], 16)
                header_state = check_header(magic_no, type_no, status_code)
                if header_state:
                    if (status_code == 0):
                        print("[FILE ERROR] The requested file is not available in the server")
                        client.close()
                        sys.exit()
                    else:
                        try:
                            f= open(sys.argv[3], 'wb')
                        except OSerror:
                            print("[FILE ERROR] Unable to open the indicated file")
                            client.close()
                            sys.exit()
                        else:
                            total_bytes = 0
                            total_msg = bytearray()                        
                            while True:
                                try:
                                    msg = client.recv(4096)
                                except socket.timeout:
                                    print("[FILE ERROR] The requested file is not available in the server")
                                    client.close()
                                    sys.exit()
                                else:
                                    if len(msg) == 0:
                                        if(total_bytes != data_length):
                                            print("[FILE ERROR] The received file might be corrupted")
                                            client.close()
                                            sys.exit()
                                        else:
                                            f.write(total_msg)
                                            f.close()
                                            print("[SUCCES] The indicated file( {} of bytes) has been downloaded".format(total_bytes))
                                            client.close()
                                            sys.exit()
                                        break
                                    else:
                                        total_bytes += len(msg)
                                        total_msg.extend(msg)                   
            else:
                print("[ERROR] no data is received")
main()