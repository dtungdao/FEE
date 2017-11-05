import os, sys
import math, re, random, time
import logging


FLS_OK = 0
FLS_NOT_OK = 1


class FlashSimulation():
	def __init__(self, fls_row_no, fls_col_no, mem_file_name, fls_page_size=256):
		self.mem_file_name = mem_file_name
		self.fls_page_size = fls_page_size
		self.fls_row_no = fls_row_no
		self.fls_col_no = fls_col_no
		self.mem_size = fls_col_no * fls_row_no
		self.logger = self.__Fls_LogSetup()
		
		if( ((self.mem_size % fls_page_size) != 0) or (self.mem_size < fls_page_size) ):
			self.logger.warn("mem_size % fls_page_size) != 0) or (mem_size < fls_page_size")
			raise Exception("FlashSimulation __init__ failed")
		
		if( os.path.isfile(mem_file_name) ):
			self.mem_arr = map(ord, open(mem_file_name, "rb").read())
		else:
			self.mem_arr = [0xFF] * self.mem_size
		
	def __Fls_LogSetup(self):
		logger = logging.getLogger(__name__)
		logger.setLevel(logging.INFO)
		
		# create a file handler
		handler = logging.FileHandler('fls_mem.log')
		handler.setLevel(logging.INFO)
		
		# create a logging format
		formatter = logging.Formatter('%(asctime)s [%(levelname)s} : %(message)s')
		handler.setFormatter(formatter)
		
		# add the handlers to the logger
		logger.addHandler(handler)
		
		return logger
	
	def __Fls_Confirmed(self, mem_file_name, data):
		mem_file = open(mem_file_name, "wb")
		
		# write as binary
		mem_file.write("".join(map(chr, data)))
		self.logger.info("__Fls_Confirmed called")
		
		mem_file.close()
		
	def Fls_Write(self, wdata, addr, write_time=0.001):
		data_len = len(wdata)
		
		if( addr > (self.mem_size - 1) ):
			return FLS_NOT_OK
		else:
			start_addr = addr
			end_addr = start_addr + data_len

			# Write on erased cells => sucess
			if( self.mem_arr[start_addr : end_addr] == ([0xFF] * data_len) ):
				self.mem_arr[start_addr : end_addr] = wdata
			# Write on un-erased cells => fail
			else:
				self.mem_arr[start_addr : end_addr] = random.sample(range(256), data_len)
				self.logger.warn("Fls_Write write check not fulfill")

		# simulate flash write delay
		time.sleep(write_time)
		self.__Fls_Confirmed(self.mem_file_name, self.mem_arr)
			
		return FLS_OK
		
	def Fls_Read(self, addr, data_len):
		if( addr > (self.mem_size - 1) ):
			return None
		else:
			start_addr = addr
			end_addr = start_addr + data_len
			
			return self.mem_arr[start_addr : end_addr]
			
	def Fls_Erase(self, addr, erase_time=0.6):
		if( addr <= (self.mem_size - 1) ):
			page_idx = addr / self.fls_page_size
			start_addr = page_idx * self.fls_page_size
			end_addr = start_addr + self.fls_page_size
			
			self.mem_arr[start_addr : end_addr] = [0xFF] * self.fls_page_size
			
			time.sleep(erase_time)
			self.__Fls_Confirmed(self.mem_file_name, self.mem_arr)
			
			return FLS_OK
		else:
			return FLS_NOT_OK
			
	def Fls_MassErase(self, erase_time=1):
		self.fls_array = [0xFF] * self.mem_size
		
		time.sleep(erase_time)
		self.logger.warn("Fls_MassErase called")
		self.__Fls_Confirmed(self.mem_file_name, self.mem_arr)
		
	def FlashArrayPrint(self, byte_per_line=32):
		print_buf = ""
		
		for addr in range(0, len(self.mem_arr), byte_per_line):
			print_buf += ">>> %08X | " % (addr)
			
			byte_cnt = 1
			for byte in self.mem_arr[addr : addr + byte_per_line]:
				print_buf += "%02X " % byte
				if ( (byte_cnt % 4) == 0 ): 
					print_buf += " "
				byte_cnt += 1
			print_buf += "\n"
			
		return print_buf.strip()
		
	
if __name__ == "__main__":
	fls_sim = FlashSimulation(fls_row_no=10, 
							  fls_col_no=1024, 
							  mem_file_name="fls.mem")
	
	fls_write_idx = 0;
	while(True):
		data_test = random.sample(range(256), random.randint(0, 100))
		
		if( (fls_write_idx + len(data_test)) <= (10*1024) ):
			fls_sim.Fls_Write(wdata=data_test, addr=fls_write_idx)
			fls_write_idx += len(data_test)
		else:
			print("Test finished !!!")
			break;
			
	print(fls_sim.FlashArrayPrint())