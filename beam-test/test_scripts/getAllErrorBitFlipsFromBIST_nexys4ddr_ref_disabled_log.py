
import re
import argparse
import os
import logging
import traceback



SDRAM_REFRESH_TEST_STR = "sdram_refresh_set {refresh_rate}"
SDRAM_REFRESH_RESET_STR = "sdram_refresh_set 586"
SDRAM_PATTERN_REGEX_ZEROS_STR = "sdram_bist_pat 0x00000000"
SDRAM_PATTERN_REGEX_ONES_STR = "sdram_bist_pat 0xffffffff"
ADDR_DATA_STR = "ADDRESS    DATA"
ZEROS_REF_STR = "zeros"
ONES_REF_STR = "ones"
REGEX_ERROR_STR = "0x0[0-9a-f]{6}:  [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f]"
LEN_DATA_VAL_EXPECTED = 18
HASHTAG_STR = "###"
LOWEST_RFSH_RATE = 586
NINTH_INDEX = 9
RFSH_RATE_NUM_INDEX = 0
REFRESH_RATE_TESTED = 0
BEG_RANK_NUM = 17
RFSH_RATE_RANK_INDEX = 3
RFSH_RATE_TESTTYPE_INDEX = 2



# ERROR Checking char constants
ASCII_VAL_LOWER_A = 97
ASCII_VAL_LOWER_B = 98
ASCII_VAL_LOWER_C = 99
ASCII_VAL_LOWER_D = 100
ASCII_VAL_LOWER_E = 101
ASCII_VAL_LOWER_F = 102
ASCII_ZERO_COMPARISON  = 48
ASCII_ONE_COMPARISON   = 49
ASCII_TW0_COMPARISON   = 50
ASCII_THREE_COMPARISON = 51
ASCII_FOUR_COMPARISON  = 52
ASCII_FIVE_COMPARISON  = 53
ASCII_SIX_COMPARISON   = 54
ASCII_SEVEN_COMPARISON = 55
ASCII_EIGHT_COMPARISON = 56
ASCII_NINE_COMPARISON  = 57
ASCII_SPACE_COMPARISON = 32



def err_check_char(data : int, bit_index : int, zero_to_one_flip : bool):

    vals_0to1_list = []
    vals_1to0_list = []

    # Calculate value (between 1-16)
    if ((data == ASCII_ZERO_COMPARISON) or (data == ASCII_SPACE_COMPARISON)):
        vals_1to0_list = [0, 1, 2, 3]
    elif (data == ASCII_ONE_COMPARISON):
        vals_0to1_list = [0]
        vals_1to0_list = [1, 2, 3]
    elif (data == ASCII_TW0_COMPARISON):
        vals_0to1_list = [1]
        vals_1to0_list = [0, 2, 3]
    elif (data == ASCII_THREE_COMPARISON):
        vals_0to1_list = [0, 1]
        vals_1to0_list = [2, 3]
    elif (data == ASCII_FOUR_COMPARISON):
        vals_0to1_list = [2]
        vals_1to0_list = [0, 1, 3]
    elif (data == ASCII_FIVE_COMPARISON):
        vals_0to1_list = [0, 2]
        vals_1to0_list = [1, 3]
    elif (data == ASCII_SIX_COMPARISON):
        vals_0to1_list = [1, 2]
        vals_1to0_list = [0, 3]
    elif (data == ASCII_SEVEN_COMPARISON):
        vals_0to1_list = [0, 1, 2]
        vals_1to0_list = [3]
    elif (data == ASCII_EIGHT_COMPARISON):
        vals_0to1_list = [3]
        vals_1to0_list = [0, 1, 2]
    elif (data == ASCII_NINE_COMPARISON):
        vals_0to1_list = [0, 3]
        vals_1to0_list = [1, 2]
    elif (data == ASCII_VAL_LOWER_A):
        vals_0to1_list = [1, 3]
        vals_1to0_list = [0, 2]
    elif (data == ASCII_VAL_LOWER_B):
        vals_0to1_list = [0, 1, 3]
        vals_1to0_list = [2]
    elif (data == ASCII_VAL_LOWER_C):
        vals_0to1_list = [2, 3]
        vals_1to0_list = [0, 1]
    elif (data == ASCII_VAL_LOWER_D):
        vals_0to1_list = [0, 2, 3]
        vals_1to0_list = [1]
    elif (data == ASCII_VAL_LOWER_E):
        vals_0to1_list = [1, 2, 3]
        vals_1to0_list = [0]
    elif (data == ASCII_VAL_LOWER_F):
        vals_0to1_list = [0, 1, 2, 3]
    else:
        print("ERROR: Value read from string not in range")
        exit()

    vals_0to1_list = [x + (bit_index * 4) for x in vals_0to1_list]
    vals_1to0_list = [x + (bit_index * 4) for x in vals_1to0_list]

    # Calculate the value to compare
    if (zero_to_one_flip):
        return vals_0to1_list
    return vals_1to0_list



# Find the rank of a number
def find_rank(rfsh_rate):

    rank = 0
    temp_rfsh_rate = LOWEST_RFSH_RATE

    while (temp_rfsh_rate != rfsh_rate):
        temp_rfsh_rate += temp_rfsh_rate
        rank += 1

    return rank




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, help="file to write to")
    args = parser.parse_args()

    # We want to open json files and concatenate contents into one dictionary
    # Check if file exists
    # if (os.path.isfile(args.output_file)):
    #     print("File already exists, exiting")
    #     exit()
    print("Collecting BIST bit flip Information")

    # Open file to write to
    file_desc = open(args.output_file, 'w')

    # Find line numbers of starting refresh rates in script
    print("Finding refresh rate sections in file")
    refresh_test_ranks = []
    with open("./nexys4ddr_complete_characterization_irradiated/nexys4ddr_complete_characterization_irradiated_refresh_disabled_UART.log") as openedFile:
        find_pattern = False
        find_addr_data_str = False
        for num, line in enumerate(openedFile, 1):
            if SDRAM_REFRESH_TEST_STR.format(refresh_rate=REFRESH_RATE_TESTED) in line:
                find_pattern = True
            elif find_pattern and (SDRAM_PATTERN_REGEX_ZEROS_STR in line):
                test_type = ZEROS_REF_STR
                find_pattern = False
                find_addr_data_str = True
            elif find_pattern and (SDRAM_PATTERN_REGEX_ONES_STR in line):
                test_type = ONES_REF_STR
                find_pattern = False
                find_addr_data_str = True
            elif find_addr_data_str and (ADDR_DATA_STR in line):
                find_addr_data_str = False
                rank = 0
                refresh_test_ranks.append((num, REFRESH_RATE_TESTED, test_type, rank))

    print(refresh_test_ranks)

    # Now go in between all the line numbers and count the total number of bit flips
    refresh_test_total_bit_flips = {}

    test_began = False
    with open("./nexys4ddr_complete_characterization_irradiated/nexys4ddr_complete_characterization_irradiated_refresh_disabled_UART.log") as openedFile:
        for num, line in enumerate(openedFile, 1):


            if HASHTAG_STR in line:
                continue


            if (re.search(REGEX_ERROR_STR, line) != None):
                # Find rank of line (key for total-bit-flips map)
                testtype_of_line = ""
                test_num = 0
                for line_num_index in range(len(refresh_test_ranks) - 1, -1, -1):
                    if num > refresh_test_ranks[line_num_index][RFSH_RATE_NUM_INDEX]:
                        testtype_of_line = refresh_test_ranks[line_num_index][RFSH_RATE_TESTTYPE_INDEX]
                        test_num = line_num_index
                        break

                
                if test_num < 0:
                    continue
                elif test_began == False:
                    print("Test began")
                    test_began = True

                # Grab address and data from list
                try:
                    timeAndAddress, dataval = (line.strip()).split(": ")
                except ValueError:
                    print(traceback.format_exc())
                    file_desc.write(traceback.format_exc())
                    continue

                # Take out all the spaces, they are every ninth element
                dataval = [dataval[(1 + i):(NINTH_INDEX + i)] for i in range(0, LEN_DATA_VAL_EXPECTED, NINTH_INDEX)]
                # print(dataval)

                # Add up total number of errors
                try:
                    for dataword in dataval:

                        if len(dataword) != 8:
                            print("Skipping word: ", dataword)
                            file_desc.write("Skipping word: " + dataword)
                            continue

                        for index in range(len(dataword)):
                            if (testtype_of_line == ZEROS_REF_STR):
                                listoferrs = err_check_char(ord(dataword[index]), 0, True)
                            else:
                                listoferrs = err_check_char(ord(dataword[index]), 0, False)
                            if test_num in refresh_test_total_bit_flips:
                                refresh_test_total_bit_flips[test_num] += len(listoferrs)
                            else:
                                print("On test: ", test_num, end="\r")
                                refresh_test_total_bit_flips[test_num] = len(listoferrs)
                except Exception as e:
                    print(traceback.format_exc())
                    file_desc.write(traceback.format_exc())
                    continue


            elif line.isspace():
                pass
            else:
                str_to_send = "Line not containing expected data. Number: " + str(num) + " Line: " + line
                print(str_to_send)
                file_desc.write(str_to_send)

    # Should have an error bit count of all the bits
    print(refresh_test_total_bit_flips)
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in refresh_test_total_bit_flips.items()]))


if __name__ == "__main__":
    main()