include makefile.mk 


SCRIPT = ./radiation_feedback.py
TXTFILES=$(wildcard *.txt)

nontmr: $(NON_TMR_LOG_LOG_FILES) $(NON_TMR_UART_LOG_FILES)
	python3 $(SCRIPT) --log-filenames $(NON_TMR_LOG_LOG_FILES) --uart-filenames $(NON_TMR_UART_LOG_FILES) --skip-uart-lines 67 > nontmr.txt

tmr: $(TMR_LOG_LOG_FILES) $(TMR_UART_LOG_FILES)
	python3 $(SCRIPT) --log-filenames $(TMR_LOG_LOG_FILES) --uart-filenames $(TMR_UART_LOG_FILES) --skip-uart-lines 67 > tmr.txt

nontmr_16_15_52:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16__15_52_14_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16__15_52_14_UART.log --skip-uart-lines 65 > $@.txt 

nontmr_16_15_57:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__15_57_38_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__15_57_38_UART.log --skip-uart-lines 65 > $@.txt 

nontmr_16_16_11:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__16_11_53_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__16_11_53_UART.log --skip-uart-lines 65 > $@.txt

nontmr_16_19_34:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__19_34_08_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__19_34_08_UART.log --skip-uart-lines 65 > $@.txt

nontmr_16_19_51:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__19_51_03_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__19_51_03_UART.log --skip-uart-lines 65 > $@.txt

nontmr_16_19_52:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__19_52_43_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__19_52_43_UART.log --skip-uart-lines 65 > $@.txt

nontmr_16_21_38:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__21_38_10_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__21_38_10_UART.log --skip-uart-lines 65 > $@.txt

nontmr_16_21_44:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__21_44_01_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_16_2022__21_44_01_UART.log --skip-uart-lines 65 > $@.txt

nontmr_17_07_36:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_17_2022__07_36_01_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_17_2022__07_36_01_UART.log --skip-uart-lines 65 > $@.txt

nontmr_17_08_30:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_17_2022__08_30_27_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_17_2022__08_30_27_UART.log --skip-uart-lines 65 > $@.txt

nontmr_17_11_41:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_17_2022__11_41_08_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_17_2022__11_41_08_UART.log --skip-uart-lines 65 > $@.txt

nontmr_19_10_32:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_19_2022__10_32_48_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_December_19_2022__10_32_48_UART.log --skip-uart-lines 65 > $@.txt

tmr_17_15_35:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_17_2022__15_35_49_UART.log --skip-uart-lines 65 > $@.txt

tmr_18_07_15:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__07_15_59_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__07_15_59_UART.log --skip-uart-lines 65 > $@.txt

tmr_18_07_26:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__07_26_49_UART.log --skip-uart-lines 65 > $@.txt

tmr_18_20_01:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__20_01_01_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__20_01_01_UART.log --skip-uart-lines 65 > $@.txt

tmr_18_21_03:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_18_2022__21_03_16_UART.log --skip-uart-lines 65 > $@.txt

tmr_19_07_57:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__07_57_13_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__07_57_13_UART.log --skip-uart-lines 65 > $@.txt

tmr_19_08_22:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__08_22_46_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__08_22_46_UART.log --skip-uart-lines 65 > $@.txt

tmr_19_08_39:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__08_39_03_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__08_39_03_UART.log --skip-uart-lines 65 > $@.txt

tmr_19_18_34:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_19_2022__18_34_25_UART.log --skip-uart-lines 65 > $@.txt

tmr_20_08_05:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_20_2022__08_05_34_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_20_2022__08_05_34_UART.log --skip-uart-lines 65 > $@.txt

tmr_20_17_47:
	python3 $(SCRIPT) --log-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_20_2022__17_47_55_LOG.log --uart-filenames ./tmp/CTRL/CTRL_ddr_11_28_tmr_December_20_2022__17_47_55_UART.log --skip-uart-lines 65 > $@.txt


clean:
	rm $(TXTFILES)