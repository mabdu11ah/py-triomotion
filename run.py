# Import modules
import sys, ctypes, platform, time

from ctypes import c_int, c_int32, c_int16, c_void_p, c_long, c_double, WINFUNCTYPE, POINTER
from ctypes.wintypes import LPCSTR

# Some people may be using python v2.x
try:
    input = raw_input
except NameError:
    pass

# Trio variables
TrioPC_Callback = WINFUNCTYPE(c_int, c_void_p, c_int, c_long, LPCSTR)

def triopc_callback(context, event_type, int_data, string_data):
    return 0

triopc_callback_delegate = TrioPC_Callback(triopc_callback)

# Use dll
trio = ctypes.windll.LoadLibrary('lib/TrioPC64.dll')

# Create the python call prototype for TrioPC_CreateContext
trio.TrioPC_CreateContext.argtypes = []
trio.TrioPC_CreateContext.restype = c_void_p

context = trio.TrioPC_CreateContext()
    
# Connect
def connect():
    # Get IP address
    ip_address = input('Please enter the IP address (shown on screen): ')
    
    print ("Context: " + str(context))

    # Create the python call prototype for TrioPC_SetHostAddress
    trio.TrioPC_SetHostAddress.argtypes = [c_void_p, LPCSTR]
    trio.TrioPC_SetHostAddress(context, LPCSTR(ip_address.strip().encode()))

    # Create the python call prototype for TrioPC_Open
    trio.TrioPC_Open.argtypes = [c_void_p, c_int32, c_int32, c_void_p, c_void_p]
    trio.TrioPC_Open.restype = c_int

    # Open connection
    if trio.TrioPC_Open(context, 2, 0, 0, triopc_callback_delegate) == 0:
        print("Cannot connect to controller")
        connect()

    # Print if connection status is positive
    print("Connected to controller")
    
    get_command()

# Ask user for commands on successful connection
def get_command():
    # Print commands
    commands = ["base", "axisparams", "vr"]
    print("Commands: BASE, VR, AXISPARAMS")

    # Ignore bad input
    message = input("Enter command: ")
    try:
        command = message.split()[0].lower()
    except e:
        print("Invalid Input")
        get_command()
    
    if (command in commands):
        process_command(command, message.lower().replace(command, "").strip())
    else:
        print("That is not a valid command!")
        get_command()

# Process input
def process_command(command, message):
    if (command == "base"):
        try:
            if (int(message) >= 0 and int(message) <= 31):
                trio.TrioPC_Base.argtypes = [c_void_p, c_int]
                trio.TrioPC_Base.restype = c_int
                if trio.TrioPC_Base(context, int(message)) == 0:
                    print("Failed to set base!")
                else:
                    print("Set BASE(" + int(message) + ")")
        except e:
            print("Usage: BASE base_number")
    elif (command == "vr"):
        try:
            number = message.split()[0]
            value = message.split()[1]
            print(number + " " + value)
            
            if (True):
                trio.TrioPC_SetVr.argtypes = [c_void_p, c_int, c_double]
                trio.TrioPC_SetVr.restype = c_int
                
                if trio.TrioPC_SetVr(context, int(number), int(value)) == 0:
                    print("Failed to change vr value!")
                else:
                    print("Set VR(" + number + ") to " + value)
        except e:
            print("Usage: VR vr_number vr_value")

    elif (command == "axisparams"):
        params = ["ATYPE", "P_GAIN", "I_GAIN", "D_GAIN", "OV_GAIN",
                  "VFF_GAIN", "UNITS", "SPEED", "ACCEL", "DECEL",
                  "CREEP", "JOGSPEED", "FE_LIMIT", "DAC", "SERVO",
                  "REP_DIST", "FWD_IN", "REV_IN", "DATUM_IN", "FH_IN",
                  "FS_LIMIT", "RS_LIMIT", "MTYPE", "NTYPE", "MPOS",
                  "DPOS", "FE", "AXISSTATUS", "VPSPEED"]

        for param in params:
            time.sleep(1)
            
            trio.TrioPC_GetVariable.argtypes = [c_void_p, LPCSTR]
            trio.TrioPC_GetVariable.restype = c_int

            value = trio.TrioPC_GetVariable(context, LPCSTR(param.encode()))
            
            if value == 0:
                    print("Failed to get axis param: " + param)
            else:
                print(value)
                
    get_command()


connect()


