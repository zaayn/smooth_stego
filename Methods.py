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
                    bit.append(1)
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
    average_bit = math.floor(math.log(np.mean(bit),2)) # aslinya 6
   
    selisih = [int(interpolated_sample[x]-embedded_sample[x]) for x in range(len(embedded_sample))]
    selisih2 = selisih.copy()
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
            number += 1
        else:
            selisih = div

        if len(smoothed_payload) + len_payload*2 > len(interpolated_sample):
            inLen = False
        number += 1
    smoothed_sample = [int(interpolated_sample[x] - smoothed_payload[x]) for x in range(len(smoothed_payload))]
    
    write_info(number, len_payload, selisih2, info_file)

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

def write_info(number, len_payload, selisih, info_file):
    os.makedirs(os.path.dirname(info_file), exist_ok=True)
    info = open(info_file,"w+")
    info.write(str(number)+'\n')
    info.write(str(len_payload)+'\n')
    info.write(str(selisih))
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

def read_info(info_file):
    file_info = open(info_file, "r")
    count = 1
    for line in file_info:
        if count == 1:
            line1 = format(line.strip())
        if count == 2:
            line2 = format(line.strip())
        if count == 3:
            line3 = format(line.strip())
        count += 1
    file_info.close()
    number = int(line1)
    length = int(line2)
    diff = line3
    return number, length, diff

def get_diffference(embedded_sample, interpolated_sample, smooth, len_payload):
    total_sample = smooth * len_payload
    selisih = [int(interpolated_sample[x] - embedded_sample[x]) for x in range(total_sample)]
    return selisih

def get_smoothed_payload(selisih, length):
    index = 0
    segmented_list_payload = []
    for x in range(len(selisih)):
        if x % length == 0:
            segmented_list_payload.append(selisih[index:index + length])
        index += 1
    # for x in range(len(segmented_list_payload)):
    #     print(segmented_list_payload[x][80:85])
    return segmented_list_payload

def extracting(smoothed_payload, smooth, bit):
    average_bit = math.floor(math.log(np.mean(bit),2))

    while smooth-1 > 0: #jika data ada 9 maka smoothing sebanyak 8 kali
        div = smoothed_payload[-1]
        mod = smoothed_payload[-2]
        tmp = [(div[x] * average_bit) + mod[x] for x in range(len(div))]
        
        del smoothed_payload[-1]
        smoothed_payload[-1] = tmp
        smooth -= 1
    smoothed_payload = smoothed_payload[0]
    return smoothed_payload

def process_bit(desimal,bit):
    payload = []
    for x in range(len(desimal)):
        if bit[x] != 0:
            
            if x == len(desimal)-1:
                payload.append(np.binary_repr(int(desimal[x])))
            else:
                payload.append(np.binary_repr(int(desimal[x]),width=bit[x]))
                # if len(np.binary_repr(int(desimal[x]),width=bit[x])) != bit[x]:
                #     print(desimal[x], np.binary_repr(int(desimal[x]),width=bit[x]), bit[x], x)

    translated_payload = ''.join(payload)
    translated_payload = '\t'.join(translated_payload)
    return translated_payload

def get_payload_cover(byte_payload, payload_path, original_sample, audio_path):
    os.makedirs(os.path.dirname(payload_path),exist_ok=True)
    with open(payload_path, 'w+') as file:
        file.write(byte_payload)
        file.close()

    unnormalize_data = np.subtract(original_sample,[32768])
    new_data_sample = np.array(unnormalize_data,dtype=np.int16)
    os.makedirs(os.path.dirname(audio_path),exist_ok=True)
    scp.write(audio_path, 44100, new_data_sample)

############################################# Testing #############################################
def decimal_payload_check(embedding_distance, extracted_distance):
    # preprocessing
    embedding_distance = embedding_distance[1:]
    embedding_distance = embedding_distance[:-1]
    embedding_distance = embedding_distance.split(", ")
    embedding_distance = [int(x) for x in embedding_distance]
    
    error = False
    if len(embedding_distance) != len(extracted_distance):
        print("length embedding distance = ", len(embedding_distance))
        print("length extracted distance = ", len(extracted_distance))
        error = True
    else:
        for x in range(len(embedding_distance)):
            if embedding_distance[x] != extracted_distance[x]:
                print("index = ", x)
                print("embedding distance ", embedding_distance[x], type(embedding_distance[x]))
                print("extracted distance ", extracted_distance[x], type(extracted_distance[x]))
                error = True
    print(error)


