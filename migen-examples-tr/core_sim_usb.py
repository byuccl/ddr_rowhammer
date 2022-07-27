#!/usr/bin/env python3

from operator import eq

from migen import *

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform
    
# Design

cmd_deselect = 0b1111
cmd_no_op = 0b0111
cmd_activate = 0b0011
cmd_auto_refresh = 0b0001
cmd_load_mode = 0b0000
cmd_read = 0b0101
cmd_write = 0b0100
cmd_precharge = 0b0010
# burst terminate: 0b0110

class Core(Module):
    def __init__(self):
        # Signals to output:
        # current_command, cke_sig, odt_sig, a_sig, b_sig
        
        # The "reset_state = INIT_STATE" is unecessary since
        # the reset state is the first fsm.act() entry by default,
        # but this is how you explicitly say which state should
        # be the reset state.
        dram_fsm = FSM(reset_state = "INIT_STATE")
        self.submodules += dram_fsm

        self.current_command = Signal(4)
        self.cke_sig = Signal()
        self.odt_sig = Signal()
        self.b_sig = Signal(4)
        self.a_sig = Signal(13)
        self.dq_sig = Signal(16)
        self.done_init = Signal(2)
        self.dqs = Signal()
        self.clock_domains.neg = ClockDomain()
        self.comb += self.neg.clk.eq(~ClockSignal("sys"))
        
        counter_example = Signal(20)

        counter = Signal(max=20_000)
        counter_init_preload = 20_000
        counter_cke_init_preload = 40
        counter_wait_program_preload = 2 
        counter_wait_refresh_preload = 20
        counter_wait_twohundred_preload = 200

        dram_fsm.act("INIT_STATE",
            NextValue(counter, counter_init_preload),
            NextState("POWER_UP_WAIT")
        )
        dram_fsm.act("POWER_UP_WAIT",
            If(counter == 0, 
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 0),
                NextValue(self.cke_sig, 1),
                NextValue(counter, counter_cke_init_preload),
                NextState("CKE_HIGH_WAIT")
            ).Else(
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("CKE_HIGH_WAIT",
            If(counter == 0, 
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_precharge),
                NextValue(counter, counter_wait_program_preload),
                # A10 high issues precharge to all banks
                NextValue(self.a_sig, 0b0010000000000),
                NextState("PRECHARGE_ALL")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
                
        )
        dram_fsm.act("PRECHARGE_ALL", 
            If(counter == 0,
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_load_mode),
                NextValue(self.b_sig, 0b010),
                # A7 - 0 for 1x refresh rate 
                NextValue(self.a_sig, 0b0000000000000),
                NextValue(counter, counter_wait_program_preload),
                NextState("PROGRAM_EMR2")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )

        
        dram_fsm.act("PROGRAM_EMR2",
        
            If(counter == 0,   
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_load_mode),
                NextValue(self.b_sig, 0b011),
                # 'A' should be 0 in EMR3
                NextValue(self.a_sig, 0b0000000000000),
                NextState("PROGRAM_EMR3")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )

        dram_fsm.act("PROGRAM_EMR3",
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_load_mode),
                NextValue(self.b_sig, 0b001),
                # A9, A8, A7 - 0 0 0, the option 1 1 1 turns on the off-chip
                # driver function, an optional ddr2 jedec feature 
                NextValue(self.a_sig, 0b0000000000000),
                NextState("PROGRAM_EMR")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )

        dram_fsm.act("PROGRAM_EMR",
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_load_mode),
                NextValue(self.b_sig, 0b000),
                # A8 - 1, issues DLL reset during initialization, must wait 200 cycles
                # (Does this resynchronize the internal clock with the external?)
                NextValue(self.a_sig, 0b0000100000000),
                NextState("PROGRAM_MR")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("PROGRAM_MR",
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_precharge),
                NextValue(self.b_sig, 0),
                # A10 high issues precharge to all banks
                NextValue(self.a_sig, 0b0010000000000),
                NextState("PRECHARGE_ALL_AGAIN")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("PRECHARGE_ALL_AGAIN",
            If(counter == 0,
                NextValue(counter, counter_wait_refresh_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_auto_refresh),
                NextValue(self.b_sig, 0),
                # A10 high issues precharge to all banks
                NextValue(self.a_sig, 0),
                NextState("REFRESH_1")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("REFRESH_1",
            If(counter == 0,
                NextValue(counter, counter_wait_refresh_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_auto_refresh),
                NextState("REFRESH_2")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("REFRESH_2",
                #A2-A0: Burst length (selected as 8 bit)
                #A3: Burst Type (selected as interleaved)
                #A6-A4: CAS Latency (between 3-7, currently 5)
                # This is the delay, in clock cycles, between the Read
                # command and the availability of the first bit of output data,
                # depending on the speed grade option being used.
                #A7: Mode (0 normal, 1 test)
                #A8: DLL Reset (0 no, 1 yes) Do not reset a second time
                #A11-A9: Write Recovery, tWR in ns / tCK in ns, round up
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_auto_refresh),
                NextValue(self.b_sig, 0b000),
                NextValue(self.a_sig, 0b0010001010010),
                NextState("PROGRAM_MR_2")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("PROGRAM_MR_2",
                #A0: DLL Enable (0 for enable(normal), 1 for disable(text/debug))
                #A1: Output Drive Strength (0 for full(normal), 1 for reduced)
                #A5-A3: Posted CAS additive latency (pg 88). After an activate command, 
                # the operation must wait tRCD (about 15 ns). This adds wait cycles to
                # accomidate this time if a read/write command is issued before the
                # end of tRCD.
                #A6, A2: Fixes ODT resistance or disables it.
                #A9-A7: OCD operation, 1 1 1 to enable ocd defaults
                #A10: DQS# enable(0)/disable(1), DQS# acts as the complement of DQS.
                #A11: RDQS enable(1)/disable(0). This signal acts the same as DQS.
                #A12: Output enable(0)/disable(1). All outputs (DQ, DQS, DQS#, RDQS, RDQS#)
                # function normally when they are enabled.
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_auto_refresh),
                NextValue(self.b_sig, 0b001),
                NextValue(self.a_sig, 0b0001110000000),
                NextValue(self.dqs, 1),
                NextState("PROGRAM_EMR_ENABLE_OCD_DEFAULT")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )

        dram_fsm.act("PROGRAM_EMR_ENABLE_OCD_DEFAULT",
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_auto_refresh),
                NextValue(self.b_sig, 0b001),
                NextValue(self.a_sig, 0b0000000000000),
                NextState("PROGRAM_EMR_ENABLE_OCD_EXIT")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("PROGRAM_EMR_ENABLE_OCD_EXIT",
            If(counter == 0,
                NextValue(counter, counter_wait_twohundred_preload),
                NextValue(self.odt_sig, 1),
                NextState("WAIT_FOR_DLL_RESET")
            ).Else(
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("WAIT_FOR_DLL_RESET",
            If(counter == 0,
                NextValue(counter, counter_wait_program_preload),
                NextValue(self.odt_sig, 0),
                NextValue(self.current_command, cmd_no_op),
                NextValue(self.b_sig, 0b000),
                NextValue(self.a_sig, 0b0000000000000),
                NextState("ACTIVATE_CMD")
            ).Else(
                NextValue(self.odt_sig, 1),
                NextValue(counter, counter - 1)
            )
        )
        dram_fsm.act("ACTIVATE_CMD",
            NextValue(self.current_command, cmd_activate),
            #So for example, activate row 50, bank 3
            NextValue(self.a_sig, 50),
            NextValue(self.b_sig, 3),
            NextState("WRITE_EX_A")
        )
        dram_fsm.act("WRITE_EX_A",
            NextValue(self.current_command, cmd_write),
            # Starting write location: column 8
            NextValue(self.a_sig, 0b0000000001000),
            NextState("NO_OP_1")
        )
        # Wait a period for tRSD (15 ns) plus any extra time for WL = AL + CL - 1
        # (If AL = 0, CL = 5, then WL = 4 clock cycles)
        dram_fsm.act("NO_OP_1",
            NextValue(self.current_command, cmd_no_op),
            NextValue(self.a_sig, 0),
            NextState("NO_OP_2")
        )
        dram_fsm.act("NO_OP_2",
            NextValue(self.current_command, cmd_no_op),
            NextValue(self.dqs, 0),
            NextState("NO_OP_3")
        )
        dram_fsm.act("NO_OP_3",
            NextValue(self.current_command, cmd_no_op),
            NextValue(self.dqs, 1),
            NextValue(self.done_init, 1),
            NextValue(self.dq_sig, 2),
            NextState("DQS_GET_1")
        )
        dram_fsm.act("DQS_GET_1",
            NextValue(self.current_command, cmd_no_op),
            NextValue(self.dqs, 1),
            NextValue(self.done_init, 2),
            NextValue(self.dq_sig, 6,),
            NextState("DQS_GET_2")
        )
        dram_fsm.act("DQS_GET_2",
            NextValue(self.current_command, cmd_no_op),
            NextValue(self.dqs, 1),
            NextValue(self.done_init, 0),
            NextValue(self.dq_sig, 0),
        )
        # Before a read command after a write command, we must 
        # wait some clock cycles for WTR, which is either
        # 2 or t_WTR/t_CK, whichever is greater. (t_WR is about 7.5 ns)
        dram_fsm.act("NO_OP_4",
            NextValue(self.current_command, cmd_no_op),
            NextState("NO_OP_5")
        )
        dram_fsm.act("NO_OP_5",
            NextValue(self.current_command, cmd_read),
            # Starting read location: column 8
            NextValue(self.a_sig, 0b0000000001000),
            NextState("READ_CMD")
        )
        # Wait for RL = AL + CL, after which the DDR2 will control the
        # signal DQS to signify the data is ready to read.
        # Each edge of DQS will tell when the data from the starting
        # column is ready to read.
        dram_fsm.act("READ_CMD",
            NextValue(self.current_command, cmd_no_op),
            NextState("END_SIM")
        )
        
        dram_fsm.act("END_SIM",
            NextState("END_SIM")
        )
        

        neg_fsm = ClockDomainsRenamer("neg")(FSM(reset_state = "INIT_STATE"))
        neg_fsm.act("INIT_STATE",
            NextValue(counter_example, counter_example + 1),
            If(self.done_init == 1,
                NextValue(self.dqs, 0),
                NextValue(self.dq_sig, 4)
            ).Elif(self.done_init == 2,
                NextValue(self.dqs, 0),
                NextValue(self.dq_sig, 8)
            ),
            NextState("INIT_STATE")
        )
        # self.sync.neg += [If(self.done_init == 1,
        #                     self.dqs.eq(0),
        #                     self.dq_sig.eq(4)
        #                 ).Elif(self.done_init == 2,
        #                     self.dqs.eq(0),
        #                     self.dq_sig.eq(8)
        #                 )]
        




if __name__ == '__main__':
    # Core Simulation
    print("Core Simulation")

    dut = Core()

    def dut_tb(dut):
        for i in range(25000):
            yield

    run_simulation(dut, dut_tb(dut), vcd_name="core.vcd")

#####################################

# module = MemExample()

# # Build

# platform.build(module)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
