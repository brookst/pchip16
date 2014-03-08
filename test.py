from pchip16 import VM, ROM
from os.path import join

FILE_PATH = join("data", "Bounce.c16")

if __name__=='__main__':
    with open(FILE_PATH, 'rb') as file_handle:
        rom = ROM(file_handle)
    print(rom.checksum)
    vm = VM(rom)
    print(hex(vm.program_counter))
    for _ in range(100000):
        vm.step()
        print(hex(vm.program_counter))
    print("Success!")
