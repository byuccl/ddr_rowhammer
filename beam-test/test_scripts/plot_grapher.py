

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.collections import PolyCollection



DRAM_WAIT_TIMES = [1, 5, 10, 60, 120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200]



def create_display_subplot(end_refresh_rate, input_list, refresh_list, max_error_cnt, write_ones:bool):
    # Plot everything
    # Set subplot up
    ax = plt.figure().add_subplot(projection='3d')

    # Get colors for each graph
    facecolors = plt.colormaps['viridis_r'](np.linspace(0, 1, len(input_list)))

    poly = PolyCollection(input_list, facecolors=facecolors)
    ax.add_collection3d(poly, zs=refresh_list, zdir='y')
    ax.set(xlim=(DRAM_WAIT_TIMES[0], DRAM_WAIT_TIMES[len(DRAM_WAIT_TIMES) - 1]), ylim=(0, end_refresh_rate), zlim=(0, max_error_cnt), xlabel='Wait time (sec)', ylabel='Refresh rate (ck)', zlabel='Errors') # xlim=(0, 10), ylim=(1, 9), zlim=(0, 0.35),
    # ax.add_collection3d(poly, zs=range(0, len(refresh_list)), zdir='y')
    # ax.set(xlim=(DRAM_WAIT_TIMES[0], DRAM_WAIT_TIMES[len(DRAM_WAIT_TIMES) - 1]), ylim=(0, len(refresh_list)), zlim=(0, max_error_cnt), xlabel='Wait time (sec)', ylabel='Refresh rate tests', zlabel='Errors') # xlim=(0, 10), ylim=(1, 9), zlim=(0, 0.35),

    if write_ones:
        plt.title("Writing All Ones")
    else:
        plt.title("Writing All Zeros")

    plt.show(block=False)


def main():
    ones_error_point_list = [[(1, 0), (1, 0), (5, 58), (10, 812), (60, 256228), (120, 1169366), (240, 2612779), (360, 2770355), (480, 2788569), (600, 2841049), (720, 2822130), (840, 2754107), (960, 2796231), (1080, 2757127), (1200, 2736866), (1200, 0)], [(1, 0), (1, 0), (5, 53), (10, 723), (60, 255557), (120, 1380780), (240, 4018297), (360, 5597400), (480, 6338295), (600, 6506608), (720, 6572561), (840, 6579251), (960, 6599163), (1080, 6620769), (1200, 6621875), (1200, 0)], [(1, 0), (1, 0), (5, 54), (10, 682), (60, 261955), (120, 1519917), (240, 4622887), (360, 6425082), (480, 7288832), (600, 7764960), (720, 8000395), (840, 8127562), (960, 8187997), (1080, 8211172), (1200, 8216664), (1200, 0)], [(1, 0), (1, 0), (5, 49), (10, 661), (60, 262227), (120, 1518038), (240, 4924529), (360, 6800292), (480, 7609213), (600, 7968967), (720, 8150800), (840, 8261540), (960, 8315526), (1080, 8340792), (1200, 8358266), (1200, 0)]]
    zeros_error_point_list = [[(1, 0), (1, 0), (5, 58), (10, 818), (60, 251162), (120, 1152716), (240, 2643052), (360, 2785352), (480, 2838390), (600, 2844376), (720, 2761273), (840, 2819357), (960, 2790603), (1080, 2753157), (1200, 2747114), (1200, 0)], [(1, 0), (1, 0), (5, 48), (10, 717), (60, 254832), (120, 1382445), (240, 4009998), (360, 5631519), (480, 6355884), (600, 6515905), (720, 6580763), (840, 6612191), (960, 6632283), (1080, 6662044), (1200, 6611223), (1200, 0)], [(1, 0), (1, 0), (5, 50), (10, 665), (60, 262170), (120, 1507906), (240, 4630714), (360, 6442208), (480, 7315937), (600, 7766009), (720, 8001116), (840, 8136024), (960, 8192774), (1080, 8214609), (1200, 8214183), (1200, 0)], [(1, 0), (1, 0), (5, 44), (10, 656), (60, 258560), (120, 1513164), (240, 4941522), (360, 6800661), (480, 7621962), (600, 7974164), (720, 8160685), (840, 8270047), (960, 8314479), (1080, 8341498), (1200, 8359164), (1200, 0)]]
    refresh_list = [1200128, 2400256, 4800512, 9601024]
    end_refresh_rate = refresh_list[len(refresh_list) - 1]
    max_error_cnt = 8390707

    create_display_subplot(
        end_refresh_rate=end_refresh_rate, 
        input_list=ones_error_point_list,
        refresh_list=refresh_list,
        max_error_cnt=max_error_cnt,
        write_ones=True)
    
    create_display_subplot(
        end_refresh_rate=end_refresh_rate, 
        input_list=zeros_error_point_list,
        refresh_list=refresh_list,
        max_error_cnt=max_error_cnt,
        write_ones=False)
    
    input("Press Enter to continue...       ")

if __name__ == "__main__":
    main()