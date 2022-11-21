
from migen import *
from litex.soc.interconnect.csr import *

class VexRiscVDebug(Module, AutoCSR):

	def __init__(self, p_iclk100, mmcm_locked, i_addr, i_cyc):
		print("Building DEBUG")
		self.mmcm_locked = mmcm_locked			# MMCM Locked signal
		self.i_addr = i_addr					# Instruction memory address (PC?)
		self.i_cyc = i_cyc						# Instruction memory cycle signal (wishbone)

		# Create a 32-bit CSR register for the core
		self.i_addr_status = CSRStatus(32, description="Instruction Address.")

		# Address latching. Latch address when cyc is high and cyc_d is low (i.e., start of cycle)
		# - This should occur in the "sys" clock domain
		self.i_addr_latch = Signal(32)
		self.i_cyc_d = Signal(1)
		self.load_addr = Signal(1)
		#self.sync.sys += self.i_cyc_d.eq(self.i_cyc)  	# One cycle delay
		self.sync += self.i_cyc_d.eq(self.i_cyc)  	# One cycle delay
		self.comb += self.load_addr.eq(self.i_cyc & ~self.i_cyc_d)
		#self.sync.sys += If(self.load_addr,self.i_addr_latch.eq(i_addr))
		self.sync += If(self.load_addr,self.i_addr_latch.eq(i_addr))
		self.comb += self.i_addr_status.status.eq(self.i_addr_latch)

		# Create a 32-bit CSR register for the MMCM locked counter
		# - This should occur in the 'clk100' clock domain
		self.mmcm_locked_count = CSRStatus(32, description="MMCM Locked Count.")
		self.mmcm_locked_count_i = Signal(32)

		self.clock_domains.cd_iclk100 = ClockDomain()  # Infers a clock domain name of "clk100"
		#clk100 = platform.request("clk100")          # get the top-level clock signal

		#self.comb += self.cd_iclk100.clk.eq(clk100)  # Note unqiue assignment for clocks
		self.comb += self.cd_iclk100.clk.eq(p_iclk100)  # Note unqiue assignment for clocks

		self.locked_d = Signal(1)
		self.locked_dd = Signal(1)
		self.locked_ddd = Signal(1)
		# NOte the specification of the iclk100 clock domain
		self.sync.iclk100 += self.locked_d.eq(mmcm_locked)
		self.sync.iclk100 += self.locked_dd.eq(self.locked_d)
		self.sync.iclk100 += self.locked_ddd.eq(self.locked_dd)
		self.sync.iclk100 += If(self.locked_dd ^ self.locked_ddd, 
			self.mmcm_locked_count_i.eq(self.mmcm_locked_count_i + 1))
		self.mmcm_locked_count.status.eq(self.mmcm_locked_count_i)
