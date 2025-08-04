
import re
import argparse
import os
import logging
import traceback



CHECK_RANK_STR = "test"
ZEROS_REF_STR = "zeros"
ONES_REF_STR = "ones"
REGEX_ERROR_STR = "0x[01][0-9a-f]{6}:  [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f]"
HASHTAG_STR = "###"
ZERO_ADD_STR = "0"
LEN_DATA_VAL_EXPECTED = 36
MIN_BIN_LENGTH = 10
LOWEST_RFSH_RATE = 782
LAST_RANK_VAL = 17
NINTH_INDEX = 9
RFSH_RATE_NUM_INDEX = 0
RFSH_RATE_RANK_INDEX = 3
RFSH_RATE_TESTTYPE_INDEX = 2

# Organized as follows: (<name of file>, <refresh_cnt>, (<line number>, <type of data, <rank number>), (<line number>, <type of data, <rank number>), ...)
SIZE_LOG_FILE_TUPLES_SMALL = 5
LOG_FILE_NONIR_STRINGS = [
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_782.log", 782, 0, ZEROS_REF_STR, 0, 15, ONES_REF_STR, 1),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_1564.log", 1564, 0, ZEROS_REF_STR, 2, 15, ONES_REF_STR, 3),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_3128.log", 3128, 0, ZEROS_REF_STR, 4, 15, ONES_REF_STR, 5), 
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_6256.log", 6256, 0, ZEROS_REF_STR, 6, 15, ONES_REF_STR, 7),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_12512.log", 12512, 0, ZEROS_REF_STR, 8, 15, ONES_REF_STR, 9),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_25024.log", 25024, 0, ZEROS_REF_STR, 10, 25, ONES_REF_STR, 11),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_50048.log", 50048, 0, ZEROS_REF_STR, 12, 33, ONES_REF_STR, 13),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_100096.log", 100096, 0, ZEROS_REF_STR, 14, 133, ONES_REF_STR, 15),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_200192.log", 200192, 0, ZEROS_REF_STR, 16, 1091, ONES_REF_STR, 17),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_400384.log", 400384, 0, ZEROS_REF_STR, 18, 10611, ONES_REF_STR, 19),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_800768.log", 800768, 0, ZEROS_REF_STR, 20, 84502, ONES_REF_STR, 21),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_UART_refresh_rate_1601536.log", 1601536, 0, ZEROS_REF_STR, 22, 513539, ONES_REF_STR, 23),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_tk2_UART_refresh_rate_3203072.log", 3203072, 0, ONES_REF_STR, 24, 2015772, ZEROS_REF_STR, 25),
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_tk2_UART_refresh_rate_6406144.log", 6406144, 0, ONES_REF_STR, 26, 3180190, ZEROS_REF_STR, 27), # Ones
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_tk2_UART_refresh_rate_12812288.log", 12812288, 0, ONES_REF_STR, 28), # Zeros
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_tk3_UART_refresh_rate_12812288.log", 12812288, 0, ZEROS_REF_STR, 29), # Ones
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_tk3_UART_refresh_rate_25624576.log", 25624576, 0, ZEROS_REF_STR, 30), # Zeros
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_tk4_UART_refresh_rate_25624576.log", 25624576, 0, ONES_REF_STR, 31), # Ones
    ("/media/rickstr/KINGSTON/row_hammer_research/ChipIR_Radiation_Test/Experiment_Data/nexys_video/nexys_video_nonirrad_whatthecrap_sd_card_issues_actual/bist_data/nexys_vid_nonir_sd_card_issues_whatthecrap/nexys_vid_nonir_sd_card_issues_actual_refresh_disabled_UART_refresh_rate_0.log", 0, 0, ZEROS_REF_STR, 32, 5370352, ONES_REF_STR, 33), # Zeros
]

FILE_NAME_INDEX = 0
FILE_LOWER_REFSTR_INDEX = 3
FILE_LOWER_RANK_INDEX = 4
FILE_LINE_NUM_INDEX = 5
FILE_HIGHER_REFSTR_INDEX = 6
FILE_HIGHER_RANK_INDEX = 7





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

    if (rfsh_rate == 0):
        return LAST_RANK_VAL

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

    # # Find line numbers of starting refresh rates in script
    # print("Finding refresh rate sections in file")
    # refresh_test_ranks = []
    # with open("./nexys_video_complete_characterization_irradiated/nexys_video_complete_caracterization_irradiated_complete_log.txt") as openedFile:
    #     for num, line in enumerate(openedFile, 1):
    #         if CHECK_RANK_STR in line:
    #             rfsh_rate = int(re.search(r'\d+', line).group())
    #             test_type = ZEROS_REF_STR if (line.find(ZEROS_REF_STR) > 0) else ONES_REF_STR
    #             rank_num = find_rank(rfsh_rate=rfsh_rate)

    #             refresh_test_ranks.append((num, rfsh_rate, test_type, rank_num))

    # print(refresh_test_ranks)

    # Now go in between all the line numbers and count the total number of bit flips
    refresh_test_total_bit_flips = {}
    refresh_bank_total_bit_flips = {}
    refresh_test_total_bits = {}
    refresh_bank_total_bits = {}


    test_began = False
    for file_tuple in LOG_FILE_NONIR_STRINGS:
        with open(file_tuple[FILE_NAME_INDEX]) as openedFile:
            for num, line in enumerate(openedFile, 1):


                if (re.search(REGEX_ERROR_STR, line) != None):
                    # Find rank of line (key for total-bit-flips map)
                    testtype_of_line = ""
                    test_num = 0
                    # for line_num_index in range(len(refresh_test_ranks) - 1, -1, -1):
                    #     if num > refresh_test_ranks[line_num_index][RFSH_RATE_NUM_INDEX]:
                    #         testtype_of_line = refresh_test_ranks[line_num_index][RFSH_RATE_TESTTYPE_INDEX]
                    #         test_num = line_num_index
                    #         break

                    if ((len(file_tuple) > SIZE_LOG_FILE_TUPLES_SMALL) and (num > file_tuple[FILE_LINE_NUM_INDEX])):
                        test_num = file_tuple[FILE_HIGHER_RANK_INDEX]
                        testtype_of_line = file_tuple[FILE_HIGHER_REFSTR_INDEX]
                    else:
                        test_num = file_tuple[FILE_LOWER_RANK_INDEX]
                        testtype_of_line = file_tuple[FILE_LOWER_REFSTR_INDEX]

                    
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

                    # Figure out the bank from the time-address string
                    # Take the last nine chars from the string, these have the address
                    # print(timeAndAddress)
                    timeString = timeAndAddress[len(timeAndAddress) - 7:len(timeAndAddress)]
                    # print(timeString)
                    bankString = timeString[4:6]  # Address is 7 digits including three extra bits to the left, row address is bits 0 - 14, bank is bits 15 - 17 so get
                                                # the letters corresponding to bits 13 - 20
                    # print(bankString)
                    bankString = int(bankString, base=16) # First convert to integer using base 16
                    # print(bankString)
                    bankBinaryStr = bin(bankString) # Turn it to a binary string
                    # print(bankBinaryStr)
                    while len(bankBinaryStr) < MIN_BIN_LENGTH:
                        bankBinaryStr = bankBinaryStr[0:2] + "0" + bankBinaryStr[2:]
                    assert len(bankBinaryStr) == MIN_BIN_LENGTH
                        
                        
                    bankBinaryStr = bankBinaryStr[:2] + bankBinaryStr[4:7] # Take out the bits 0 - 1, 5 - 7, leave 'Ob' at the beginning
                    # print(bankBinaryStr)
                    if bankBinaryStr == '0b00000010':
                        print(timeAndAddress)
                        print(timeString)
                        print(bankString)
                        print(bankBinaryStr)
                        exit()
                    bankInt = int(bankBinaryStr, base=2)
                    # print(bankInt)
                    assert bankInt >= 0 and bankInt <= 7

                    # Add up total number of errors

                    if len(dataval) < 4:
                        print("Len of dataval: ", len(dataval), ", dataval: ", dataval, ", Line: ", line)
                        exit()

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
                                    refresh_test_total_bits[test_num] += 4
                                    if (bankInt == 0):
                                        refresh_bank_total_bit_flips[test_num] += len(listoferrs)
                                        refresh_bank_total_bits[test_num] += 4
                                else:
                                    print("On test: ", test_num, end="\r")
                                    refresh_test_total_bit_flips[test_num] = len(listoferrs)
                                    refresh_test_total_bits[test_num] = 4
                                    if bankInt == 0:
                                        refresh_bank_total_bit_flips[test_num] = len(listoferrs)
                                        refresh_bank_total_bits[test_num] = 4
                                    else:
                                        refresh_bank_total_bit_flips[test_num] = 0
                                        refresh_bank_total_bits[test_num] = 0

                        if refresh_bank_total_bits[test_num] % 128 != 0:
                            print("ERROR: Bank total bit flips not divisible by 128")
                            print("Len of dataval: ", len(dataval), ", dataval: ", dataval, ", Line: ", line)
                            print(refresh_bank_total_bit_flips[test_num])
                            exit()

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
    # print(refresh_test_total_bit_flips)
    print(refresh_test_total_bit_flips)
    file_desc.write("\n\n\n\n\n\n\n\nPrinting refresh test total bit flips\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in refresh_test_total_bit_flips.items()]))

    # Print out the total number of bits for bank 0 
    print(refresh_bank_total_bit_flips)
    file_desc.write("\n\n\n\n\n\n\n\nPrinting refresh test total bit flips for bank 0\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in refresh_bank_total_bit_flips.items()]))

    # Print out the total number of bits
    print(refresh_test_total_bits)
    file_desc.write("\n\n\n\n\n\n\n\nPrinting refresh test total bits\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in refresh_test_total_bits.items()]))

    # Print out the total number of bits for bank 0
    print(refresh_bank_total_bits)
    file_desc.write("\n\n\n\n\n\n\n\nPrinting refresh test total bits for bank 0\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in refresh_bank_total_bits.items()]))


if __name__ == "__main__":
    main()