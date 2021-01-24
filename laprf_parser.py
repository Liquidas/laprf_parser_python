run_one_time = 0
max_loop_cycles = 100
is_terminal_cmd = 0
good_msg_rx_log = 0
bad_msg_rx_log = 1

from os import system, name
print("##################################################################################################################################################################")
print("------------------------------------------------------------------------------------------------------------------------------------------------------------------")
print("##################################################################################################################################################################")
print("")

if is_terminal_cmd == 1:
    def clear(): #clean cmd window
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = system('clear') 
    clear()

import socket #for TCP connection to laprf
import struct #for bytes object to float
import time #for pause
#import numpy as np #for crc16 calculation

if bad_msg_rx_log == 1:
    text_bad = open(r"bad_messages.txt","w")
if good_msg_rx_log == 1:
    text_good = open(r"good_messages.txt","w")



sor = bytes([0x5a]) #start of message
eor = bytes([0x5b]) #end of message
esc = bytes([0x5c]) #po sitos reiksmes sekanciam simboliui darom - 0x40
#types of messages
type_rf_settings = bytes([0x02, 0xda])
type_detection = bytes([0x09, 0xda])
type_status = bytes([0x0a, 0xda])
type_settings = bytes([0x07, 0xda])
type_descriptor = bytes([0x08, 0xda])
#common
subtype_pilot_id = bytes([0x01])
subtype_rtc_time = bytes([0x02])
subtype_status_flags = bytes([0x03])
#rf_settings SENT/RECEIVED BY LAPRF
subtype_rf_settings_enable = bytes([0x20])
subtype_rf_settings_channel = bytes([0x21])
subtype_rf_settings_band = bytes([0x22])
subtype_rf_settings_threshold = bytes([0x23])
subtype_rf_settings_gain = bytes([0x24])
subtype_rf_settings_frequency = bytes([0x25])
#detections SENT BY LAPRF
subtype_decoder_id = bytes([0x20])
subtype_detection_no = bytes([0x21])
subtype_detection_peak_height = bytes([0x22])
subtype_detection_flags = bytes([0x23])
#status SENT BY LAPRF
subtype_status_input_voltage = bytes([0x21])
subtype_status_rssi = bytes([0x22])
subtype_status_gate_state = bytes([0x23])
subtype_status_count = bytes([0x24])
#settings SENT BY LAPRF
subtype_settings_name = bytes([0x20])
subtype_settings_status_update_period_ms = bytes([0x22])
subtype_settings_save_settings = bytes([0x25])
subtype_settings_min_lap = bytes([0x26])
subtype_settings_module_enabled = bytes([0x27])
#descriptor SENT BY LAPRF
subtype_puck_version = bytes([0x20])
subtype_protocol_version = bytes([0x21])
#integer variables
#crc_poly = 32773 #0x8005
#crc_poly = np.uint16(0x8005)
#crc_poly = 0x8005
#msg_rx = bytearray(1024)
bad_msg_rx = 0
good_msg_rx = 0
input_voltage = 0
rtc_hrs = 0
rtc_min = 0
rtc_sec = 0
rssi = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
gate_state = 0
detection_count = 0
pilot = 0
settings_enable = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
settings_channel = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
settings_band = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
settings_threshold = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
settings_gain = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
settings_frequency = [0, 0, 0, 0, 0, 0, 0, 0] #8 pilots max
msg_rx_crc = bytes([0x00, 0x00])
#start byte
#lrf_start = bytes([0x5a, 0x61])
msg_rx_end = 0
msg_rx_end_raw = 0
start_look_for_end = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.1.10', 5403))
msg_tx = bytearray([
    0x5a,#start byte
    0x0b,#msg length
    0x00,#
    0x00,#crc
    0x00,#crc
    0x02,#message ID
    0xda,#message ID
    0x00,#subtype
    0x00,#byte count
    0x00,#pilot no
    0x5b
])

test_ask_for_settings1 = bytes([
    0x5a,
    0x0b,
    0x00,
    0x19,
    0x5c,
    0x9a,
    0x02,
    0xda,
    0x01,
    0x01,
    0x01,
    0x5b
])

test_ask_for_settings2 = bytes([
    0x5a,
    0x0b,
    0x00,
    0x19,
    0xaa,
    0x02,
    0xda,
    0x01,
    0x01,
    0x02,
    0x5b
])

def init_msg_tx():
    global msg_tx
    msg_tx = bytearray([
        0x5a,#start byte
        0x0b,#msg length
        0x00,#
        0x00,#crc
        0x00,#crc
        0x00,#message ID
        0xda,#message ID
        0x00,#subtype
        0x00,#byte count
        0x00,#pilot no
        0x5b
    ])

def ask_rf_settings():
    init_msg_tx()
    msg_tx[5] = 0x02
    msg_tx[7] = 0x01
    msg_tx[8] = 0x01
    for i in range(1, 9):
        msg_tx[9] = i

def find_esc_symbols(data: bytes):
    global start_look_for_end
    data_out = bytearray(data)
    j = 0
    tmpEnd = msg_rx_end_raw
    while j < tmpEnd:
        if data_out[j:j+1] == esc:
            data_out.pop(j)
            data_out[j:j+1] = (int.from_bytes(data_out[j:j+1], byteorder='little', signed=False)-0x40).to_bytes(1, byteorder='little', signed=False)
            #j += 1 #used in case there is two 5c bytes
            start_look_for_end = j+1
            tmpEnd -= 1
        j += 1
    return bytes(data_out)

def crc16(data, length):
    ###CRC-16/ARC###
    crc = 0x0000
    for i in (range(0, length)):
        crc ^= data[i]
        for j in range(0, 8):
            if (crc & 0x0001) > 0:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = crc >> 1
    return crc

def find_msg_rx_type(data: bytes):
    if data[0:2] == type_rf_settings[0:2]:
        return "type_rf_settings"
    elif data[0:2] == type_detection[0:2]:
        return "type_detection"
    elif data[0:2] == type_status[0:2]:
        return "type_status"
    elif data[0:2] == type_settings[0:2]:
        return "type_settings"
    elif data[0:2] == type_descriptor[0:2]:
        return "type_descriptor"
    else:
        return "parse error"

def find_status():
    global pilot
    if msg_rx_subtype == subtype_status_input_voltage:
        input_voltage = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little') / 1000
        print("input_voltage: ", input_voltage)
    #elif msg_rx_subtype == subtype_rtc_time:
        #timestamp, microseconds since startup
    elif msg_rx_subtype == subtype_pilot_id:
        pilot = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little') - 1
        print("pilot: ", pilot)
    elif msg_rx_subtype == subtype_status_rssi:
        #approx. 950 for no signal, ~3500 for max. signal
        rssi[pilot] = struct.unpack('f', msg_rx_content[0:tmpIndex])
        print("rssi: ", rssi[pilot])
    elif msg_rx_subtype == subtype_status_gate_state:
        gate_state = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("gate_state: ", gate_state)
    elif msg_rx_subtype == subtype_status_count:
        #number of detections (use to detect a communications lapse)
        detection_count = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("detection_count: ", detection_count)
    elif msg_rx_subtype == subtype_status_flags:
        #status of puck
        #might need fixing, because status should be short
        status = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("status: ", status)

def find_rf_settings():
    global pilot
    if msg_rx_subtype == subtype_pilot_id:
        pilot = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little') - 1
        print("pilot: ", pilot)
    elif msg_rx_subtype == subtype_rf_settings_enable:
        settings_enable[pilot] = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("settings_enable: ", settings_enable[pilot])
    elif msg_rx_subtype == subtype_rf_settings_channel:
        settings_channel[pilot] = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("settings_channel: ", settings_channel[pilot])
    elif msg_rx_subtype == subtype_rf_settings_band:
        settings_band[pilot] = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("settings_band: ", settings_band[pilot])
    elif msg_rx_subtype == subtype_rf_settings_threshold:
        settings_threshold[pilot] = struct.unpack('f', msg_rx_content[0:tmpIndex])
        print("settings_threshold: ", settings_threshold[pilot])
    elif msg_rx_subtype == subtype_rf_settings_gain:
        settings_gain[pilot] = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("settings_gain: ", settings_gain[pilot])
    elif msg_rx_subtype == subtype_rf_settings_frequency:
        settings_frequency[pilot] = int.from_bytes(msg_rx_content[0:tmpIndex], byteorder='little')
        print("settings_frequency: ", settings_frequency[pilot])

def decode_msg_rx():
    global msg_rx_end_raw
    global good_msg_rx
    global bad_msg_rx
    global msg_rx_subtype
    global msg_rx_content
    global tmpIndex

    start0 = bytearray(msg_rx_raw).find(sor)
    if start0 >= 0:
        msg_rx_end_raw = bytearray(msg_rx_raw).rfind(eor) + 1 #rfind finds last occurance of eor
        #Look for esc symbols
        msg_rx = find_esc_symbols(msg_rx_raw)

        start0 = bytearray(msg_rx_raw).find(sor)
        start3 = start0 + 3
        start4 = start0 + 4
        start5 = start0 + 5
        start7 = start0 + 7
        msg_rx_crc = msg_rx[start3:start5]
        print("CRC: ", msg_rx_crc)

        msg_rx_end = bytearray(msg_rx).find(eor, start_look_for_end) + 1

        msg_rx_to_be_CRC = bytearray(msg_rx)
        msg_rx_to_be_CRC[start3:start4] = bytes([0x00])
        msg_rx_to_be_CRC[start4:start5] = bytes([0x00])
        msg_rx_to_be_CRC = bytes(msg_rx_to_be_CRC)
        msg_rx_crc_calculated = (crc16(msg_rx_to_be_CRC, msg_rx_end)).to_bytes(2, byteorder='little')
        print("calculated CRC: ", msg_rx_crc_calculated)

        if msg_rx_crc == msg_rx_crc_calculated:
            good_msg_rx += 1
            msg_rx_type_b = msg_rx[start5:start7]
            msg_rx_type = find_msg_rx_type(msg_rx_type_b)
            print("Type of packet: ", msg_rx_type)
            print("")
            print("msg_rx_raw: ", msg_rx_raw)
            print("")
            print("msg_rx: ", msg_rx)
            print("")
            i0 = start7
            i1 = i0 + 1
            i2 = i0 + 2

            while msg_rx[i0:i1] != eor:
                msg_rx_subtype = msg_rx[i0:i1]
                msg_rx_byte_count = msg_rx[i1:i2]
                tmpIndex = int.from_bytes(msg_rx_byte_count, byteorder='little')
                msg_rx_content = msg_rx[i2:i2+tmpIndex]

                if msg_rx_type == "type_status":
                    find_status()
                elif msg_rx_type == "type_rf_settings":
                    find_rf_settings()
                
                i0 = i2+tmpIndex
                i1 = i0 + 1
                i2 = i0 + 2

                if i0 > 110:
                    print("Error in while loop")
                    break
            if good_msg_rx_log == 1:
                text_good.write(msg_rx.hex())
                text_good.write("\n")
        else:
            bad_msg_rx += 1
            print("Bad message")
            if bad_msg_rx_log == 1:
                text_bad.write("msg_rx_raw: ")
                print("msg_rx_raw: ")
                j = 0
                while j < msg_rx_end_raw:
                    text_bad.write(msg_rx_raw[j:j+1].hex())
                    text_bad.write(",")
                    text_bad.write("\n")
                    print(msg_rx_raw[j:j+1].hex())
                    j += 1
                text_bad.write("msg_rx: ")
                print("msg_rx: ")
                j = 0
                while j < msg_rx_end:
                    text_bad.write(msg_rx[j:j+1].hex())
                    text_bad.write(",")
                    text_bad.write("\n")
                    print(msg_rx[j:j+1].hex())
                    j += 1
                abc = 1
    print("")
    print("Good messages received: ", good_msg_rx)
    print("Bad messages received: ", bad_msg_rx)
    print("End of message parsing")
    print("")

if run_one_time == 1:
    i = max_loop_cycles
else:
    i = 0

#MAIN LOOP
while i <= max_loop_cycles:
    #s.send(test_ask)
    msg_rx_raw = s.recv(1024)
    
    if is_terminal_cmd == 1:
        clear()
    
    decode_msg_rx()
    
    i += 1
    
print('Python Done')
abc = 1