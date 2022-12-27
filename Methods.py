import scipy.io.wavfile as scp
import numpy as np
import math
import copy
import os

def read_payload(file_payload):
    binary_data = list(open(file_payload))[0]
    binary_data = binary_data.split('\t')
    binary_data = [x.strip('ÿþ') for x in binary_data]

    binary_data = [x.strip('\x00') for x in binary_data]
    binary_data = ''.join(binary_data)
    return binary_data

def sampling(file_audio):
    rate, data = scp.read(file_audio)
    data = np.add(np.int16(data),[32768])
    return rate, data

def interpolation_linear(input_sampling):
    index_odd = [x for x in range (0, (len(input_sampling)*2) - 1) if x%2 == 1]
    index_even = [x for x in range (0, (len(input_sampling)*2)) if x%2 == 0]
    interpolated_sample = np.interp(index_odd, index_even, input_sampling)
    interpolated_sample = np.floor(interpolated_sample)
    return interpolated_sample

def fuzzifikasi(interpolated_sample, original_sample):
    data = [0,16384,32768,49152,65536]
    bit = []
    for x in range (len(interpolated_sample)):
        for y in range(1, len(data)):
            if(data[y-1] <= interpolated_sample[x] < data[y]):
                up = (data[y] - interpolated_sample[x])/(data[y]-data[y-1])
                low = 1 - up

                selisih_up = abs(interpolated_sample[x] - original_sample[x+1])
                selisih_down = abs(interpolated_sample[x] - original_sample[x])

                total = math.floor((up * selisih_up) + (low * selisih_down))
                if total == 0:
                    bit.append(0)
                else:
                    bit.append(math.floor(math.log(total,2)))

    return bit

def payload_process(bit, binary_payload, interpolated_sample):
    index = 0
    processed_payload = []

    for x in bit:
        if(index < len(binary_payload)):
            processed_payload.append(binary_payload[index:index+x])
            index += x
    
    return processed_payload

def converting(data_binary):
    data_decimal = [int(data_binary[x],2) if data_binary[x]!='X' and data_binary[x]!='' else 0 for x in range (len(data_binary))]
    return data_decimal

def embedding(payload_decimal, interpolated_sample):
    embedded = []
    for x in range (len(payload_decimal)):
        embedded.append(interpolated_sample[x] - payload_decimal[x])
    return embedded

def smoothing(embedded_sample, interpolated_sample, bit, info_file):
    average_bit = 2 # aslinya 6
    # print(average_bit)
   
    selisih = [int(interpolated_sample[x]-embedded_sample[x]) for x in range(len(embedded_sample))]
    len_payload = len(selisih) #panjang payload

    smoothed_payload = []
    number = 0
    flag = True
    inLen = True

    while flag == True and inLen == True:
        mod, div, flag = get_div_mod(selisih, average_bit)
        smoothed_payload = np.append(smoothed_payload, mod)
        if flag == False:
            smoothed_payload = np.append(smoothed_payload, div)
        else:
            selisih = div

        if len(smoothed_payload) + len_payload*2 > len(interpolated_sample):
            inLen = False

        number += 1

    smoothed_sample = [(interpolated_sample[x] - smoothed_payload[x]) for x in range(len(smoothed_payload))]
    
    write_info(number, len_payload, info_file)

    return smoothed_sample

def get_div_mod(selisih, average_bit):
    mod = [int(selisih[x]%average_bit) for x in range(len(selisih))]
    div = [math.floor(selisih[x]/average_bit) for x in range(len(selisih))]

    flag = False
    for x in div:
        if x > average_bit:
            flag = True
            break
    return mod, div, flag

def write_info(number, len_payload, info_file):
    os.makedirs(os.path.dirname(info_file), exist_ok=True)
    info = open(info_file,"w+")
    info.write(str(number)+'\n')
    info.write(str(len_payload))
    info.close()

def combine(input_sampling, embed_data, data_interpolation):
    new_embed_data = [embed_data[x] if x < len(embed_data) else data_interpolation[x] for x in range (len(data_interpolation))]
    stego_data = []
    index_stego = 0
    index_sample = 0
    index_embed = 0

    for x in range (0, len(input_sampling)*2 - 1):
        if (index_stego % 2 == 0):
            stego_data.append(input_sampling[index_sample])
            index_sample += 1
        else:
            stego_data.append(new_embed_data[index_embed])
            index_embed += 1
        index_stego += 1

    return stego_data

def create_stego_audio(stego_data, filepath):
    process_1 = np.subtract(stego_data, [32768])
    stego_audio = np.array(process_1, dtype=np.int16)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    scp.write(filepath, 88200, stego_audio)

############################################# Extract #############################################

def divide_stego_sample(data):
    cover_audio_data = [data[x] for x in range (len(data)) if x % 2 == 0]
    stego_audio_data = [data[x] for x in range (len(data)) if x % 2 == 1]
    return cover_audio_data, stego_audio_data

