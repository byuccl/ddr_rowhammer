
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
REGEX_ERROR_STR = "0x0[0-9a-f]{6}:  [ 0-9a-f]{7}[0-9a-f] [ 0-9a-f]{7}[0-9a-f]"
BANK_INDEX_INT = 5
BEG_FREQ_CNT = 1
NEXYS4DDR_BANK_BIT_CNT = 3
NEXYS4DDR_COL_BIT_CNT = 8
NEXYS4DDR_COL_BIT_DEL = 2
STARTING_PAGE_NUM = 1
STARTING_DECREMENTING_RANK_NUM = 18
NUM_RANKS = 18 # Ranks range from index 0 - 17, 18 means nonexistentrank
TUNE_OUT_REFRESH_ERRORS = 5
RANK_INDEX = 5
BASE_SIXTEEN = 16
WORD_BIT_CNT = 32
NINTH_INDEX = 9
NUM_BITS_IN_HEX = 4
BIT_CNT_MODULO8 = 8
BIT_CNT_SUB7 = 7
HIGHEST_RFSH_RATE = 38404096
LOWEST_RFSH_RATE = 586
RANK_PAGE_INDEX = 0
RANK_TESTTYPE_INDEX = 2
RANK_RANK_INDEX = 3
ROWS_BANK_CNT = 3
ATTACKED_RW1_INDEX = 0
ATTACKED_RW2_INDEX = 1
BANK_EXTRACT_INDEX = 2
MAX_ROW_ADDR_NEXYS4DDR = 8191
ATTACK_ROW_SEPARATION = 2
ROWHAMMERED_ROW_SEPARATION = 1
LAST_RANK_VAL = 17



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
            
            # FIXME: Hardcoded assumption that bank number is single-digit
            bank_char = file_name.name[bank_index + BANK_INDEX_INT]
            
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

    print("Computing error_map_rbits map (selecting errors near hammered rows, now also selecting bits not in previous test)")

    # Keep only the bits that have flipped near the attacked rows
    error_map_rbits = {}
    rbits_new_list_removed_bits = {}
    near_bit_upper_list = []
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

            # Temporarily store bits in a list
            near_bit_list = []

            for row_key in error_map[key][bank_key]:

                # #####################################
                # # OLD ROW HAMMER COUNTER
                # #####################################

                # # Skip the row if not next to the attacked rows
                # if not ((rows_bank_list[ATTACKED_RW1_INDEX] + 1 == int(row_key)) or 
                #         ((rows_bank_list[ATTACKED_RW1_INDEX] > 0) and (int(row_key) == (rows_bank_list[ATTACKED_RW1_INDEX] - ROWHAMMERED_ROW_SEPARATION))) or
                #         ((rows_bank_list[ATTACKED_RW2_INDEX] < MAX_ROW_ADDR_NEXYS4DDR) and (int(row_key) == (rows_bank_list[ATTACKED_RW2_INDEX] + ROWHAMMERED_ROW_SEPARATION)))):
                #     continue

                # for col_key in error_map[key][bank_key][row_key]:

                #     # Now that address is in attacked bank near attacked rows, add element to list
                #     if not (key in error_map_rbits):
                #         error_map_rbits[key] = {}
                #     if not (bank_key in error_map_rbits[key]):
                #         error_map_rbits[key][bank_key] = {}
                #     if not (row_key in error_map_rbits[key][bank_key]):
                #         error_map_rbits[key][bank_key][row_key] = {}
                #     if not (col_key in error_map_rbits[key][bank_key][row_key]):
                #         error_map_rbits[key][bank_key][row_key][col_key] = error_map[key][bank_key][row_key][col_key]

                # #####################################

                #####################################
                # NEW ROW HAMMER COUNTER
                #####################################

                for col_key in error_map[key][bank_key][row_key]:

                    # Caching (for fast performance)
                    row_map = error_map[key][bank_key][row_key]
                    bit_list = row_map[col_key]

                    # See if bits were already added
                    for bit_num in bit_list:

                        error_map_rbits_keys = list(error_map_rbits.keys())
                        for key_temp in error_map_rbits_keys:
                            if ((bank_key in error_map_rbits[key_temp]) and
                                (row_key in error_map_rbits[key_temp][bank_key]) and 
                                (col_key in error_map_rbits[key_temp][bank_key][row_key]) and 
                                (bit_num in error_map_rbits[key_temp][bank_key][row_key][col_key])):

                                # If it was added (enters this if statement), then
                                # check if it is in our lists of 3rd or 5th bits.
                                # If not, get rid of it.
                                if (((len(near_bit_upper_list) >= 2) and (not ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[1]))) or 
                                    (((len(near_bit_upper_list) >= 1) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[0])) or
                                     ((len(near_bit_upper_list) >= 3) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[2])) or 
                                     ((len(near_bit_upper_list) >= 5) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[4])) or 
                                     ((len(near_bit_upper_list) >= 6) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[5])))):
                                    
                                    # Add this bit to a list of removed bits (we don't want to see it again)
                                    if not (bank_key in rbits_new_list_removed_bits):
                                        rbits_new_list_removed_bits[bank_key] = {}
                                    if not (row_key in rbits_new_list_removed_bits[bank_key]):
                                        rbits_new_list_removed_bits[bank_key][row_key] = {}
                                    if not (col_key in rbits_new_list_removed_bits[bank_key][row_key]):
                                        rbits_new_list_removed_bits[bank_key][row_key][col_key] = []
                                    rbits_new_list_removed_bits[bank_key][row_key][col_key].append(bit_num)

                                    # Remove the bit
                                    error_map_rbits[key_temp][bank_key][row_key][col_key].remove(bit_num)

                                    # If list and maps are empty, remove them accordingly
                                    if len(error_map_rbits[key_temp][bank_key][row_key][col_key]) == 0:
                                        error_map_rbits[key_temp][bank_key][row_key].pop(col_key)
                                    if len(error_map_rbits[key_temp][bank_key][row_key]) == 0:
                                        error_map_rbits[key_temp][bank_key].pop(row_key)
                                    if len(error_map_rbits[key_temp][bank_key]) == 0:
                                        error_map_rbits[key_temp].pop(bank_key)
                                    if len(error_map_rbits[key_temp]) == 0:
                                        error_map_rbits.pop(key_temp)

                        # Don't wanna add bits we just removed that were added previously!
                        if ((bank_key in rbits_new_list_removed_bits) and
                            (row_key in rbits_new_list_removed_bits[bank_key]) and 
                            (col_key in rbits_new_list_removed_bits[bank_key][row_key]) and 
                            (bit_num in rbits_new_list_removed_bits[bank_key][row_key][col_key])):
                            continue

                        # Now that address is in attacked bank near attacked rows, add element to list
                        if not (key in error_map_rbits):
                            error_map_rbits[key] = {}
                        if not (bank_key in error_map_rbits[key]):
                            error_map_rbits[key][bank_key] = {}
                        if not (row_key in error_map_rbits[key][bank_key]):
                            error_map_rbits[key][bank_key][row_key] = {}
                        if not (col_key in error_map_rbits[key][bank_key][row_key]):
                            error_map_rbits[key][bank_key][row_key][col_key] = []
                        if not (bit_num in error_map_rbits[key][bank_key][row_key][col_key]):
                            error_map_rbits[key][bank_key][row_key][col_key].append(bit_num)
                        near_bit_list.append((bank_key, row_key, col_key, bit_num))

            # As soon as all columns have been added, update deque of lists
            if (len(near_bit_upper_list) >= 6):
                near_bit_upper_list.pop(5)
            near_bit_upper_list.insert(0, near_bit_list.copy())
            near_bit_list.clear()

            #####################################
    
    file_desc.write("\n\n\n\n\n\n\n\n")
    file_desc.write("Error map rbits map (all errors that have flippped near attacked rows)")
    file_desc.write("\n".join([str(key) + " : " + str(value) for key, value in error_map_rbits.items()]))

    ##################################################################
    # Added code for keeping bits that flipped near previous attacked rows
    ##################################################################

    prev_error_map_rbits = {}
    rbits_new_list_removed_bits = {}
    near_bit_upper_list = []
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

            # Temporarily store bits in a list
            near_bit_list = []

            for row_key in prev_error_map[key][bank_key]:

                # #####################################
                # # OLD ROW HAMMER COUNTER
                # #####################################

                # # print("\rNum loop: {}".format(index), end='')
                # # index += 1
                # # print(row_key)

                # # Skip the row if not next to the attacked rows
                # if not ((rows_bank_list[ATTACKED_RW1_INDEX] + 1 == int(row_key)) or 
                #         ((rows_bank_list[ATTACKED_RW1_INDEX] > 0) and (int(row_key) == (rows_bank_list[ATTACKED_RW1_INDEX] - ROWHAMMERED_ROW_SEPARATION))) or
                #         ((rows_bank_list[ATTACKED_RW2_INDEX] < MAX_ROW_ADDR_NEXYSVIDEO) and (int(row_key) == (rows_bank_list[ATTACKED_RW2_INDEX] + ROWHAMMERED_ROW_SEPARATION)))):
                #     continue

                # for col_key in prev_error_map[key][bank_key][row_key]:

                #     # Now that address is in attacked bank near attacked rows, add element to list
                #     if not (key in prev_error_map_rbits):
                #         prev_error_map_rbits[key] = {}
                #     if not (bank_key in prev_error_map_rbits[key]):
                #         prev_error_map_rbits[key][bank_key] = {}
                #     if not (row_key in prev_error_map_rbits[key][bank_key]):
                #         prev_error_map_rbits[key][bank_key][row_key] = {}
                #     if not (col_key in prev_error_map_rbits[key][bank_key][row_key]):
                #         prev_error_map_rbits[key][bank_key][row_key][col_key] = prev_error_map[key][bank_key][row_key][col_key]

                # #####################################

                #####################################
                # NEW ROW HAMMER COUNTER
                #####################################

                for col_key in prev_error_map[key][bank_key][row_key]:

                    # Caching (for fast performance)
                    row_map = prev_error_map[key][bank_key][row_key]
                    bit_list = row_map[col_key]

                    # See if bits were already added
                    for bit_num in bit_list:

                        prev_error_map_rbits_keys = list(prev_error_map_rbits.keys())
                        for key_temp in prev_error_map_rbits_keys:
                            if ((bank_key in prev_error_map_rbits[key_temp]) and
                                (row_key in prev_error_map_rbits[key_temp][bank_key]) and 
                                (col_key in prev_error_map_rbits[key_temp][bank_key][row_key]) and 
                                (bit_num in prev_error_map_rbits[key_temp][bank_key][row_key][col_key])):

                                # If it was added (enters this if statement), then
                                # check if it is in our lists of 3rd or 5th bits.
                                # If not, get rid of it.
                                if (((len(near_bit_upper_list) >= 2) and (not ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[1]))) or 
                                    (((len(near_bit_upper_list) >= 1) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[0])) or
                                     ((len(near_bit_upper_list) >= 3) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[2])) or 
                                     ((len(near_bit_upper_list) >= 5) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[4])) or 
                                     ((len(near_bit_upper_list) >= 6) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[5])))):
                                    
                                    # Add this bit to a list of removed bits (we don't want to see it again)
                                    if not (bank_key in rbits_new_list_removed_bits):
                                        rbits_new_list_removed_bits[bank_key] = {}
                                    if not (row_key in rbits_new_list_removed_bits[bank_key]):
                                        rbits_new_list_removed_bits[bank_key][row_key] = {}
                                    if not (col_key in rbits_new_list_removed_bits[bank_key][row_key]):
                                        rbits_new_list_removed_bits[bank_key][row_key][col_key] = []
                                    rbits_new_list_removed_bits[bank_key][row_key][col_key].append(bit_num)

                                    # Remove the bit
                                    prev_error_map_rbits[key_temp][bank_key][row_key][col_key].remove(bit_num)

                                    # If list and maps are empty, remove them accordingly
                                    if len(prev_error_map_rbits[key_temp][bank_key][row_key][col_key]) == 0:
                                        prev_error_map_rbits[key_temp][bank_key][row_key].pop(col_key)
                                    if len(prev_error_map_rbits[key_temp][bank_key][row_key]) == 0:
                                        prev_error_map_rbits[key_temp][bank_key].pop(row_key)
                                    if len(prev_error_map_rbits[key_temp][bank_key]) == 0:
                                        prev_error_map_rbits[key_temp].pop(bank_key)
                                    if len(prev_error_map_rbits[key_temp]) == 0:
                                        prev_error_map_rbits.pop(key_temp)

                        # Don't wanna add bits we just removed that were added previously!
                        if ((bank_key in rbits_new_list_removed_bits) and
                            (row_key in rbits_new_list_removed_bits[bank_key]) and 
                            (col_key in rbits_new_list_removed_bits[bank_key][row_key]) and 
                            (bit_num in rbits_new_list_removed_bits[bank_key][row_key][col_key])):
                            continue           

                        # Now that address is in attacked bank near attacked rows, add element to list
                        if not (key in prev_error_map_rbits):
                            prev_error_map_rbits[key] = {}
                        if not (bank_key in prev_error_map_rbits[key]):
                            prev_error_map_rbits[key][bank_key] = {}
                        if not (row_key in prev_error_map_rbits[key][bank_key]):
                            prev_error_map_rbits[key][bank_key][row_key] = {}
                        if not (col_key in prev_error_map_rbits[key][bank_key][row_key]):
                            prev_error_map_rbits[key][bank_key][row_key][col_key] = []
                        if not (bit_num in prev_error_map_rbits[key][bank_key][row_key][col_key]):
                            prev_error_map_rbits[key][bank_key][row_key][col_key].append(bit_num)
                        near_bit_list.append((bank_key, row_key, col_key, bit_num))

            # As soon as all columns have been added, update deque of lists
            if (len(near_bit_upper_list) >= 6):
                near_bit_upper_list.pop(5)
            near_bit_upper_list.insert(0, near_bit_list.copy())
            near_bit_list.clear()

                #####################################
    
    file_desc.write("\n\n\n\n\n\n\n\n")
    print("\nPrev error map rbits map (all errors that have flippped near attacked rows)")
    file_desc.write("Prev error map rbits map (all errors that have flippped near attacked rows)")
    print("\n".join([str(key) + " : " + str(value) for key, value in prev_error_map_rbits.items()]))
    file_desc.write("\n".join([str(key) + " : " + str(value) for key, value in prev_error_map_rbits.items()]))

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

    # Find line numbers of starting refresh rates in script
    print("Finding refresh rate sections in file")
    refresh_test_ranks = []
    with open("./nexys4ddr_complete_characterization_nonirradiated/nexys4ddr_complete_characterization_nonirradiated_organized.log") as openedFile:
        for num, line in enumerate(openedFile, 1):
            if CHECK_RANK_STR in line:
                rfsh_rate = int(re.search(r'\d+', line).group())
                test_type = ZEROS_REF_STR if (line.find(ZEROS_REF_STR) > 0) else ONES_REF_STR
                rank_num = find_rank(rfsh_rate=rfsh_rate)

                refresh_test_ranks.append((num, rfsh_rate, test_type, rank_num))

    print("Printing refresh rank list: (organized by line number, rfsh rate, test type, rank)")
    refresh_test_ranks = sort_tuple_ranks(refresh_test_ranks)

    print(refresh_test_ranks)

    # Get all refresh test counts
    refresh_test_rank_error_cnts = (len(refresh_test_ranks) + 1) * [0]
    print("\n\n\nrefresh_test_rank_error_cnts:")
    print(refresh_test_rank_error_cnts)

    ## Assert that the log contains data for 16 refresh rates, two tests each (with ones, with zeros)
    assert len(refresh_test_ranks) == (NUM_RANKS * 2)

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

                        # print("part1: bank: ", bank_key, " row: ", row_key, " col: ", col_key, " bit_cnt: ", bit_cnt, " freq: ", frq_cnt_map[bank_key][row_key][col_key][bit_cnt])
                        # if frq_cnt_map[bank_key][row_key][col_key][bit_cnt] > TUNE_OUT_REFRESH_ERRORS:
                        #     total_index += 1
                        #     print("Total lines finished: ", total_index, end='\r')
                        #     if (total_index == 1800):
                        #         print("\n\n\n\nOOPS my mistake\n\n\n\n")
                        #     continue

                        # print("part2: bank: ", bank_key, " row: ", row_key, " col: ", col_key, " bit_cnt: ", bit_cnt, " freq: ", frq_cnt_map[bank_key][row_key][col_key][bit_cnt])

                        ################################
                        # Prev Error Check
                        ################################

                        # # Check if bits are from previous file
                        # if ((bank_key in prev_error_map) and 
                        #     (row_key in prev_error_map[bank_key]) and 
                        #     (col_key in prev_error_map[bank_key][row_key]) and 
                        #     (bit_cnt in prev_error_map[bank_key][row_key][col_key])):
                        #     print("Bit skipped due to prev file: bank: ", bank_key, ", row: ", row_key, ", col: ", col_key, ', bit_cnt: ', bit_cnt)
                        #     file_desc.write("Bit skipped due to prev file: bank: " + str(bank_key) + ", row: " + str(row_key) + ", col: " + str(col_key) + ", bit_cnt: " + str(bit_cnt) + "\n")
                        #     continue

                        ################################


                        ################################
                        # Added code
                        ################################

                        # Prevent previous file bits to be used for this
                        if not(args.prev_file is None):
                            found_prev_bit = False
                            for key_help in prev_error_map_rbits:
                                if (bank_key in prev_error_map_rbits[key_help]) and \
                                (row_key in prev_error_map_rbits[key_help][bank_key]) and \
                                (col_key in prev_error_map_rbits[key_help][bank_key][row_key]) and \
                                (bit_cnt in prev_error_map_rbits[key_help][bank_key][row_key][col_key]):
                                    
                                    found_prev_bit = True
                                    print("Bit found in previous file array, skipping. Attacked: ", key_help, ", Bank: ", bank_key, ", Row: ", row_key, ", Col: ", col_key, ", Bit_cnt: ", bit_cnt)
                                    file_desc.write("\n\nBit found in previous file array, skipping. Attacked: " + key_help + ", Bank: " + str(bank_key) + ", Row: " + str(row_key) + ", Col: " + str(col_key) + ", Bit_cnt: " + str(bit_cnt) + "\n")
                                    break

                            if found_prev_bit == True:
                                continue

                        ################################

                        # Make sure that the bank, row, col exist in rank_map
                        if not (bank_key in rank_map):
                            rank_map[bank_key] = {}
                        if not (row_key in rank_map[bank_key]):
                            rank_map[bank_key][row_key] = {}
                        if not (col_key in rank_map[bank_key][row_key]):
                            rank_map[bank_key][row_key][col_key] = {}
                        if bit_cnt in rank_map[bank_key][row_key][col_key]:
                            continue
                        
                        address_to_convert = int(row_key)
                        address_to_convert = (address_to_convert << NEXYS4DDR_BANK_BIT_CNT) + int(bank_key)
                        address_to_convert = (address_to_convert << NEXYS4DDR_COL_BIT_CNT) + (int(col_key) >> NEXYS4DDR_COL_BIT_DEL) 
                        bist_matching_str = ADDRESS_CONVERSION_STR % (address_to_convert)

                        # print("DEBUG: bank: %x, row: %x, col: %x, bit cnt: %x, matching string: %s" % (int(bank_key), int(row_key), int(col_key), int(bit_cnt), bist_matching_str))


                        # Find the rank
                        address = ""
                        lowest_rank = STARTING_DECREMENTING_RANK_NUM
                        found_lowest_rank = False
                        check_0_flipped_1_list = []
                        with open("./nexys4ddr_complete_characterization_nonirradiated/nexys4ddr_complete_characterization_nonirradiated_organized.log") as openedFile:

                            for line_num, line in enumerate(openedFile, STARTING_PAGE_NUM):
                                # Find the first line in file matching address. There are assumptions made about how the BIST log file opened is organized.
                                if bist_matching_str in line:
                                    
                                    # Assert data exists in correct format
                                    if (re.search(REGEX_ERROR_STR, line) == None):
                                        file_desc.write("\n\nWARNING: Line matching address does not match regex, skipping. Line: " + line + "\n\n")
                                        continue

                                    # Grab address and data from list
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
                                    
                                    # Check 
                                    if ((len(dataval[0]) != 8) or (len(dataval[1]) != 8)):
                                        print("Chars in individual datavals do not match 8. Skipping dataval: ", dataval)
                                        file_desc.write("Chars in individual datavals do not match 8. Skipping dataval: " + dataval)
                                        continue

                                    # Extract exact character from list of strings that is erroneous
                                    bit_cnt_dividebyfour = int(bit_cnt) // NUM_BITS_IN_HEX
                                    bit_cnt_divide_modulo8_sub8 = BIT_CNT_SUB7 - (bit_cnt_dividebyfour % BIT_CNT_MODULO8)

                                    element_index = len(refresh_test_ranks) - 1
                                    while(line_num < refresh_test_ranks[element_index][RANK_PAGE_INDEX]):
                                        element_index -= 1
                                    
                                    check_0_flipped_1 = (refresh_test_ranks[element_index][RANK_TESTTYPE_INDEX] == ZEROS_REF_STR)

                                    print("Testing line from BIST: ", line, " Matching address: ", bist_matching_str, " Bit number: ", bit_cnt, " Check 0 flipped 1: ", check_0_flipped_1)
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

                                            # First check if keys exist in dictionary
                                            # if not((bank_key in rank_map) and (row_key in rank_map[bank_key]) and (col_key in rank_map[bank_key][row_key]) and (bit_cnt in rank_map[bank_key][row_key][col_key])):

                                            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Passed? Yes")
                                            
                                            lowest_rank = refresh_test_ranks[element_index][RANK_RANK_INDEX]
                                            found_lowest_rank = True
                                            refresh_test_rank_error_cnts[element_index] += 1
                                            check_0_flipped_1_list.append((check_0_flipped_1, bist_matching_str))

                                            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Now finding other ranks")

                                        else:

                                            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Passed? No")
                                    
                                    else:

                                        if (len(flipped_bits_list) > 0 and int(bit_cnt) in flipped_bits_list):

                                            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Found rank? Yes")
                                            refresh_test_rank_error_cnts[element_index] += 1
                                            check_0_flipped_1_list.append((check_0_flipped_1, bist_matching_str))
                                        
                                        else:

                                            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Found rank? No")
                                
                                    

                        total_index += 1
                        print("\n\nTotal lines finished: ", total_index, ", rank added: ", lowest_rank) # end = '\r'


                        if (found_lowest_rank == False):
                            refresh_test_rank_error_cnts[len(refresh_test_rank_error_cnts) - 1] += 1

                        print("\n\nCurrent error counts: ", refresh_test_rank_error_cnts)
                        print("\n\n")
                        
                        rank_map[bank_key][row_key][col_key][bit_cnt] = (lowest_rank, timeAndAddress, ''.join(("(" + str(element[0]) + " : " + str(element[1]) + ") ") for element in check_0_flipped_1_list))

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

    file_desc.close()



if __name__ == "__main__":
    main()