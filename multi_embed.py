from Methods import read_payload

from Methods import sampling
from Methods import interpolation_linear
from Methods import fuzzifikasi

from Methods import payload_process
from Methods import converting
from Methods import embedding
from Methods import smoothing

from Methods import combine
from Methods import create_stego_audio

def main():
    total_file_payload = 11
    total_file_cover_audio = 15

    folder_file_payload = 'dataset/Payload/'
    folder_file_audio = 'dataset/Audio/'
    folder_stego_audio = 'stego_audio/'
    folder_info = 'stego_audio/'

    for x in range(1, total_file_cover_audio+1):
        for y in range(1, total_file_payload+1):
            
            # init file
            audio_file = folder_file_audio + 'data' + str(x) + '_mono.wav'
            payload_file = folder_file_payload + 'payload' + str(y) + '.txt'
            stego_audio = folder_stego_audio + 'stego_audio' + str(x) + '_payload' + str(y) +'/stegoaudio.wav'
            info_file = folder_info + 'stego_audio' + str(x) + '_payload' + str(y) + '/info.txt'

            #payload process
            binary_payload = read_payload(payload_file)

            #audio process
            freame_rate, original_sample = sampling(audio_file)
            interpolated_sample = interpolation_linear(original_sample)
            bit = fuzzifikasi(interpolated_sample, original_sample)

            #embedding process
            processed_payload, last_bit = payload_process(bit, binary_payload, interpolated_sample)
            decimal_payload = converting(processed_payload)
            embedded = embedding(decimal_payload, interpolated_sample)
            smoothed = smoothing(embedded, interpolated_sample,bit,info_file,processed_payload, last_bit)

            #create output
            stego_data = combine(original_sample, smoothed, interpolated_sample)
            create_stego_audio(stego_data, stego_audio)
            print('Create stego_audio'+ str(x) +'_payload'+ str(y) +'.wav SUKSES')

main()