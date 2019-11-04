import cchardet


def convert_encoding(data: bytes, new_coding: str = 'UTF-8') -> bytes:
    encoding = cchardet.detect(data)['encoding']
    decoded_data = data.decode(encoding, data)
    if new_coding.upper() != encoding.upper():
        decoded_data = data.decode(encoding, data).encode(new_coding)
    return decoded_data


def convert_decoding(data: bytes) -> str:
    encoding = cchardet.detect(data)['encoding']
    decoded_data = data.decode(encoding, data)
    return decoded_data