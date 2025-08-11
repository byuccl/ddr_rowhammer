import argparse
import os.path
import re
import numpy as np
import json
import traceback
from collections import deque

THOUSAND_KEY_RW_STR = "10000000"
READ_COUNT_KEY_RW_STR = "read_count"
ROW_BANK_ATTACK_KEY_STR = "attacked_row_{row_attacked_str}_bank_{bank}"
ERR_IN_ROW_KEY_STR = "errors_in_rows"

BANK_STR_FILENAME = "bank_"
BANK_INDEX_INT = 5
FREQ_INIT = 100
FREQ_LIMIT = 4
FREQ_LIMIT_OLD = 3

ROWS_BANK_CNT = 3
ATTACKED_RW1_INDEX = 0
ATTACKED_RW2_INDEX = 1
BANK_EXTRACT_INDEX = 2
NO_ERRORS_FOUND = -1

ATTACK_ROW_SEPARATION = 2
ROWHAMMERED_ROW_SEPARATION = 1
MAX_ROW_ADDR_NEXYS4DDR = 8191

BEG_FREQ_CNT = 1

def main():

    # Main changes: Added range_arg_first and range_arg_last, added likely_total_errors variable

    # First grab all the files listed
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', type=argparse.FileType('r'), nargs='+', help="data files to read. Do NOT use data files for multiple boards.")
    parser.add_argument('--compare_file', type=argparse.FileType('r'), default=None, help="Check if actual row hammer errors (from error counter) are in this file")
    parser.add_argument('--output_file', type=str, default=None, help="output file to write to")
    parser.add_argument('--range_arg_first_one', type=int, default=None, help="first_arg_one =< x < last_arg_one, x contains the rows you want to look at")
    parser.add_argument('--range_arg_last_one', type=int, default=None, help="first_arg_one =< x < last_arg_one, x contains the rows you want to look at")
    parser.add_argument('--prev_file', type=argparse.FileType('r'), default=None, help="Collect previous errors from files so they aren't repeatedly used")
    parser.add_argument('--prev_rows', type=int, nargs='+', default=None, help="Control which previous attacked rows are used from previous file.")
    parser.add_argument('--bank', type=int, default=-1, help="Because I'm so sick and tired of having to type bank")
    args = parser.parse_args()
    
    # We want to open json files and concatenate contents into one dictionary
    # Check if file exists
    # if (os.path.isfile(args.output_file)):
    #     print("File already exists, exiting")
    #     exit()
    print("Collecting Rowhammer Information")

    # Open file to write to
    if not (args.output_file == None):
        file_desc = open(args.output_file, 'w')

    # Create map to keep track of errors
    error_map = {}
    prev_error_map = {}

    # Go through all files
    for file_name in args.files:

        if (args.bank == -1):

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

        else:
            bank_char = str(args.bank)
        
        
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


    ##################################################################
    # Added code for prev file error map
    ##################################################################

    if not(args.prev_file is None):
        assert not (args.prev_rows is None)
        temp_dict = json.load(args.prev_file)

        for pair_dict in temp_dict[THOUSAND_KEY_RW_STR].keys():

            # Again, get the correct key and data
            if pair_dict == READ_COUNT_KEY_RW_STR:
                continue
        
            # Collect all integers from key (the two row numbers attacked)
            pair_list = [int(s) for s in pair_dict.split("_") if s.isdigit()]

            # See if the argument we put in were in the pair_list created above. 
            # If it is, then create a map with the key.
            for prev_row_int in args.prev_rows:
                if prev_row_int in pair_list:
                    if not (ROW_BANK_ATTACK_KEY_STR.format(row_attacked_str=pair_dict, bank=bank_char) in prev_error_map):
                        prev_error_map[ROW_BANK_ATTACK_KEY_STR.format(row_attacked_str=pair_dict, bank=bank_char)] = temp_dict[THOUSAND_KEY_RW_STR][pair_dict][ERR_IN_ROW_KEY_STR]

        temp_dict.clear()

    # file_desc.write("\n\n\n\n\n\n\n\n\n\n\n\n The previoius error map data\n\n\n")
    # file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in prev_error_map.items()]))
    
    # file_desc.write("\n\n\n\n\n\n\n\n\n\n\n\n Error map data\n\n\n")
    # file_desc.write("\n".join(["[" + str(key) + " : " + str(value) + "]" for key, value in error_map.items()]))

    ##################################################################
    # First, find the frequency of all bits (all that are in the file)
    ##################################################################

    # Give each bit flip a frequency count
    frq_cnt_map = {}
    for key in error_map:
        for bank_key in error_map[key]:
            for row_key in error_map[key][bank_key]:
                for col_key in error_map[key][bank_key][row_key]:

                    # Find the frequency counts of bits in original file
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

    ##################################################################
    # Find the frequency of all bits in the previous file (if any)
    ##################################################################

    prev_freq_cnt_map = {}
    for key in prev_error_map:
        for bank_key in prev_error_map[key]:
            for row_key in prev_error_map[key][bank_key]:
                for col_key in prev_error_map[key][bank_key][row_key]:
                    for bit_cnt in prev_error_map[key][bank_key][row_key][col_key]:

                        if bank_key in frq_cnt_map and \
                            row_key in frq_cnt_map[bank_key] and \
                            col_key in frq_cnt_map[bank_key][row_key] and \
                            bit_cnt in frq_cnt_map[bank_key][row_key][col_key]:

                            if not (bank_key in prev_freq_cnt_map):
                                prev_freq_cnt_map[bank_key] = {}
                            if not (row_key in prev_freq_cnt_map[bank_key]):
                                prev_freq_cnt_map[bank_key][row_key] = {}
                            if not (col_key in prev_freq_cnt_map[bank_key][row_key]):
                                prev_freq_cnt_map[bank_key][row_key][col_key] = {}
                            if not (bit_cnt in prev_freq_cnt_map[bank_key][row_key][col_key]):
                                prev_freq_cnt_map[bank_key][row_key][col_key][bit_cnt] = frq_cnt_map[bank_key][row_key][col_key][bit_cnt]
                            
                        else:

                            if not (bank_key in prev_freq_cnt_map):
                                prev_freq_cnt_map[bank_key] = {}
                            if not (row_key in prev_freq_cnt_map[bank_key]):
                                prev_freq_cnt_map[bank_key][row_key] = {}
                            if not (col_key in prev_freq_cnt_map[bank_key][row_key]):
                                prev_freq_cnt_map[bank_key][row_key][col_key] = {}
                            if not (bit_cnt in prev_freq_cnt_map[bank_key][row_key][col_key]):
                                prev_freq_cnt_map[bank_key][row_key][col_key][bit_cnt] = NO_ERRORS_FOUND

    file_desc.write("\n\n\n\n\n\n\n\n")
    print("\nPrev freq cnt map ")
    file_desc.write("Prev freq cnt map")
    print("\n".join([str(key) + " : " + str(value) for key, value in prev_freq_cnt_map.items()]))
    file_desc.write("\n".join([str(key) + " : " + str(value) for key, value in prev_freq_cnt_map.items()]))


    ##############################################################################
    # Next, go through each row, find the frequency of every error in each row
    ##############################################################################

    print("Computing error_map_rbits map (selecting errors near hammered rows, now also selecting bits not in previous test)")

    # Keep only the bits that have flipped near the attacked rows
    near_bit_upper_list = []
    error_map_rbits_new = {}
    rbits_new_list_removed_bits = {}
    error_map_rbits = {}
    error_map_rbits_old = {}
    row_counter_old = 0
    row_counter_current = 0
    for key in error_map:

        print("\rprogress: ", key, end="")

        # Extract attacked rows, bank number, and place into list
        rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]

        # Assert we have both rows and bank (should be in this order: row0, row1, bank)
        if (len(rows_bank_list) != ROWS_BANK_CNT):
            print("Assertion error was here")
            print("Len: ", len(rows_bank_list))
            print("list: ", rows_bank_list)
            print("Key: ", key)
            exit(0)
        

        # Both rows should be separated by two
        assert (rows_bank_list[ATTACKED_RW1_INDEX] + ATTACK_ROW_SEPARATION) == (rows_bank_list[ATTACKED_RW2_INDEX])

        for bank_key in error_map[key]:

            # Skip the bank if not the attacked bank
            if (rows_bank_list[BANK_EXTRACT_INDEX] != int(bank_key)):
                continue

            near_bit_list = []

            for row_key in error_map[key][bank_key]:

                ##########################################################
                # Method below only gets errors near attacked rows, 
                ##########################################################

                # Skip the row if not next to the attacked rows
                if not ((rows_bank_list[ATTACKED_RW1_INDEX] + 1 == int(row_key)) or 
                        ((rows_bank_list[ATTACKED_RW1_INDEX] > 0) and (int(row_key) == (rows_bank_list[ATTACKED_RW1_INDEX] - ROWHAMMERED_ROW_SEPARATION))) or
                        ((rows_bank_list[ATTACKED_RW2_INDEX] < MAX_ROW_ADDR_NEXYS4DDR) and (int(row_key) == (rows_bank_list[ATTACKED_RW2_INDEX] + ROWHAMMERED_ROW_SEPARATION)))):
                    
                    pass
                else:

                    row_counter_old += 1

                    for col_key in error_map[key][bank_key][row_key]:

                        # Now that address is in attacked bank near attacked rows, add element to list
                        if not (key in error_map_rbits_old):
                            error_map_rbits_old[key] = {}
                        if not (bank_key in error_map_rbits_old[key]):
                            error_map_rbits_old[key][bank_key] = {}
                        if not (row_key in error_map_rbits_old[key][bank_key]):
                            error_map_rbits_old[key][bank_key][row_key] = {}
                        if not (col_key in error_map_rbits_old[key][bank_key][row_key]):
                            error_map_rbits_old[key][bank_key][row_key][col_key] = error_map[key][bank_key][row_key][col_key]

                ##########################################################

                ##########################################################
                # Method below gets errors everywhere, 
                ##########################################################

                # Keep the row if there are bits that flipped with a frequency less than 4
                lowest_freq = FREQ_INIT
                for col_key in error_map[key][bank_key][row_key]:
                    for bit_cnt in error_map[key][bank_key][row_key][col_key]:

                        # Find the frequency of the bit
                        if not (bit_cnt in frq_cnt_map[bank_key][row_key][col_key]):
                            print("What the heck, why is this bit not in freq_cnt_map? Bank: ", bank_key, " Row: ", row_key, " Column: ", col_key, " Bit: ", bit_cnt)
                            exit()
                        else:  
                            if lowest_freq > frq_cnt_map[bank_key][row_key][col_key][bit_cnt]:
                                lowest_freq = frq_cnt_map[bank_key][row_key][col_key][bit_cnt]

                # If the lowest frequency is less than 4, keep the row
                if lowest_freq < FREQ_LIMIT_OLD:

                    row_counter_current += 1

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

                ##########################################################

                ##########################################################################################
                # Method below gets errors everywhere and makes sure they are within 5 rows of each other
                ##########################################################################################

                # # Keep the row if there are bits that flipped with a frequency less than 4
                # lowest_freq = FREQ_INIT
                # for col_key in error_map[key][bank_key][row_key]:
                #     for bit_cnt in error_map[key][bank_key][row_key][col_key]:

                #         # Find the frequency of the bit
                #         if not (bit_cnt in frq_cnt_map[bank_key][row_key][col_key]):
                #             print("New, What the heck, why is this bit not in freq_cnt_map? Bank: ", bank_key, " Row: ", row_key, " Column: ", col_key, " Bit: ", bit_cnt)
                #             exit()
                #         else:  
                #             if lowest_freq > frq_cnt_map[bank_key][row_key][col_key][bit_cnt]:
                #                 lowest_freq = frq_cnt_map[bank_key][row_key][col_key][bit_cnt]

                # # If the lowest frequency is less than 4, keep the row
                # if lowest_freq < FREQ_LIMIT:

                for col_key in error_map[key][bank_key][row_key]:

                    # Caching (for fast performance)
                    row_map = error_map[key][bank_key][row_key]
                    bit_list = row_map[col_key]

                    # See if bits were already added
                    for bit_num in bit_list:

                        # Debug
                        # print("Error map rbits new : ", error_map_rbits_new, "\n\n")
                        # print("Checking: (Bank: ", bank_key, ", row: ", row_key, ", col: ", col_key, ", bit: ", bit_num, ")")
                        # print("Does this ever run? Near bit upper list: ", near_bit_upper_list)
                        error_map_rbits_keys = list(error_map_rbits_new.keys())
                        for key_temp in error_map_rbits_keys:
                            if ((bank_key in error_map_rbits_new[key_temp]) and
                                (row_key in error_map_rbits_new[key_temp][bank_key]) and 
                                (col_key in error_map_rbits_new[key_temp][bank_key][row_key]) and 
                                (bit_num in error_map_rbits_new[key_temp][bank_key][row_key][col_key])):
                                
                                # Debug
                                # print(" 1st step", end="")

                                # if ((bank_key == "0") and (row_key == "3850") and (col_key == "256") and (bit_num == 42)):
                                #     print("This if statement executed")

                                # If it was added (enters this if statement), then
                                # check if it is in our lists of 3rd or 5th bits.
                                # If not, get rid of it.
                                if (((len(near_bit_upper_list) >= 2) and (not ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[1]))) or 
                                    (((len(near_bit_upper_list) >= 1) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[0])) or
                                     ((len(near_bit_upper_list) >= 3) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[2])) or 
                                     ((len(near_bit_upper_list) >= 5) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[4])) or 
                                     ((len(near_bit_upper_list) >= 6) and ((bank_key, row_key, col_key, bit_num) in near_bit_upper_list[5])))):
                                    if ((bank_key == "0") and (row_key == "3850") and (col_key == "256") and (bit_num == 42)):
                                        print(" part 1, we are looking for ", (bank_key, row_key, col_key, bit_num), end="\n\n")
                                        print("This is part 1, should not be here: ", near_bit_upper_list[0], end="\n\n")
                                        print("This is part 2, possibly should be here: ", near_bit_upper_list[1], end="\n\n")
                                        print("This is part 3, should not be here: ", near_bit_upper_list[2], end="\n\n")
                                        print("This is part 4, possibly should be here: ", near_bit_upper_list[3], end="\n\n")

                                    # Add this bit to a list of removed bits (we don't want to see it again)
                                    if not (bank_key in rbits_new_list_removed_bits):
                                        rbits_new_list_removed_bits[bank_key] = {}
                                    if not (row_key in rbits_new_list_removed_bits[bank_key]):
                                        rbits_new_list_removed_bits[bank_key][row_key] = {}
                                    if not (col_key in rbits_new_list_removed_bits[bank_key][row_key]):
                                        rbits_new_list_removed_bits[bank_key][row_key][col_key] = []
                                    rbits_new_list_removed_bits[bank_key][row_key][col_key].append(bit_num)
                                                                        
                                    # Debug
                                    # print(", 2nd, indeed it does!")
                                    error_map_rbits_new[key_temp][bank_key][row_key][col_key].remove(bit_num)

                                    # If list and maps are empty, remove them accordingly
                                    if len(error_map_rbits_new[key_temp][bank_key][row_key][col_key]) == 0:
                                        error_map_rbits_new[key_temp][bank_key][row_key].pop(col_key)
                                        # print("Removed col: ", col_key)
                                    if len(error_map_rbits_new[key_temp][bank_key][row_key]) == 0:
                                        error_map_rbits_new[key_temp][bank_key].pop(row_key)
                                        # print("Removed row: ", row_key)
                                    if len(error_map_rbits_new[key_temp][bank_key]) == 0:
                                        error_map_rbits_new[key_temp].pop(bank_key)
                                        # print("Removed bank: ", bank_key)
                                    if len(error_map_rbits_new[key_temp]) == 0:
                                        error_map_rbits_new.pop(key_temp)
                                        # print("Removed key: ", key_temp)


                        

                        # Don't wanna add bits we just removed that were added previously!
                        if ((bank_key in rbits_new_list_removed_bits) and
                            (row_key in rbits_new_list_removed_bits[bank_key]) and 
                            (col_key in rbits_new_list_removed_bits[bank_key][row_key]) and 
                            (bit_num in rbits_new_list_removed_bits[bank_key][row_key][col_key])):
                            continue

                        # Now that address is in attacked bank near attacked rows, add element to list
                        if not (key in error_map_rbits_new):
                            error_map_rbits_new[key] = {}
                        if not (bank_key in error_map_rbits_new[key]):
                            error_map_rbits_new[key][bank_key] = {}
                        if not (row_key in error_map_rbits_new[key][bank_key]):
                            error_map_rbits_new[key][bank_key][row_key] = {}
                        if not (col_key in error_map_rbits_new[key][bank_key][row_key]):
                            error_map_rbits_new[key][bank_key][row_key][col_key] = []
                        if not (bit_num in error_map_rbits_new[key][bank_key][row_key][col_key]):
                            error_map_rbits_new[key][bank_key][row_key][col_key].append(bit_num)
                        near_bit_list.append((bank_key, row_key, col_key, bit_num))

                    # print("Near bit list: ", near_bit_list)

            # As soon as all columns have been added, update deque of lists
            # if (len(error_map[key][bank_key]) > 0):
            if (len(near_bit_upper_list) >= 6):
                near_bit_upper_list.pop(5)
            near_bit_upper_list.insert(0, near_bit_list.copy())
            near_bit_list.clear()
            # print("Near bit upper list: ", near_bit_upper_list)
                                
            ##########################################################

    
    error_map.clear()

    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\nOld Counter Row Count: " + str(row_counter_old))
        file_desc.write("\n\n\n\n\nCurrent Counter Row Count: " + str(row_counter_current))
    print("Old row counter: ", row_counter_old, " ##############################")
    print("Current row counter: ", row_counter_current, " ##############################")
    
    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\n")
        file_desc.write("Error map rbits map (all errors that have flippped near attacked rows)")
        file_desc.write("\n".join([str(key) + " : " + str(value) for key, value in error_map_rbits.items()]))
        
        file_desc.write("\n\n\n\n\n\n\n\n")
        file_desc.write("Frequency count map of all errors\n\n")

    # #####################################################
    # # Find why there are more rows in the old error map
    # #####################################################

    # print("####################################################")
    # file_desc.write("####################################################\n")
    # print("# Find why there are more errors in the old error map")
    # file_desc.write("# Find why there are more errors in the old error map\n")
    # print("####################################################")
    # file_desc.write("####################################################\n")

    # # Find out, for every row, how many errors there are
    # for key in error_map_rbits_old:
    #     print("Key: ", key, end="")
    #     file_desc.write("Key: " + str(key))
    #     for bank_key in error_map_rbits_old[key]:
    #         for row_key in error_map_rbits_old[key][bank_key]:
    #             if not (key in error_map_rbits and \
    #                bank_key in error_map_rbits[key] and \
    #                row_key in error_map_rbits[key][bank_key]):
    #                 print("Row: ", row_key, " ", end="")
    #                 file_desc.write("Row: " + row_key + " ")

    #         print("")
    #         file_desc.write("\n")
    #             # for col_key in error_map_rbits_old[key][bank_key][row_key]:
    #             #     for bit_cnt in error_map_rbits_old[key][bank_key][row_key][col_key]:
    #             #         pass


    # #####################################################
    # # Find why there are less rows in the new error map
    # #####################################################

    # print("####################################################")
    # file_desc.write("####################################################\n")
    # print("# Find why there are less errors in the new error map")
    # file_desc.write("# Find why there are less errors in the new error map\n")
    # print("####################################################")
    # file_desc.write("####################################################\n")

    # # Find out, for every row, how many errors there are
    # for key in error_map_rbits:
    #     print("Key: ", key, end="")
    #     file_desc.write("Key: " + str(key))
    #     for bank_key in error_map_rbits[key]:
    #         for row_key in error_map_rbits[key][bank_key]:
    #             if not (key in error_map_rbits_old and \
    #                bank_key in error_map_rbits_old[key] and \
    #                row_key in error_map_rbits_old[key][bank_key]):
    #                 print("Row: ", row_key, " ", end="")
    #                 file_desc.write("Row: " + row_key + " ")
                
    #         print("")
    #         file_desc.write("\n")
        
    #             # for col_key in error_map_rbits[key][bank_key][row_key]:
    #             #     for bit_cnt in error_map_rbits[key][bank_key][row_key][col_key]:
    #             #         pass
                        

    #####################################################
    # Old error counter
    #####################################################
    print("####################################################")
    print("# Starting with old error counter")
    print("####################################################")
    if not (args.output_file == None):
        file_desc.write("####################################################")
        file_desc.write("# Starting with old error counter")
        file_desc.write("####################################################")

    # First find the max frequency count
    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nFinding max frequency count")
    print("Finding max frequency count")
    max_freq = 0
    for bank in frq_cnt_map:
        for row in frq_cnt_map[bank]:
            for col in frq_cnt_map[bank][row]:
                for bit_cnt in frq_cnt_map[bank][row][col]:
                    if max_freq < frq_cnt_map[bank][row][col][bit_cnt]:
                        max_freq = frq_cnt_map[bank][row][col][bit_cnt]

    from collections import defaultdict

    print("Printing errors out from highest frequency to lowest")

    # Preprocess `frq_cnt_map` to group by frequency
    freq_to_entries = defaultdict(list)
    for bank, rows in frq_cnt_map.items():
        for row, cols in rows.items():
            for col, bit_cnt_map in cols.items():
                for bit_cnt, freq in bit_cnt_map.items():
                    freq_to_entries[freq].append((bank, row, col, bit_cnt))

    # Iterate from the highest frequency
    for freq in range(max_freq, 0, -1):
        print(f"Progress: {freq} out of {max_freq}", end="\r")
        if freq in freq_to_entries:
            lines = [
                f"Bank: {bank}, Row: {row}, Column: {col}, Bit Cnt: {bit_cnt}, Freq: {freq}\n"
                for bank, row, col, bit_cnt in freq_to_entries[freq]
            ]
            if not (args.output_file == None):
                file_desc.write("".join(lines))

    # Finally, print errors from highest frequency to loest again, but only the errors in the error_map_rbits
    # Use the previous file (if it exists) to filter out the errors that were already found
    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nPrinting errors out from highest frequency to lowest, but only the errors in error_map_rbits_old\n\n")
    print("Printing errors out from highest frequency to lowest, but only the errors in error_map_rbits_old\n\n")
    total_cnt = 0
    prev_total_cnt = 0
    likely_total_errors = 0
    rank_map = {}
    for freq in range(max_freq, 0, -1):
        print("Progress: ", freq, " out of ", max_freq, end="\r")
        for key in error_map_rbits_old:

            # Extract attacked rows, bank number, and place into list
            rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]

            # Assert we have both rows and bank (should be in this order: row0, row1, bank)
            assert len(rows_bank_list) == ROWS_BANK_CNT

            # Put ranges on the addresses we want to see
            if not (args.range_arg_first_one == None):
                assert not (args.range_arg_last_one == None)

                if rows_bank_list[0] < args.range_arg_first_one or \
                   rows_bank_list[1] < args.range_arg_first_one or \
                   rows_bank_list[0] >= args.range_arg_last_one or\
                   rows_bank_list[1] >= args.range_arg_last_one:
                    continue

            for bank in error_map_rbits_old[key]:
                for row in error_map_rbits_old[key][bank]:
                    for col in error_map_rbits_old[key][bank][row]:
                        for bit_cnt in error_map_rbits_old[key][bank][row][col]:

                            # # Check if in prev freq cnt map first
                            # if bank in prev_freq_cnt_map and \
                            #     row in prev_freq_cnt_map[bank] and \
                            #     col in prev_freq_cnt_map[bank][row] and \
                            #     bit_cnt in prev_freq_cnt_map[bank][row][col] and \
                            #     prev_freq_cnt_map[bank][row][col][bit_cnt] == freq:
                                
                            #     # prev_total_cnt += 1
                            #     file_desc.write("\n".join(["Prev total cnt: ", str(prev_total_cnt), ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "#### Prev freq error\n"]))


                            if frq_cnt_map[bank][row][col][bit_cnt] == freq:

                                if not (bank in rank_map):
                                    rank_map[bank] = {}
                                if not (row in rank_map[bank]):
                                    rank_map[bank][row] = {}
                                if not (col in rank_map[bank][row]):
                                    rank_map[bank][row][col] = {}
                                if bit_cnt in rank_map[bank][row][col]:
                                    continue
                                else: 
                                    rank_map[bank][row][col][bit_cnt] = 0

                                if bank in prev_freq_cnt_map and \
                                    row in prev_freq_cnt_map[bank] and \
                                    col in prev_freq_cnt_map[bank][row] and \
                                    bit_cnt in prev_freq_cnt_map[bank][row][col] and \
                                    prev_freq_cnt_map[bank][row][col][bit_cnt] == freq:

                                    prev_total_cnt += 1
                                    if not (args.output_file == None):
                                        file_desc.write("\n".join(["Prev total cnt: ", str(prev_total_cnt), ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "#### Prev freq error\n"]))
                                    continue

                                total_cnt += 1
                                if (freq < FREQ_LIMIT):
                                    likely_total_errors += 1
                                if not (args.output_file == None):
                                    file_desc.write("\n".join(["Norm total cnt: " + str(total_cnt) + ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "\n"]))

    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nTotal errors: " + str(total_cnt))
        file_desc.write("\n\nLikely Total errors: " + str(likely_total_errors) + "\n\n")
    print("Total errors: ", total_cnt, "##################")
    print("Likely total errors: ", likely_total_errors)
    print("Prev total errors: ", prev_total_cnt, "#############")

    #####################################################
    # New error counter
    #####################################################
    print("####################################################")
    print("# New error counter")
    print("####################################################")
    if not (args.output_file == None):
        file_desc.write("####################################################")
        file_desc.write("# New error counter")
        file_desc.write("####################################################")

    # # First find the max frequency count
    # if not (args.output_file == None):
    #     file_desc.write("\n\n\n\n\n\n\n\nFinding max frequency count")
    # print("Finding max frequency count")
    # max_freq = 0
    # for bank in frq_cnt_map:
    #     for row in frq_cnt_map[bank]:
    #         for col in frq_cnt_map[bank][row]:
    #             for bit_cnt in frq_cnt_map[bank][row][col]:
    #                 if max_freq < frq_cnt_map[bank][row][col][bit_cnt]:
    #                     max_freq = frq_cnt_map[bank][row][col][bit_cnt]

    # print("Printing errors out from highest frequency to lowest")

    # # Preprocess `frq_cnt_map` to group by frequency
    # freq_to_entries = defaultdict(list)
    # for bank, rows in frq_cnt_map.items():
    #     for row, cols in rows.items():
    #         for col, bit_cnt_map in cols.items():
    #             for bit_cnt, freq in bit_cnt_map.items():
    #                 freq_to_entries[freq].append((bank, row, col, bit_cnt))

    # # Iterate from the highest frequency
    # for freq in range(max_freq, 0, -1):
    #     print(f"Progress: {freq} out of {max_freq}", end="\r")
    #     if freq in freq_to_entries:
    #         lines = [
    #             f"Bank: {bank}, Row: {row}, Column: {col}, Bit Cnt: {bit_cnt}, Freq: {freq}\n"
    #             for bank, row, col, bit_cnt in freq_to_entries[freq]
    #         ]
    #         if not (args.output_file == None):
    #             file_desc.write("".join(lines))

    # Finally, print errors from highest frequency to loest again, but only the errors in the error_map_rbits
    # Use the previous file (if it exists) to filter out the errors that were already found
    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nPrinting errors out from highest frequency to lowest, but only the errors in error_map_rbits\n\n")
    print("Printing errors out from highest frequency to lowest, but only the errors in error_map_rbits\n\n")
    total_cnt = 0
    if not (args.compare_file == None):
        new_counter_total_errors = {}
    likely_total_errors = 0
    rank_map = {}
    prev_total_cnt = 0
    for freq in range(max_freq, 0, -1):
        print("Progress: ", freq, " out of ", max_freq, end="\r")
        for key in error_map_rbits:

            # Extract attacked rows, bank number, and place into list
            rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]

            # Assert we have both rows and bank (should be in this order: row0, row1, bank)
            assert len(rows_bank_list) == ROWS_BANK_CNT

            # Put ranges on the addresses we want to see
            if not (args.range_arg_first_one == None):
                assert not (args.range_arg_last_one == None)

                if rows_bank_list[0] < args.range_arg_first_one or \
                   rows_bank_list[1] < args.range_arg_first_one or \
                   rows_bank_list[0] >= args.range_arg_last_one or\
                   rows_bank_list[1] >= args.range_arg_last_one:
                    continue

            for bank in error_map_rbits[key]:
                for row in error_map_rbits[key][bank]:
                    for col in error_map_rbits[key][bank][row]:
                        for bit_cnt in error_map_rbits[key][bank][row][col]:

                            # # Check if in prev freq cnt map first
                            # if bank in prev_freq_cnt_map and \
                            #     row in prev_freq_cnt_map[bank] and \
                            #     col in prev_freq_cnt_map[bank][row] and \
                            #     bit_cnt in prev_freq_cnt_map[bank][row][col] and \
                            #     prev_freq_cnt_map[bank][row][col][bit_cnt] == freq:
                                
                            #     # prev_total_cnt += 1
                            #     file_desc.write("\n".join(["Prev total cnt: ", str(prev_total_cnt), ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "#### Prev freq error\n"]))


                            if frq_cnt_map[bank][row][col][bit_cnt] == freq:

                                if not (bank in rank_map):
                                    rank_map[bank] = {}
                                if not (row in rank_map[bank]):
                                    rank_map[bank][row] = {}
                                if not (col in rank_map[bank][row]):
                                    rank_map[bank][row][col] = {}
                                if bit_cnt in rank_map[bank][row][col]:
                                    continue
                                else: 
                                    rank_map[bank][row][col][bit_cnt] = 0

                                if bank in prev_freq_cnt_map and \
                                    row in prev_freq_cnt_map[bank] and \
                                    col in prev_freq_cnt_map[bank][row] and \
                                    bit_cnt in prev_freq_cnt_map[bank][row][col] and \
                                    prev_freq_cnt_map[bank][row][col][bit_cnt] == freq:

                                    prev_total_cnt += 1
                                    if not (args.output_file == None):
                                        file_desc.write("\n".join(["Prev total cnt: ", str(prev_total_cnt), ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "#### Prev freq error\n"]))
                                    continue

                                total_cnt += 1
                                if (freq < FREQ_LIMIT_OLD):
                                    likely_total_errors += 1

                                    # Only getting the likely errors for comparison
                                    if not (args.compare_file == None):
                                        if not (freq in new_counter_total_errors):
                                            new_counter_total_errors[freq] = {}
                                        if not (bank in new_counter_total_errors[freq]):
                                            new_counter_total_errors[freq][bank] = {}
                                        if not (row in new_counter_total_errors[freq][bank]):
                                            new_counter_total_errors[freq][bank][row] = {}
                                        if not (col in new_counter_total_errors[freq][bank][row]):
                                            new_counter_total_errors[freq][bank][row][col] = {}
                                        if not (bit_cnt in new_counter_total_errors[freq][bank][row][col]):
                                            new_counter_total_errors[freq][bank][row][col][bit_cnt] = {}
                                        
                                if not (args.output_file == None):
                                    file_desc.write("\n".join(["Norm total cnt: " + str(total_cnt) + ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "\n"]))

    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nTotal errors: " + str(total_cnt))
        file_desc.write("\n\nLikely Total errors: " + str(likely_total_errors) + "\n\n")
    print("Total errors: ", total_cnt, "##################")
    print("Likely total errors: ", likely_total_errors)
    print("Prev total errors: ", prev_total_cnt, "#############")

    #####################################################
    # Latest n greatest error counter
    #####################################################
    print("####################################################")
    print("# Latest n greatest counter")
    print("####################################################")
    if not (args.output_file == None):
        file_desc.write("####################################################")
        file_desc.write("# Latest n greatest counter")
        file_desc.write("####################################################")

    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nPrinting errors out from highest frequency to lowest, but only the errors in error_map_rbits_new\n\n")
    print("Printing errors out from highest frequency to lowest, but only the errors in error_map_rbits_new\n\n")
    total_cnt = 0
    if not (args.compare_file == None):
        new_counter_total_errors = {}
    likely_total_errors = 0
    rank_map = {}
    prev_total_cnt = 0
    for freq in range(max_freq, 0, -1):
        print("Progress: ", freq, " out of ", max_freq, end="\r")
        for key in error_map_rbits_new:

            # Extract attacked rows, bank number, and place into list
            rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]

            # Assert we have both rows and bank (should be in this order: row0, row1, bank)
            assert len(rows_bank_list) == ROWS_BANK_CNT

            # Put ranges on the addresses we want to see
            if not (args.range_arg_first_one == None):
                assert not (args.range_arg_last_one == None)

                if rows_bank_list[0] < args.range_arg_first_one or \
                   rows_bank_list[1] < args.range_arg_first_one or \
                   rows_bank_list[0] >= args.range_arg_last_one or\
                   rows_bank_list[1] >= args.range_arg_last_one:
                    continue

            for bank in error_map_rbits_new[key]:
                for row in error_map_rbits_new[key][bank]:
                    for col in error_map_rbits_new[key][bank][row]:
                        for bit_cnt in error_map_rbits_new[key][bank][row][col]:

                            # # Check if in prev freq cnt map first
                            # if bank in prev_freq_cnt_map and \
                            #     row in prev_freq_cnt_map[bank] and \
                            #     col in prev_freq_cnt_map[bank][row] and \
                            #     bit_cnt in prev_freq_cnt_map[bank][row][col] and \
                            #     prev_freq_cnt_map[bank][row][col][bit_cnt] == freq:
                                
                            #     # prev_total_cnt += 1
                            #     file_desc.write("\n".join(["Prev total cnt: ", str(prev_total_cnt), ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "#### Prev freq error\n"]))


                            if frq_cnt_map[bank][row][col][bit_cnt] == freq:

                                if not (bank in rank_map):
                                    rank_map[bank] = {}
                                if not (row in rank_map[bank]):
                                    rank_map[bank][row] = {}
                                if not (col in rank_map[bank][row]):
                                    rank_map[bank][row][col] = {}
                                if bit_cnt in rank_map[bank][row][col]:
                                    continue
                                else: 
                                    rank_map[bank][row][col][bit_cnt] = 0

                                if bank in prev_freq_cnt_map and \
                                    row in prev_freq_cnt_map[bank] and \
                                    col in prev_freq_cnt_map[bank][row] and \
                                    bit_cnt in prev_freq_cnt_map[bank][row][col] and \
                                    prev_freq_cnt_map[bank][row][col][bit_cnt] == freq:

                                    prev_total_cnt += 1
                                    if not (args.output_file == None):
                                        file_desc.write("\n".join(["Prev total cnt: ", str(prev_total_cnt), ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "#### Prev freq error\n"]))
                                    continue

                                total_cnt += 1
                                if (freq < FREQ_LIMIT):
                                    likely_total_errors += 1

                                    # # Only getting the likely errors for comparison
                                    # if not (args.compare_file == None):
                                    #     if not (freq in new_counter_total_errors):
                                    #         new_counter_total_errors[freq] = {}
                                    #     if not (bank in new_counter_total_errors[freq]):
                                    #         new_counter_total_errors[freq][bank] = {}
                                    #     if not (row in new_counter_total_errors[freq][bank]):
                                    #         new_counter_total_errors[freq][bank][row] = {}
                                    #     if not (col in new_counter_total_errors[freq][bank][row]):
                                    #         new_counter_total_errors[freq][bank][row][col] = {}
                                    #     if not (bit_cnt in new_counter_total_errors[freq][bank][row][col]):
                                    #         new_counter_total_errors[freq][bank][row][col][bit_cnt] = {}
                                        
                                if not (args.output_file == None):
                                    file_desc.write("\n".join(["Norm total cnt: " + str(total_cnt) + ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Freq: " + str(freq) + "\n"]))

    if not (args.output_file == None):
        file_desc.write("\n\n\n\n\n\n\n\nTotal errors: " + str(total_cnt))
        file_desc.write("\n\nLikely Total errors: " + str(likely_total_errors) + "\n\n")
    print("Total errors: ", total_cnt, "##################")
    print("Likely total errors: ", likely_total_errors)
    print("Prev total errors: ", prev_total_cnt, "#############")

    #####################################################

    # If we have a file to compare, find matching row hammer errors in compare file
    if not (args.compare_file == None):

        print("####################################################")
        print("# Compare File errors")
        print("####################################################")
        if not (args.output_file == None):
            file_desc.write("####################################################")
            file_desc.write("# Compare File errors")
            file_desc.write("####################################################\n\n\n\n")

        # Get rid of extra memory
        error_map_rbits_old.clear()
        error_map_rbits.clear()
        error_map_rbits_new.clear()

        # Open the new file
        comp_error_map = {}
        temp_dict = (json.load(args.compare_file))

        for pair_dict in temp_dict[THOUSAND_KEY_RW_STR].keys():
            
            # Two types of keys in temp_dict: "read_count", and "pair_%d_%d". The latter points to a 3-keyed map, one key "errors_in_rows"
            # points to a map of error bits (bank numbers, pointing to map of row numbers, pointing to row of column numbers, pointing to 
            # lists full of the bit numbers in each column)
            # We skip the keys with "read_count".
            if pair_dict == READ_COUNT_KEY_RW_STR:
                continue
            
            # Take the map from key "errors_in_rows", this is all we want from the rowhammer tester map. 
            # Create a new key with rows attacked, bank number attacked, 
            comp_error_map[ROW_BANK_ATTACK_KEY_STR.format(row_attacked_str=pair_dict, bank=bank_char)] = temp_dict[THOUSAND_KEY_RW_STR][pair_dict][ERR_IN_ROW_KEY_STR]

        temp_dict.clear()

        # Get a frequency map for the compare file
        # Give each bit flip a frequency count
        frq_cnt_map_comp = {}
        for key in comp_error_map:
            for bank_key in comp_error_map[key]:
                for row_key in comp_error_map[key][bank_key]:
                    for col_key in comp_error_map[key][bank_key][row_key]:

                        # Find the frequency counts of bits in original file
                        if not (bank_key in frq_cnt_map_comp):
                            frq_cnt_map_comp[bank_key] = {}
                        if not (row_key in frq_cnt_map_comp[bank_key]):
                            frq_cnt_map_comp[bank_key][row_key] = {}
                        if not (col_key in frq_cnt_map_comp[bank_key][row_key]):
                            frq_cnt_map_comp[bank_key][row_key][col_key] = {}
                        for bit_cnt in comp_error_map[key][bank_key][row_key][col_key]:
                            if not (bit_cnt in frq_cnt_map_comp[bank_key][row_key][col_key]):
                                # rows_bank_list = [int(i) for i in key.split('_') if i.isdigit()]
                                # rows_bank_list.insert(0, BEG_FREQ_CNT)
                                frq_cnt_map_comp[bank_key][row_key][col_key][bit_cnt] = BEG_FREQ_CNT
                            else:
                                frq_cnt_map_comp[bank_key][row_key][col_key][bit_cnt] += 1

        # Finally, do a comparison between the two
        total_cnt = 0
        high_cnt = 0
        for freq in new_counter_total_errors:
            for bank in new_counter_total_errors[freq]:
                for row in new_counter_total_errors[freq][bank]:
                    for col in new_counter_total_errors[freq][bank][row]:
                        for bit_cnt in new_counter_total_errors[freq][bank][row][col]:

                            if bank in frq_cnt_map_comp and \
                            row  in frq_cnt_map_comp[bank] and \
                            col  in frq_cnt_map_comp[bank][row] and \
                            bit_cnt in frq_cnt_map_comp[bank][row][col]:
                                
                                total_cnt += 1
                                if ((frq_cnt_map[bank][row][col][bit_cnt] >= FREQ_LIMIT) or (frq_cnt_map_comp[bank][row][col][bit_cnt] >= FREQ_LIMIT)):
                                    file_desc.write("\n".join(["Total cnt: " + str(total_cnt) + ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Source Freq: " + str(frq_cnt_map[bank][row][col][bit_cnt]) + ", Freq in compare file: " + str(frq_cnt_map_comp[bank][row][col][bit_cnt]) + "#####################################################################################\n"]))
                                    high_cnt += 1
                                else:
                                    file_desc.write("\n".join(["Total cnt: " + str(total_cnt) + ", Bank: " + str(bank) + ", Row: " + str(row) + ", Column: " + str(col) + ", Bit Cnt " + str(bit_cnt) + ", Source Freq: " + str(frq_cnt_map[bank][row][col][bit_cnt]) + ", Freq in compare file: " + str(frq_cnt_map_comp[bank][row][col][bit_cnt]) + "\n"]))

        print("Final comparison count: ", total_cnt)
        print("High count: ", high_cnt)
        file_desc.write("\n\nFinal comparison count: " + str(total_cnt))
        file_desc.write("\n\nHigh count: " + str(high_cnt))

    pass
        


if __name__=="__main__":
    main()