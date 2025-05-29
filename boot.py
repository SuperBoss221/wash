# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import os
def check_file_exists(filename):
    try:
        os.stat(filename) 
        return True
    except OSError:
        return False
print("version:1")
file_to_check = 'wash.txt'
if check_file_exists(file_to_check):
    os.remove('wash.py')
    os.rename(file_to_check, 'wash.py')
    print(f"UPDATE WASH")

file_to_check = 'main.txt'
if check_file_exists(file_to_check):
    os.remove('main.py')
    os.rename(file_to_check, 'main.py')
    print(f"UPDATE MAIN")