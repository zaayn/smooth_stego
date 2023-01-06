import scipy.io.wavfile
import numpy as np
import os

def sampling_audio(fileaudio):
    rate, data = scipy.io.wavfile.read(fileaudio)
    data = np.array(data,dtype=np.int16)
    nilaimax=[32768]
    data=np.add(data,nilaimax)
    return data

def read_number_data(file):
    test = np.loadtxt(file,dtype=np.int)
    return test

def compare_data(data1, data2):
    hasil = 1
    if len(data1) != len(data2):
        print('panjang data1 = ', len(data1))
        print('panjang data2 = ', len(data2))
        return 0
    else:
        miss_data = 0
        for x in range (len(data1)):
            if data1[x] != data2[x]:
                print('miss pada index : ', x)
                print('data1 = ', data1[x], '| data2 = ', data2[x])
                miss_data += 1
                hasil = 0
    return hasil


def main():
    total_file_payload = 11
    total_file_cover_audio = 15
    for x in range(1,total_file_cover_audio+1):
        for y in range(1,total_file_payload+1):

            original_audio = 'dataset/Audio/data'+str(x)+'_mono.wav'
            extract_audio = 'extracted/stego_audio' + str(x) + '_payload' + str(y) + '/audio.wav'

            original_sample = sampling_audio(original_audio)
            extracted_sample = sampling_audio(extract_audio)

            hasil_audio = compare_data(original_sample, extracted_sample)

            if hasil_audio == 0:
                print('Extracted Audio dari Stego_audio'+str(x)+'_payload'+str(y)+'.wav GAGAL di Ekstraksi')
                return
            else:
                print('Extracted Audio dari Stego_audio'+str(x)+'_payload'+str(y)+'.wav SUKSES diekstraksi')
                print("-------------------------------------------------------------------------")


main()