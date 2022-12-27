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

audio = '1'
payload = '9'
audio_file = 'dataset/Audio/data'+audio+'_mono.wav'
payload_file = 'dataset/Payload/payload'+payload+'.txt'
stego_audio = 'stego_audio/stego_audio'+audio+'_payload'+payload+'/stegoaudio.wav'

#payload process
binary_payload = read_payload(payload_file)

#audio process
freame_rate, original_sample = sampling(audio_file)
interpolated_sample = interpolation_linear(original_sample)
bit = fuzzifikasi(interpolated_sample, original_sample)

#embedding process
processed_payload = payload_process(bit, binary_payload, interpolated_sample)
decimal_payload = converting(processed_payload)
embedded = embedding(decimal_payload, interpolated_sample)
smoothed = smoothing(embedded, interpolated_sample,bit)

#create output
stego_data = combine(original_sample, smoothed, interpolated_sample)
create_stego_audio(stego_data, stego_audio)
print(stego_audio)