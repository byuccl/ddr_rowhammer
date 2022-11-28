
from migen import *
from litex.soc.interconnect.csr import *

class VexRiscVDebug(Module, AutoCSR):

	def __init__(self, p_iclk100, mmcm_locked, i_addr, i_cyc, pll = None):
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

		# DRP port (copied from xilinx_common.py from 'expose_drp' in XilinxClocking)
		if pll:  # pll is reference to the PLL module
			self.drp_reset  = CSR()				# hooked up to what? (looks unconnected)
			self.drp_locked = CSRStatus()		# driven by PLL locked signal
			self.drp_read   = CSR()				# Causes a read to occur
			self.drp_write  = CSR()
			self.drp_drdy   = CSRStatus()
			self.drp_adr    = CSRStorage(7,  reset_less=True)
			self.drp_dat_w  = CSRStorage(16, reset_less=True)
			self.drp_dat_r  = CSRStatus(16)

			# # #

			den_pipe = Signal()			# enable signal (asserted when drp_read or drp_write asserted)
			dwe_pipe = Signal()			# Write enable signal (driven by drp_write)
			drp_drdy = Signal()

			pll.params.update(
				i_DCLK  = ClockSignal(),
				i_DWE   = dwe_pipe,  # internal signal
				i_DEN   = den_pipe,  # internal signal
				o_DRDY  = drp_drdy,  # internal signal
				i_DADDR = self.drp_adr.storage,    # from CSR
				i_DI    = self.drp_dat_w.storage,  # from CSR
				o_DO    = self.drp_dat_r.status    # status
			)
			self.sync += [
				# enable signal driven by a read or a write
				den_pipe.eq(self.drp_read.re | self.drp_write.re),	
				# DRP write enable
				dwe_pipe.eq(self.drp_write.re),
				# Status is read when not reading or writing
				If(self.drp_read.re | self.drp_write.re,
					self.drp_drdy.status.eq(0)
				).Elif(drp_drdy,
					self.drp_drdy.status.eq(1)
				)
			]
			self.comb += self.drp_locked.status.eq(pll.locked)   # locked status signal hooked up to DRP locked signal
			#self.logger.info("Exposing DRP interface within VexRiscV debug.")
