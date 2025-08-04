
import argparse
import os.path
import re
import numpy as np
import json
import traceback


THOUSAND_KEY_RW_STR = "10000000"
READ_COUNT_KEY_RW_STR = "read_count"
PAIR_ROW_KEY_STR = "pair_{first_row}_{second_row}"
ROW_BANK_ATTACK_KEY_STR = "attacked_row_{row_attacked_str}_bank_{bank}"
ADDRESS_CONVERSION_STR = "0x%07x"
ERR_IN_ROW_KEY_STR = "errors_in_rows"
BANK_STR_FILENAME = "bank_"
FULL_LINE_REGEX = "#### refresh rate {refresh_rate} test {one_zero_str}"
LINE_RANK_STR_REGEX = "#### refresh rate \d* test (zeros|ones)"
CHECK_RANK_STR = "test"
ZEROS_REF_STR = "zeros"
ONES_REF_STR = "ones"
REGEX_ERROR_STR = "0x[0-1][0-9a-f]{6}:  [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f]"
BANK_INDEX_INT = 5
BEG_FREQ_CNT = 1
NEXYS_VIDEO_BANK_BIT_CNT = 3
NEXYS_VIDEO_COL_BIT_CNT = 7
NEXYS_VIDEO_COL_BIT_DEL = 3
STARTING_PAGE_NUM = 1
NUM_RANKS = 17 # Ranks range from index 0 - 15, 16 means nonexistentrank
STARTING_DECREMENTING_RANK_NUM = NUM_RANKS
TUNE_OUT_REFRESH_ERRORS = 5
RANK_INDEX = 5
WORD_BIT_CNT = 32
NINTH_INDEX = 9
NUM_BITS_IN_HEX = 4
BIT_CNT_MODULO8 = 8
BIT_CNT_SUB7 = 7
HIGHEST_RFSH_RATE = 38404096
LOWEST_RFSH_RATE = 782
RANK_PAGE_INDEX = 0
RANK_TESTTYPE_INDEX = 2
RANK_RANK_INDEX = 3
ROWS_BANK_CNT = 3
ATTACKED_RW1_INDEX = 0
ATTACKED_RW2_INDEX = 1
BANK_EXTRACT_INDEX = 2
MAX_ROW_ADDR_NEXYSVIDEO = 32767
ATTACK_ROW_SEPARATION = 2
ROWHAMMERED_ROW_SEPARATION = 1
LAST_RANK_VAL = 17
CHARS_PER_DATA_WORD = 8
FREQ_LIMIT_CNT = 4 # Anything equal to this or above will be rejected as a possible non-rowhammer error.



# Open the log files needed 
# Organized as follows: (<name of file>, <line number>, <type of data, <line number>, <type of data>, ...)
LEN_RANKS = (NUM_RANKS * 2) + 1 # Enough for counting each rank
LOG_FILE_STRINGS = [
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_782.log", 782, 0, ONES_REF_STR, 0, 24, ZEROS_REF_STR, 1),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_1564.log", 1564, 0, ONES_REF_STR, 2, 31, ZEROS_REF_STR, 3),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_3128.log", 3128, 0, ONES_REF_STR, 4, 62, ZEROS_REF_STR, 5), 
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_6256.log", 6256, 0, ONES_REF_STR, 6, 211, ZEROS_REF_STR, 7),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_12512.log", 12512, 0, ONES_REF_STR, 8, 703, ZEROS_REF_STR, 9),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_25024.log", 25024, 0, ONES_REF_STR, 10, 2162, ZEROS_REF_STR, 11),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_50048.log", 50048, 0, ONES_REF_STR, 12, 6193, ZEROS_REF_STR, 13),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_100096.log", 100096, 0, ONES_REF_STR, 14, 16923, ZEROS_REF_STR, 15),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_200192.log", 200192, 0, ONES_REF_STR, 16, 47096, ZEROS_REF_STR, 17),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_400384.log", 400384, 0, ONES_REF_STR, 18, 127737, ZEROS_REF_STR, 19),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_800768.log", 800768, 0, ONES_REF_STR, 20, 359383, ZEROS_REF_STR, 21),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_1601536.log", 1601536, 0, ONES_REF_STR, 22, 1147207, ZEROS_REF_STR, 23),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_3203072.log", 3203072, 0, ONES_REF_STR, 24, 2415606, ZEROS_REF_STR, 25),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_6406144.log", 6406144, 0, ONES_REF_STR, 26, 3426757, ZEROS_REF_STR, 27),
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_12812288.log", 12812288, 0, ONES_REF_STR, 28), # Ones
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_12812288_take2.log", 12812288, 0, ZEROS_REF_STR, 29), # Zeros
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_25624576_take2_ones.log", 25624576, 0, ONES_REF_STR, 30), # Ones
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_rate_25624576_zeros.log", 25624576, 0, ZEROS_REF_STR, 31), # Zeros
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_disabled.log_UART_refresh_rate_0.log", 0, 0, ONES_REF_STR, 32), # Ones
    ("nexys_video_complete_characterization_nonirradiated/nexys_video_complete_characterization_nonirradiated_UART_refresh_disabled_tk2.log_UART_refresh_rate_0.log", 0, 0, ZEROS_REF_STR, 33), # Zeros
]
LOG_FILE_STRING_INDEX = 0
LOG_FILE_REFRESH_RATE_INDEX = 1
LOG_FILE_RANK_INDEX_FIRST = 4
LOG_FILE_RANK_INDEX_SECOND = 7
LOG_FILE_PG_NUM_INDEX = 5 
LOG_FILE_TUPLE_SMALL_SIZE = 5
LOG_FILE_ONES_ZEROS_INDEX_SECOND = 6
LOG_FILE_ONES_ZEROS_INDEX_FIRST = 3



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







# Return a list of bit numbers flipped from zero to one
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


# Sort the categories of errors by their line number
def sort_tuple_ranks(refresh_test_ranks):
    
    return sorted(refresh_test_ranks, key=lambda x: x[RANK_PAGE_INDEX])



def main():

    # First grab all the files listed
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', type=argparse.FileType('r'), nargs='+', help="data files to read. Do NOT use data files for multiple boards.")
    parser.add_argument('--output_file', type=str, help="file to write to")
    parser.add_argument('--prev_file', type=argparse.FileType('r'), default=None, help="Collect previous errors from files so they aren't repeatedly used")
    parser.add_argument('--prev_rows', type=int, nargs='+', default=None, help="Control which previous attacked rows are used from previous file.")
    parser.add_argument('--error_max_warning_threshold', type=int, default=8, help="Warn user if errors in address exceed this threshold")
    args = parser.parse_args()
    
    # We want to open json files and concatenate contents into one dictionary
    # Check if file exists
    # if (os.path.isfile(args.output_file)):
    #     print("File already exists, exiting") 
    #     exit()
    print("Collecting Rowhammer Information")

    # Open file to write to
    file_desc = open(args.output_file, 'w')

    # Create map to keep track of errors
    error_map = {}
    prev_error_map = {}

    # Go through all files
    for file_name in args.files:

        bank_index = 0
        bank_char = ""
        bank_index = file_name.name.find(BANK_STR_FILENAME)

        # There is no way to tell from the rowhammer tester logs alone which bank was attacked. 
        # Therefore, bank description must be in the name of rowhammer log file exactly like this: "bank_%d"
        # I make assumption that the file name does not start with bank description, find the actual starting nonzero index of this string
        if (bank_index != 0):   
            bank_char_index = 0

            temp_digit_char = file_name.name[bank_index + BANK_INDEX_INT + bank_char_index]

            while (temp_digit_char.isdigit()):

                bank_char += temp_digit_char
                bank_char_index += 1
                temp_digit_char = file_name.name[bank_index + BANK_INDEX_INT + bank_char_index]

            print("Received bank number from rowhammer test: [", bank_char, "]")
                
            
        # Close if bank number not found, as this helps with keys
        else:
            print("ERROR: Bank number not in name!")
            exit()
        
        # print(bank_char)
        
        
        temp_dict = (json.load(file_name))

        for pair_dict in temp_dict[THOUSAND_KEY_RW_STR].keys():
            
            # Two types of keys in temp_dict: "read_count", and "pair_%d_%d". The latter points to a 3-keyed map, one key "errors_in_rows"
            # points to a map of error bits (bank numbers, pointing to map of row numbers, pointing to row of column numbers, pointing to 
            # lists full of the bit numbers in each column)
            # We skip the keys with "read_count".
            if pair_dict == READ_COUNT_KEY_RW_STR:
                continue
            
            # Take the map from key "errors_in_rows", this is all we want from the rowhammer tester map. 
            # Create a new key with rows attacked, bank number attacked, 
            error_map[ROW_BANK_ATTACK_KEY_STR.format(row_attacked_str=pair_dict, bank=bank_char)] = temp_dict[THOUSAND_KEY_RW_STR][pair_dict][ERR_IN_ROW_KEY_STR]

        temp_dict.clear()

    file_desc.write("\n The complete error map data\n\n\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in error_map.items()]))

    ##################################################################
    # added code for prev file error map
    ##################################################################
    if not(args.prev_file is None):
        assert not (args.prev_rows is None)
        temp_dict = json.load(args.prev_file)

        for pair_dict in temp_dict[THOUSAND_KEY_RW_STR].keys():

            # Again, get the correct key and data
            if pair_dict ==  READ_COUNT_KEY_RW_STR:
                continue

            # Collect all integers from key (the two row numbers attacked)
            pair_list = [int(s) for s in pair_dict.split("_") if s.isdigit()]

            # See if the arguments we put in were in the pair_list created
            # above. If it is, then create a map with the key.
            for prev_row_int in args.prev_rows:
                if prev_row_int in pair_list:
                    if not (ROW_BANK_ATTACK_KEY_STR.format(row_attacked_str=pair_dict, bank=bank_char) in prev_error_map):
                        prev_error_map[ROW_BANK_ATTACK_KEY_STR.format(row_attacked_str=pair_dict, bank=bank_char)] = temp_dict[THOUSAND_KEY_RW_STR][pair_dict][ERR_IN_ROW_KEY_STR]

        temp_dict.clear()

    file_desc.write("\n The previoius error map data\n\n\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in prev_error_map.items()]))

    ##################################################################

    print("Computing error_map_rbits map (selecting errors near hammered rows)")

    # Keep only the bits that have flipped near the attacked rows
    error_map_rbits = {}
    index = 0
    for key in error_map:

        # Extract attacked rows, bank number, and place into list
        rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]

        # Assert we have both rows and bank (should be in this order: row0, row1, bank)
        assert len(rows_bank_list) == ROWS_BANK_CNT

        # Both rows should be separated by two
        assert (rows_bank_list[ATTACKED_RW1_INDEX] + ATTACK_ROW_SEPARATION) == (rows_bank_list[ATTACKED_RW2_INDEX])

        for bank_key in error_map[key]:

            # Skip the bank if not the attacked bank
            if (rows_bank_list[BANK_EXTRACT_INDEX] != int(bank_key)): 
                continue

            for row_key in error_map[key][bank_key]:

                # print("\rNum loop: {}".format(index), end='')
                # index += 1
                # print(row_key)

                # Skip the row if not next to the attacked rows
                if not ((rows_bank_list[ATTACKED_RW1_INDEX] + 1 == int(row_key)) or 
                        ((rows_bank_list[ATTACKED_RW1_INDEX] > 0) and (int(row_key) == (rows_bank_list[ATTACKED_RW1_INDEX] - ROWHAMMERED_ROW_SEPARATION))) or
                        ((rows_bank_list[ATTACKED_RW2_INDEX] < MAX_ROW_ADDR_NEXYSVIDEO) and (int(row_key) == (rows_bank_list[ATTACKED_RW2_INDEX] + ROWHAMMERED_ROW_SEPARATION)))):
                    continue

                for col_key in error_map[key][bank_key][row_key]:

                    # Now that address is in attacked bank near attacked rows, add element to list
                    if not (key in error_map_rbits):
                        error_map_rbits[key] = {}
                    if not (bank_key in error_map_rbits[key]):
                        error_map_rbits[key][bank_key] = {}
                    if not (row_key in error_map_rbits[key][bank_key]):
                        error_map_rbits[key][bank_key][row_key] = {}
                    if not (col_key in error_map_rbits[key][bank_key][row_key]):
                        error_map_rbits[key][bank_key][row_key][col_key] = error_map[key][bank_key][row_key][col_key]

    

    file_desc.write("\n\n\n\n\n\n\n\n")
    print("\nError map rbits map (all errors that have flippped near attacked rows)")
    file_desc.write("Error map rbits map (all errors that have flippped near attacked rows)")
    print("\n".join([str(key) + " : " + str(value) for key, value in error_map_rbits.items()]))
    file_desc.write("\n".join([str(key) + " : " + str(value) for key, value in error_map_rbits.items()]))

    ##################################################################
    # Added code for keeping bits that flipped near previous attacked rows
    ##################################################################

    if not(args.prev_file is None):

        prev_error_map_rbits = {}
        for key in prev_error_map:
            
            # Extract attacked rows, bank number, and place into list
            rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]

            # Assert we have both rows and bank (should be in this order: row0, row1, bank)
            assert len(rows_bank_list) == ROWS_BANK_CNT

            # Both rows should be separated by two
            assert (rows_bank_list[ATTACKED_RW1_INDEX] + ATTACK_ROW_SEPARATION) == (rows_bank_list[ATTACKED_RW2_INDEX])

            for bank_key in prev_error_map[key]:

                # Skip the bank if not the attacked bank
                if (rows_bank_list[BANK_EXTRACT_INDEX] != int(bank_key)): 
                    continue

                for row_key in prev_error_map[key][bank_key]:

                    # print("\rNum loop: {}".format(index), end='')
                    # index += 1
                    # print(row_key)

                    # Skip the row if not next to the attacked rows
                    if not ((rows_bank_list[ATTACKED_RW1_INDEX] + 1 == int(row_key)) or 
                            ((rows_bank_list[ATTACKED_RW1_INDEX] > 0) and (int(row_key) == (rows_bank_list[ATTACKED_RW1_INDEX] - ROWHAMMERED_ROW_SEPARATION))) or
                            ((rows_bank_list[ATTACKED_RW2_INDEX] < MAX_ROW_ADDR_NEXYSVIDEO) and (int(row_key) == (rows_bank_list[ATTACKED_RW2_INDEX] + ROWHAMMERED_ROW_SEPARATION)))):
                        continue

                    for col_key in prev_error_map[key][bank_key][row_key]:

                        # Now that address is in attacked bank near attacked rows, add element to list
                        if not (key in prev_error_map_rbits):
                            prev_error_map_rbits[key] = {}
                        if not (bank_key in prev_error_map_rbits[key]):
                            prev_error_map_rbits[key][bank_key] = {}
                        if not (row_key in prev_error_map_rbits[key][bank_key]):
                            prev_error_map_rbits[key][bank_key][row_key] = {}
                        if not (col_key in prev_error_map_rbits[key][bank_key][row_key]):
                            prev_error_map_rbits[key][bank_key][row_key][col_key] = prev_error_map[key][bank_key][row_key][col_key]

        file_desc.write("\n\n\n\n\n\n\n\n")
        print("\nPrev error map rbits map (all errors that have flippped near attacked rows)")
        file_desc.write("Prev error map rbits map (all errors that have flippped near attacked rows)")
        print("\n".join([str(key) + " : " + str(value) for key, value in prev_error_map_rbits.items()]))
        file_desc.write("\n".join([str(key) + " : " + str(value) for key, value in prev_error_map_rbits.items()]))
        exit()

    ##################################################################

    print("Computing frequency map of all errors")

    # Give each bit flip a frequency count
    frq_cnt_map = {}
    for key in error_map:
        for bank_key in error_map[key]:
            for row_key in error_map[key][bank_key]:
                for col_key in error_map[key][bank_key][row_key]:
                    if not (bank_key in frq_cnt_map):
                        frq_cnt_map[bank_key] = {}
                    if not (row_key in frq_cnt_map[bank_key]):
                        frq_cnt_map[bank_key][row_key] = {}
                    if not (col_key in frq_cnt_map[bank_key][row_key]):
                        frq_cnt_map[bank_key][row_key][col_key] = {}
                    for bit_cnt in error_map[key][bank_key][row_key][col_key]:
                        if not (bit_cnt in frq_cnt_map[bank_key][row_key][col_key]):
                            # rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]
                            # rows_bank_list.insert(0, BEG_FREQ_CNT)
                            frq_cnt_map[bank_key][row_key][col_key][bit_cnt] = BEG_FREQ_CNT
                        else:
                            frq_cnt_map[bank_key][row_key][col_key][bit_cnt] += 1

    file_desc.write("\n\n\n\n\n\n\n\n\n\nFreq cnt map:\n")

    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in frq_cnt_map.items()]))

    ############################################################

    # For every file, find the line number of the "Pattern set to:" string; there are two of them (or one)

    # Probably don't need this
    # # Find line numbers of starting refresh rates in script
    # print("Finding refresh rate sections in file")
    # refresh_test_ranks = []
    # with open("./nexys_video_complete_characterization_irradiated/nexys_video_complete_caracterization_irradiated_complete_log.txt") as openedFile:
    #     for num, line in enumerate(openedFile, 1):
    #         if CHECK_RANK_STR in line:
    #             rfsh_rate = int(re.search(r'\d+', line).group())
    #             test_type = ZEROS_REF_STR if (line.find(ZEROS_REF_STR) > 0) else ONES_REF_STR
    #             rank_num = find_rank(rfsh_rate=rfsh_rate)
    #             print(rfsh_rate, ", ", test_type, ", ", rank_num)
    #             pass
    #             refresh_test_ranks.append((num, rfsh_rate, test_type, rank_num))



    # #############################################################
    # # Added code

    # refresh_test_ranks = []
    # for num, tuple_group in enumerate(LOG_FILE_STRINGS):
    #     refresh_test_ranks.append()

    # #############################################################

                
    # print.write("[" + ", \n".join([str(n) for n in refresh_test_ranks]) + "]")

    # Get all refresh test counts
    # refresh_test_rank_error_cnts = (len(refresh_test_ranks) + 1) * [0]
    refresh_test_rank_error_cnts = LEN_RANKS * [0]
    refresh_test_rank_ercnts_minus_frequent_bits = LEN_RANKS * [0]
    print("\n\n\nrefresh_test_rank_error_cnts:")
    print(refresh_test_rank_error_cnts)

    # ## Assert that the log contains data for 16 refresh rates, two tests each (with ones, with zeros)
    # assert len(refresh_test_ranks) == (NUM_RANKS * 2)

    ## Create a string that matches string in BIST, find it in log, and set a rank for it
    print("Computing rank map")
    print(frq_cnt_map)
    rank_map = {}
    total_index = 0
    for key in error_map_rbits:
        for bank_key in error_map_rbits[key]:
            for row_key in error_map_rbits[key][bank_key]:
                for col_key in error_map_rbits[key][bank_key][row_key]:
                    for bit_cnt in error_map_rbits[key][bank_key][row_key][col_key]:

                        # # print("part1: bank: ", bank_key, " row: ", row_key, " col: ", col_key, " bit_cnt: ", bit_cnt, " freq: ", frq_cnt_map[bank_key][row_key][col_key][bit_cnt])
                        # if frq_cnt_map[bank_key][row_key][col_key][bit_cnt] > TUNE_OUT_REFRESH_ERRORS:
                        #     total_index += 1
                        #     print("Total lines finished: ", total_index, end='\r')
                        #     if (total_index == 1800):
                        #         print("\n\n\n\nOOPS my mistake\n\n\n\n")
                        #     continue

                        # print("part2: bank: ", bank_key, " row: ", row_key, " col: ", col_key, " bit_cnt: ", bit_cnt, " freq: ", frq_cnt_map[bank_key][row_key][col_key][bit_cnt])

                        #################################################################################
                        # Added code
                        #################################################################################

                        # Prevent previous file bits to be used for this
                        if not(args.prev_file is None):
                            found_prev_bit = False
                            for key in prev_error_map_rbits:
                                if (bank_key in prev_error_map_rbits[key]) and \
                                (row_key in prev_error_map_rbits[key][bank_key]) and \
                                (col_key in prev_error_map_rbits[key][bank_key][row_key]) and \
                                (bit_cnt in prev_error_map_rbits[key][bank_key][row_key][col_key]):
                                    
                                    found_prev_bit = True
                                    print("Bit found in previous file array, skipping. Bank: ", bank_key, ", Row: ", row_key, ", Col: ", col_key, ", Bit_cnt: ", bit_cnt)
                                    file_desc.write("\n\nBit found in previous file array, skipping. Bank: " + str(bank_key) + ", Row: " + str(row_key) + ", Col: " + str(col_key) + ", Bit_cnt: " + str(bit_cnt) + "\n")
                                    break
                            
                            if found_prev_bit == True:
                                continue
                        
                        #################################################################################

                        # Make sure that the bank, row, col exist in rank_map
                        if not (bank_key in rank_map):
                            rank_map[bank_key] = {}
                        if not (row_key in rank_map[bank_key]):
                            rank_map[bank_key][row_key] = {}
                        if not (col_key in rank_map[bank_key][row_key]):
                            rank_map[bank_key][row_key][col_key] = {}
                        if bit_cnt in rank_map[bank_key][row_key][col_key]:
                            continue

                        # Use row, bank, and column to get the string format of the address we want to find
                        address_to_convert = int(row_key)
                        address_to_convert = (address_to_convert << NEXYS_VIDEO_BANK_BIT_CNT) + int(bank_key)
                        address_to_convert = (address_to_convert << NEXYS_VIDEO_COL_BIT_CNT) + (int(col_key) >> NEXYS_VIDEO_COL_BIT_DEL) 
                        bist_matching_str = ADDRESS_CONVERSION_STR % (address_to_convert)

                        # print("DEBUG: bank: %x, row: %x, col: %x, bit cnt: %x, matching string: %s" % (int(bank_key), int(row_key), int(col_key), int(bit_cnt), bist_matching_str))


                        # Find the rank
                        address = ""
                        lowest_rank = STARTING_DECREMENTING_RANK_NUM
                        found_lowest_rank = False
                        timeAndAddress = ""
                        check_0_flipped_1_list = []
                        for tuple_group in LOG_FILE_STRINGS:
                            with open(tuple_group[LOG_FILE_STRING_INDEX]) as openedFile:

                                print("Bist string to match: ", bist_matching_str)
                                for line_num, line in enumerate(openedFile, STARTING_PAGE_NUM):
                                    # Find the first line in file matching address. There are assumptions made about how the BIST log file opened is organized.
                                    if bist_matching_str in line:
                                        print("Looking at line from BIST: ", line, end="")
    
                                        # Assert data exists in correct format
                                        if (re.search(REGEX_ERROR_STR, line) == None):
                                            file_desc.write("\n\nWARNING: Line matching address does not match regex, skipping. Line: " + line + "\n\n")
                                            continue

                                        # Grab address and data from list
                                        try:
                                            timeAndAddress, dataval = (line.strip()).split(": ")
                                        except ValueError:
                                            print(traceback.format_exc())
                                            file_desc.write(traceback.format_exc())
                                            continue

                                        # Take out all the spaces, they are every ninth element
                                        dataval = [dataval[(1 + i):(NINTH_INDEX + i)] for i in range(0, len(dataval), NINTH_INDEX)]
                                        # print(dataval)
                                        
                                        # Check the correct number of hex digits in each dataval. (Is this necessary?)
                                        if ((len(dataval[0]) != CHARS_PER_DATA_WORD) or 
                                            (len(dataval[1]) != CHARS_PER_DATA_WORD) or 
                                            (len(dataval[2]) != CHARS_PER_DATA_WORD) or 
                                            (len(dataval[3]) != CHARS_PER_DATA_WORD)):
                                            print("Chars in individual datavals do not match 8. Skipping dataval: ", dataval)
                                            file_desc.write("Chars in individual datavals do not match 8. Skipping dataval: " + dataval)
                                            continue

                                        # Extract exact character from list of strings that is erroneous
                                        bit_cnt_dividebyfour = int(bit_cnt) // NUM_BITS_IN_HEX
                                        bit_cnt_divide_modulo8_sub8 = BIT_CNT_SUB7 - (bit_cnt_dividebyfour % BIT_CNT_MODULO8)

                                        #############################################################

                                        # Find the rank
                                        # element_index = tuple_group[LOG_FILE_RANK_INDEX_FIRST] // 2
                                        # check_0_flipped_1 = (refresh_test_ranks[element_index][RANK_TESTTYPE_INDEX] == ZEROS_REF_STR)
                                        if ((len(tuple_group) > LOG_FILE_TUPLE_SMALL_SIZE) and (line_num >= tuple_group[LOG_FILE_PG_NUM_INDEX])):
                                            check_0_flipped_1 = (tuple_group[LOG_FILE_ONES_ZEROS_INDEX_SECOND] == ZEROS_REF_STR)
                                        else:
                                            check_0_flipped_1 = (tuple_group[LOG_FILE_ONES_ZEROS_INDEX_FIRST] == ZEROS_REF_STR)

                                        print("Testing line from BIST: ", line, " Matching address: ", bist_matching_str, " Bit number: ", bit_cnt, " Check 0 flipped 1: ", check_0_flipped_1)
                                        print("Bank: ", bank_key, " Row: ", row_key, " Column: ", col_key)
                                        print("Dataval: ", dataval)
                                        print("Bit being checked: ", bit_cnt_dividebyfour)
                                        print("First index of data val: ", int(bit_cnt) // WORD_BIT_CNT)
                                        print("Second index of data val checking: ", bit_cnt_divide_modulo8_sub8)
                                        print("Dataval index value: ", dataval[int(bit_cnt) // WORD_BIT_CNT][bit_cnt_divide_modulo8_sub8:bit_cnt_divide_modulo8_sub8 + 1])

                                        flipped_bits_list = err_check_char(ord(dataval[int(bit_cnt) // WORD_BIT_CNT][bit_cnt_divide_modulo8_sub8:bit_cnt_divide_modulo8_sub8 + 1]), bit_cnt_dividebyfour, check_0_flipped_1)

                                        print("Flipped bits list: ", flipped_bits_list)

                                        if (found_lowest_rank == False):
                                            lowest_rank = STARTING_DECREMENTING_RANK_NUM
                                            if (len(flipped_bits_list) > 0 and int(bit_cnt) in flipped_bits_list):

                                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Passed? Yes")
                                                
                                                lowest_rank = (tuple_group[LOG_FILE_RANK_INDEX_FIRST] // 2)
                                                found_lowest_rank = True
                                                if((len(tuple_group) > LOG_FILE_TUPLE_SMALL_SIZE) and (line_num >= tuple_group[LOG_FILE_PG_NUM_INDEX])):
                                                    refresh_test_rank_error_cnts[tuple_group[LOG_FILE_RANK_INDEX_SECOND]] += 1 
                                                    if frq_cnt_map[bank_key][row_key][col_key][bit_cnt] < FREQ_LIMIT_CNT:
                                                        refresh_test_rank_ercnts_minus_frequent_bits[tuple_group[LOG_FILE_RANK_INDEX_SECOND]] += 1   
                                                else:
                                                    refresh_test_rank_error_cnts[tuple_group[LOG_FILE_RANK_INDEX_FIRST]] += 1 
                                                    if frq_cnt_map[bank_key][row_key][col_key][bit_cnt] < FREQ_LIMIT_CNT:
                                                        refresh_test_rank_ercnts_minus_frequent_bits[tuple_group[LOG_FILE_RANK_INDEX_FIRST]] += 1  
                                                check_0_flipped_1_list.append((check_0_flipped_1, bist_matching_str))

                                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Now finding other ranks")

                                            else:
                                        
                                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Passed? No")

                                        else:

                                            if (len(flipped_bits_list) > 0 and int(bit_cnt) in flipped_bits_list):

                                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Found rank? Yes")
                                                if((len(tuple_group) > LOG_FILE_TUPLE_SMALL_SIZE) and (line_num >= tuple_group[LOG_FILE_PG_NUM_INDEX])):
                                                    refresh_test_rank_error_cnts[tuple_group[LOG_FILE_RANK_INDEX_SECOND]] += 1  
                                                    if frq_cnt_map[bank_key][row_key][col_key][bit_cnt] < FREQ_LIMIT_CNT:
                                                        refresh_test_rank_ercnts_minus_frequent_bits[tuple_group[LOG_FILE_RANK_INDEX_SECOND]] += 1  
                                                else:
                                                    refresh_test_rank_error_cnts[tuple_group[LOG_FILE_RANK_INDEX_FIRST]] += 1 
                                                    if frq_cnt_map[bank_key][row_key][col_key][bit_cnt] < FREQ_LIMIT_CNT:
                                                        refresh_test_rank_ercnts_minus_frequent_bits[tuple_group[LOG_FILE_RANK_INDEX_FIRST]] += 1  
                                                check_0_flipped_1_list.append((check_0_flipped_1, bist_matching_str))
                                            
                                            else:

                                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Found rank? No")

                        total_index += 1
                        print("\n\nTotal lines finished: ", total_index, ", rank added: ", lowest_rank) # end = '\r'

                        if (found_lowest_rank == False):
                            refresh_test_rank_error_cnts[len(refresh_test_rank_error_cnts) - 1] += 1
                            refresh_test_rank_ercnts_minus_frequent_bits[len(refresh_test_rank_error_cnts) - 1] += 1

                        print("\n\nCurrent error counts: ", refresh_test_rank_error_cnts)
                        print("\n\n")
                        
                        if len(timeAndAddress) > 0:
                            rank_map[bank_key][row_key][col_key][bit_cnt] = (lowest_rank, timeAndAddress, ''.join(("(" + str(element[0]) + " : " + str(element[1]) + ") ") for element in check_0_flipped_1_list))
                        else:
                            rank_map[bank_key][row_key][col_key][bit_cnt] = (lowest_rank, bist_matching_str, ''.join(("(" + str(element[0]) + " : " + str(element[1]) + ") ") for element in check_0_flipped_1_list))

    file_desc.write("\n\n\n\n\n\n\n\nRank map {bank, row, col, bit_num, rank), rank:0-17, 18 means nonexistant (18 refresh tests):\n")
    file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in rank_map.items()]))

    # Create a list of tuples from information
    print("Creating tuple list (bank, row, col, bit_num, freq, rank), rank:0-17, 18 means nonexistant (18 refresh tests):")
    file_desc.write("Creating tuple list (bank, row, col, bit_num, freq, rank), rank:0-17, 18 means nonexistant (18 refresh tests):")
    organized_rank_list = []
    for bank_key in rank_map:
        for row_key in rank_map[bank_key]:
            for col_key in rank_map[bank_key][row_key]:
                for bit_cnt in rank_map[bank_key][row_key][col_key]:
                    organized_rank_list.append((int(bank_key), int(row_key), int(col_key), int(bit_cnt), frq_cnt_map[bank_key][row_key][col_key][bit_cnt], rank_map[bank_key][row_key][col_key][bit_cnt][0], rank_map[bank_key][row_key][col_key][bit_cnt][1], rank_map[bank_key][row_key][col_key][bit_cnt][2]))

    # Organize the list by rank with a lambda
    organized_rank_list.sort(key=lambda a: a[RANK_INDEX])

    file_desc.write("\n\n\n\n\n\n\n\nOrganized list (bank, row, col, bit_num, freq, rank), rank:0-17, 18 means nonexistant (18 refresh tests):\n")
    for tuple_element in organized_rank_list:
        file_desc.write(str(tuple_element) + "\n")

    # Write the number of rowhammer errors found in refresh tests to file
    file_desc.write("\n\n\n\n\n\n\n\nList of rowhammer errors found for each section of refresh errors")
    for element in refresh_test_rank_error_cnts:
        file_desc.write("[" + str(element) + "]\n")

    # Show the count of first-time errrs for simplicity's sake
    file_desc.write("\n\n\n\n\n\n\n\nList of first-time rowhammer errors found for each section of refresh errors:\n")
    counter_var = 0
    for help_index in range(NUM_RANKS + 1):
        for element in organized_rank_list:
            if help_index == element[RANK_INDEX]:
                counter_var += 1
        file_desc.write(str(counter_var) + "\n")
        counter_var = 0

    file_desc.write("\n\n\n\n\n\n\n\nList of rowhammer errors found for each section of refresh errors minus frequent counts equal to or greater than: " + str(FREQ_LIMIT_CNT))
    for element in refresh_test_rank_ercnts_minus_frequent_bits:
        file_desc.write("[" + str(element) + "]\n")

    file_desc.close()



if __name__ == "__main__":
    main()