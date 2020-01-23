#!/usr/bin/python3
from argparse import ArgumentParser, SUPPRESS
import os
import sys
import re
import subprocess
import pprint
import psutil
from pathlib import Path
from colorama import Fore
from colorama import Style

class PartMap:
    
    mountpoint = ""
    partition = ""
    pp = pprint.PrettyPrinter(indent=4)
    rows, columns = [int(i) for i in (os.popen('stty size', 'r').read().split())]
    outputmap = list()
    current_file = ""
    
    def __init__(self, args):

        if not args.fullscreen:
            self.rows = (args.rows if args.rows is not None else 50)
            self.columns = (args.columns if args.columns is not None else 200)
        else:
            self.rows -= 4
            self.columns -= 2

        self.mountpoint = args.mountpoint.rstrip('/')
        
        devices = list(filter(lambda x: (self.mountpoint in x.mountpoint), psutil.disk_partitions()))
        
        if len(devices) > 0:
            self.partition = devices[0].device
        
            self.outputmap = list()
            for i in range( (self.columns)*(self.rows) ):
                self.outputmap.append( 0 )
        else:
            raise ValueError('Mountpoint not found in Device Scan')

    @staticmethod
    def clear():
        """Clears the screen"""

        _ = subprocess.call('clear' if os.name == 'posix' else 'cls')
        
    def get_file_frag(self):
        
        root_directory = Path(self.mountpoint)
        for f in root_directory.glob('**/*'):
            if f.is_file() and all(ord(c) < 128 for c in str(f)):
                fileinfo = subprocess.check_output(
                    [
                        'filefrag', 
                        '-b512',
                        '-e',
                        str(f)
                    ],
                    stderr=None
                ).decode('ascii').split("\n")
                
                index = 0
                for i in fileinfo[3:-1]:
                    index += 1
                    fields = i.split(':')
                    if "Storage" not in fields[0]:                        
                        data = fields[2].split('.')[0]
                        
                        try:
                            maploc = int( int( data ) / 7814035087 *  ( ( int(self.columns) - 1 ) * ( int(self.rows) - 2 ) ) )
                            self.outputmap[ maploc ] =  int(self.outputmap[ maploc ]) + 1 

                        except Exception as e:
                            print(data)
                            print(self.outputmap)
                            print(str(maploc))
                            print(str(e))
                            print(str(f))
                            break
        self.current_file = ""
        procs = [
            p.info for p in psutil.process_iter(
                attrs=['pid', 'name', 'cmdline']
            ) if 'e4defrag' in p.info['name']
        ]
        
        for proc in procs:
            processes = subprocess.check_output(
                [
                    'lsof', 
                    '-e', '/run/user/1000/doc', 
                    '-e', '/run/user/1000/gvfs', 
                    '-Fn', 
                    '-p', 
                    str(proc['pid']), 
                    '-n'
                ],
                stderr=None
            ).decode('ascii').split("\n")

            for thread in processes:
                if "Storage" in thread and "." in thread:
                    if re.findall(r'Television|Movies', thread):
                        if os.path.isfile( str( thread[1:]).strip() ):
                            self.current_file = str(thread[1:]).strip()
                            print(self.current_file)
                            fileinfo = subprocess.check_output(
                                [
                                    'filefrag', 
                                    '-b512',
                                    '-e',
                                    str(self.current_file)
                                ],
                                stderr=None
                            ).decode('ascii').split("\n")
        
        
                            for i in fileinfo[3:-1]:
                                fields = i.split(':')
                                if len(fields) >= 3 and "Storage" not in fields[0] and fields[2] is not None:                        
                                    data = fields[2].split('.')[0]
                                    try:
                                        maploc = int( int( data ) / 7814035087 *  ( ( int(self.columns) - 1 ) * ( int(self.rows) - 2 ) ) )
                                        self.outputmap[ maploc ] =  -1

                                    except Exception as e:
                                        print(str(e))
                                        print(str(f))

    def output_map(self):
        results = ""
        results += ( (Style.BRIGHT + Fore.BLUE + chr(213) + "{}" + chr(184) + Style.RESET_ALL).format((self.columns)*chr(196)) )
        index = 0
        line = ""
        line += Style.BRIGHT + Fore.BLUE + chr(179) + Style.RESET_ALL
        maxval = int(max(self.outputmap))
        for c in self.outputmap:
            index += 1
            if int(c) == -1:
                line += Style.BRIGHT + Fore.MAGENTA + '#' + Style.RESET_ALL
            elif int(c) == 0:
                line += " "
            elif int(c) < maxval * ( 1 / 11 ):
                line += chr(249)
            elif int(c) < maxval * ( 2 / 11 ):
                line += ( Style.DIM + Fore.BLUE + chr(176) + Style.RESET_ALL)
            elif int(c) < maxval * ( 3 / 11 ):
                line += ( Style.BRIGHT + Fore.BLUE + chr(176) + Style.RESET_ALL)
            elif int(c) < maxval * ( 4 / 11 ):
                line += ( Style.DIM + Fore.CYAN + chr(176) + Style.RESET_ALL)
            elif int(c) < maxval * ( 5 / 11 ):
                line += ( Style.BRIGHT + Fore.CYAN + chr(176) + Style.RESET_ALL)
            elif int(c) < maxval * ( 6 / 11 ):
                line += ( Style.DIM + Fore.GREEN + chr(177) + Style.RESET_ALL)
            elif int(c) < maxval * ( 7 / 11 ):
                line += ( Style.BRIGHT + Fore.GREEN + chr(177) + Style.RESET_ALL)
            elif int(c) < maxval * ( 8 / 11 ):
                line += ( Style.DIM + Fore.YELLOW + chr(178) + Style.RESET_ALL)
            elif int(c) < maxval * ( 9 / 11 ):
                line += ( Style.BRIGHT + Fore.YELLOW + chr(178) + Style.RESET_ALL)
            elif int(c) < maxval * ( 10 / 11 ):
                line += ( Style.DIM + Fore.RED + chr(219) + Style.RESET_ALL)
            else:
                line += ( Style.BRIGHT + Fore.RED + chr(219) + Style.RESET_ALL)
           
            if index % self.columns == 0:
                line += Style.BRIGHT + Fore.BLUE + chr(179) + Style.RESET_ALL
                results += (str(line))
                line =  Style.BRIGHT + Fore.BLUE + chr(179) + Style.RESET_ALL
                results += ("\n")
                
        results += ( (Style.BRIGHT + Fore.BLUE + chr(192) + "{}" + chr(217) + Style.RESET_ALL).format((self.columns)*chr(196)) )
        
        if self.current_file != '':
            results += (self.current_file)
            results += ("\n")
            
        # PartMap.clear()
        sys.stdout.write( results )
        sys.stdout.flush()
        
    def str2bool(v):
        if isinstance(v, bool):
           return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
        
# Disable default help
parser = ArgumentParser(add_help=False)
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

# Add back help 
optional.add_argument(
    '-h',
    '--help',
    action='help',
    default=SUPPRESS,
    help='show this help message and exit'
)
required.add_argument('-m', '--mountpoint', required=True)
optional.add_argument('-r', '--rows', type=int)
optional.add_argument('-c', '--columns', type=int)
optional.add_argument('-f', '--fullscreen', type=PartMap.str2bool, nargs='?', const=True, default=False, help="Activate nice mode.")
args = parser.parse_args()


pm = PartMap(args)
pm.get_file_frag()
pm.output_map()
