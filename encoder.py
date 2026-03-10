#! /usr/bin/env python
"""
This is a simple app that uses 1-byte variation selectors (16 code point)
and supplemental selectors (240 points) to encode messages into an
emoji. Since the variation selectors are invisible and do not alter the looks
of an emoji, it can then be used to smuggle messages out through an emoji
"""

def byte_to_variation_selector(byte):
    # Map any decimal 16 or below characters to variation selectors
    if byte < 16:
        return chr(0xFE00 + byte)
    # Map decimal 17 and above characters to supplemental selectors
    else:
        return chr(0xE0100 + (byte - 16))

def encode(base_emoji, message):
    bytes_data = message.encode('utf-8')
    result = base_emoji
    for byte in bytes_data:
        result += byte_to_variation_selector(byte)
    return result

def variation_selector_to_byte(char):
    code = ord(char)
    if 0xFE00 <= code <= 0xFE0F:
        return code - 0xFE00
    elif 0xE0100 <= code <= 0xE01EF:
        return (code - 0xE0100) + 16
    return None

def decode(encoded_str):
    bytes_data = []
    started = False
    for char in encoded_str:
        byte = variation_selector_to_byte(char)
        if byte is not None:
            bytes_data.append(byte)
            started = True
        elif started:
            break
    return bytes(bytes_data).decode('utf-8')


def embed_with_zero_width_chars(secret_message: str, cover_text: str) -> str:
    """
    Uses unicode control character encoding to encode binary.
    """
    # Convert the secret message to a binary string
    binary_message = ''.join(
        format(ord(char), '08b') for char in secret_message
    )

    # 2. Map binary digits to zero-width characters
    ZWNJ = '\u200c'  # Zero Width Non-Joiner (Represents '0')
    ZWSP = '\u200b'  # Zero Width Space (Represents '1')

    invisible_payload = binary_message.replace('0', ZWNJ).replace('1', ZWSP)

    # 3. Embed the payload in the backend of the cover text
    embedded_text = cover_text + " " + invisible_payload

    return embedded_text


def embed_with_tag_chars(secret_message: str, cover_text: str) -> str:
    """
    Encodes a secret message into Unicode Tag characters (U+E0000 to U+E007F).
    """
    # Start of the Tag Block range
    TAG_START = 0xE0000

    tag_payload = ""
    for char in secret_message:
        # Get the ASCII value and offset it into the Tag Block range
        # We only use the lower 127 ASCII values to fit within the block
        ascii_val = ord(char)
        if 0 < ascii_val < 128:
            tag_char = chr(TAG_START + ascii_val)
            tag_payload += tag_char
        else:
            print(f"Warning: Skipping character '{char}' (outside basic ASCII range).")

    # Embed the payload at the end of the cover text
    embedded_text = cover_text + tag_payload + "END"

    return embedded_text


def main():
    print(" ______                 _____  \n"         
          "| ____|                |  __ \\   \n"      
          "| |__   _ __ ___   ___ | |__) | __ ___\n"  
          "|  __| | '_ ` _ \\ / _ \\|  ___/ '__/ _ \\\n" 
          "|-|____|-| |-| |-| (_)-|-|   |-| |-(_)-|\n"
          "|======|=| |=| |=|\\===/|=|   |=|  \\===/ \n"
          "")
    print("\n=😇 EMOJI MESSAGE ENCODER, BREAKING LLMS, ONE SMILEY FACE AT A TIME 😇=")
    # Base emoji selection
    emoji_selection = {"1": "😊",
                       "2": "😂",
                       "3": "😑",
                       "4": "😭",
                       "5": "💩",
                       "6": "🤪",
                       "7": "😰",
                       "8": "😘"}
    for key in emoji_selection.keys():
        print(f"{key}\t{emoji_selection[key]}")
    emoji_num = ""
    while emoji_num not in emoji_selection.keys():
        emoji_num = input("\nPlease select an emoji number to use for encoding: ")

    emoji = emoji_selection[emoji_num]
    message = input("Please provide a message to be encoded in the emoji: ")
    mode = ""
    while mode.upper() not in ('Y', 'N'):
        mode = input("Would you like to use the ASCII tag encoding method? [Y/N]: ")
    if mode.upper() == 'N':
        encoded = encode(base_emoji=emoji, message=message)
    else:
        encoded = embed_with_tag_chars(secret_message=message, cover_text=emoji)
    print(f"Encoded emoji for {emoji}) is: {encoded}")
    if mode == 'N':
        print(f"Decoded emoji text is {decode(encoded)}")


if __name__ == '__main__':
    main()
