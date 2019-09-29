# _________________________FUNCTIONS_______________________________
def swap_bit(bit):
    bit ^= 1
    return bit


def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'


def partiy_calculation(byte, bits_nums_to_parry):
    number_of_ones = 0
    for bit_num in bits_nums_to_parry:
        number_of_ones += int(byte[bit_num - 1])
    if number_of_ones % 2 == 0:
        return 1
    else:
        return 0


def convert_to_error_check_type(bits):
    splitted_bits = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    for index, byte in enumerate(splitted_bits):
        c1 = partiy_calculation(byte, [1, 2, 4, 5, 7])
        c2 = partiy_calculation(byte, [1, 3, 4, 6, 7])
        c4 = partiy_calculation(byte, [2, 3, 4, 8])
        c8 = partiy_calculation(byte, [5, 6, 7, 8])
        splitted_bits[index] = str(c1) + str(c2) + byte[:1] + str(c4) + byte[1:4] + str(c8) + byte[4:8]

    return splitted_bits


def check_and_fix_converted_bits(listed_bits):
    for index, byte in enumerate(listed_bits):
        error_sum = 0
        c1_original = int(byte[0])
        c2_original = int(byte[1])
        c4_original = int(byte[3])
        c8_original = int(byte[7])
        c1_to_compare = partiy_calculation(byte, [3, 5, 7, 9, 11])
        c2_to_compare = partiy_calculation(byte, [3, 6, 7, 10, 11])
        c4_to_compare = partiy_calculation(byte, [5, 6, 7, 12])
        c8_to_comapre = partiy_calculation(byte, [9, 10, 11, 12])
        if c1_original != c1_to_compare:
            error_sum += 1
        if c2_original != c2_to_compare:
            error_sum += 2
        if c4_original != c4_to_compare:
            error_sum += 4
        if c8_original != c8_to_comapre:
            error_sum += 8
        if error_sum == 0:
            print("no mistakes for byte: " + byte)
        else:
            print("mistake in byte: " + byte)
            if error_sum <= 12:
                print("fixinig mistake for current byte")
                try:
                    current_byte = list(listed_bits[index])
                    current_byte[error_sum - 1] = str(swap_bit(int(current_byte[error_sum - 1])))
                    listed_bits[index] = "".join(current_byte)
                    print("byte was fixed!")
                except Exception as e:
                    print("byte wasn't fixed - " + e)

            else:
                print("too many mistakes, can't fix dat")
                listed_bits[index] = "????????????"

    return listed_bits


def retrieve_original_bits(checked_bits):
    for index, byte in enumerate(checked_bits):
        if byte == "????????????":
            checked_bits[index] = "00111111"  # if cant restore byte then it transforms to ? char
        else:
            checked_bits[index] = byte[2] + byte[4:7] + byte[8:12]

    checked_bits = ''.join(checked_bits)
    return checked_bits


def emulate_transmission(src_file_path, dst_file_path, fixable_errors, not_fixable_errors):
    with open(src_file_path) as f:
        data = f.read().replace('\n', '')

    if len(data) % 2 != 0:
        data += " "

    # first we convert file context to bits
    bits_from_file = text_to_bits(data)
    # then convert to 12-bit per char format
    check_format = convert_to_error_check_type(bits_from_file)
    # below is the stage where transformed data is being translated to the receiver for example

    # then we check and fix(if we can) mistakes
    if not_fixable_errors:  # if not fixable let's assume one byte was completely transformed into zeros
        for index, byte in enumerate(check_format):
            if index == 0:
                check_format[0] = "000000000000"
    if fixable_errors:  # if fixable let's assume last bit was reversed
        for index, byte in enumerate(check_format):
            if index == 0:
                bit_to_change = check_format[0][-1:]
                check_format[0] = check_format[0][:-1] + str(swap_bit(int(bit_to_change)))

    checked_format = check_and_fix_converted_bits(check_format)
    # let's retrieve original bits
    restore_orig_bits = retrieve_original_bits(checked_format)
    # and finally convert to text again and write to dest
    text_to_write = text_from_bits(restore_orig_bits)
    dst_file = open(dst_file_path, 'w')
    dst_file.write(text_to_write)


# _________________________FUNCTIONS_______________________________


# uncomment one at a time to see expected behaviour

# WITHOUT MISTAKES
# emulate_transmission("testFiles_src/src_test.txt", "testFiles_dst/dst_tst.txt", False, False)

# WITH FIXABLE MISTAKES
# emulate_transmission("testFiles_src/src_test.txt", "testFiles_dst/dst_tst.txt", True, False)

# WITH UNFIXABLE MISTAKES
# emulate_transmission("testFiles_src/src_test.txt", "testFiles_dst/dst_tst.txt", False, True)
