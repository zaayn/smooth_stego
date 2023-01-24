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

from Methods import decimal_payload_check

def main():
    audio = '9'
    payload = '7'

    # init file
    stego_audio = 'stego_audio/stego_audio'+audio+'_payload'+payload+'/stegoaudio.wav'
    info_file = 'stego_audio/stego_audio'+audio+'_payload'+payload+'/info.txt'
    extracted_payload = 'extracted/stego_audio'+audio+'_payload'+payload+'/payload.txt'
    extracted_audio = 'extracted/stego_audio'+audio+'_payload'+payload+'/audio.wav'

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

    # testing
    result = decimal_payload_check(diff, decimal_payload, payload, segmented_payload, bit)


main()