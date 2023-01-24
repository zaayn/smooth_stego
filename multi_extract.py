from Methods import sampling
from Methods import divide_stego_sample
from Methods import interpolation_linear
from Methods import fuzzifikasi

from Methods import read_info

from Methods import get_diffference
from Methods import get_smoothed_payload
from Methods import extracting
from Methods import process_bit

from Methods import get_payload_cover

def main():
    total_file_payload = 11
    total_file_cover_audio = 15

    for x in range(1, total_file_cover_audio+1):
        for y in range(1, total_file_payload+1):
            stego_audio = 'stego_audio/stego_audio'+ str(x) +'_payload'+ str(y) +'/stegoaudio.wav'
            info_file = 'stego_audio/stego_audio'+ str(x) +'_payload'+ str(y) +'/info.txt'
            extracted_payload = 'extracted/stego_audio'+ str(x) +'_payload'+ str(y) +'/payload.txt'
            extracted_audio = 'extracted/stego_audio'+ str(x) +'_payload'+ str(y) +'/audio.wav'

            # audio process
            freame_rate, stego_audio_sample = sampling(stego_audio)
            original_sample, embedded_sample = divide_stego_sample(stego_audio_sample)
            interpolated_sample = interpolation_linear(original_sample)
            bit = fuzzifikasi(interpolated_sample, original_sample)

            # read file info
            smooth, len_payload, last_bit = read_info(info_file)
            
            # extracting
            differenced = get_diffference(embedded_sample, interpolated_sample, smooth, len_payload)
            smoothed_payload = get_smoothed_payload(differenced, len_payload)
            decimal_payload = extracting(smoothed_payload, smooth, bit)
            converted_payload = process_bit(decimal_payload, bit, last_bit)
            get_payload_cover(converted_payload, extracted_payload,original_sample, extracted_audio)

            print(x, y, "sukses")
    
main()
