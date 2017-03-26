""" Wrapper to TISEAN files.
"""

import tempfile
import subprocess
import os
from sys import platform as _platform
from time import strftime
import numpy as np
from collections import OrderedDict

__author__ = "Troels Bogeholm Mikkelsen"
__copyright__ = "Troels Bogeholm Mikkelsen 2016"
__credits__ = "Rainer Hegger, Holger Kantz and Thomas Schreiber"
__license__ = "MIT"
__version__ = "0.1"
__email__ = "bogeholm@nbi.ku.dk"
__status__ = "Development"

# Directory for temporary files
if "linux" in _platform:
    DIRSTR = '/tmp/'
elif _platform == "darwin":
    DIRSTR = '/private/tmp/'
# Prefix to identify these files
PREFIXSTR = 'pytisean_temp_'
# suffix - TISEAN likes .dat
SUFFIXSTR = '.dat'

# We will use the present time as a part of the temporary file name
def strnow():
    """ Return 'now' as a string with hyphenation
    """
    return strftime('%Y-%m-%d-%H-%M-%S')

def genfilename():
    """ Generate a file name.
    """
    return PREFIXSTR + strnow() + '_'

def _gen_tmpFolder():
    """ generate a temporary folder
    """
    return tempfile.mkdtemp(prefix=genfilename(),
                            dir=DIRSTR)

def gentmpfile():
    """ Generate temporary file and return file handle.
    """
    fhandle = tempfile.mkstemp(prefix=genfilename(),
                               suffix=SUFFIXSTR,
                               dir=DIRSTR,
                               text=True)
    return fhandle

def _output_parser_remover(command, outFile_base, legacy=True):
    """ Parser for output
    Some tisean command, like d2, output multiple files, to handle this case,
    wrapper will find each file and load each into a numpy array.

    In legacy mode:
        * for single-file-output command, an array is returned;
        * for multiple-file-output command, a dictionary with output filetype
          as keyword is returned;
    In non-legacy mode:
        * Dictionary of entry format
            {keyword:output_np_array}
          will be returned.
        * For single-file-output command, keyword is "out";
        * For multiple-file-output command, keyword is filetype of each output
          file

    This routine also takes over the temporary output file's removal
    """
    output_data = OrderedDict();
    if command == 'd2':
        outFile_c2 = outFile_base+'.c2'
        outFile_d2 = outFile_base+'.d2'
        outFile_h2 = outFile_base+'.h2'
        try:
            output_data['c2'] = np.loadtxt(outFile_c2)
            output_data['d2'] = np.loadtxt(outFile_d2)
            output_data['h2'] = np.loadtxt(outFile_h2)
        finally:
            os.remove(outFile_c2)
            os.remove(outFile_d2)
            os.remove(outFile_h2)
    else:
        try:
            if legacy:
                output_data = np.loadtxt(outFile_base)
            else:
                output_data['out'] = np.loadtxt(outFile_base)
        finally:
            os.remove(outFile_base)
    return output_data

def tiseanio(command, *args, data=None, silent=False, legacy=True):
    """ TISEAN input/output wrapper.

        Accept numpy array 'data' - run 'command' on this and return result.
        This function is meant as a wrapper around the TISEAN package.
    """
    # Return values if 'command' (or something else) fails
    res = None
    err_string = 'Something failed!'

    workspace = _gen_tmpFolder()

    # If user specifies '-o' the save routine below will fail.
    if '-o' in args:
        raise ValueError('User is not allowed to specify an output file.')

    # Handles to temporary files
    if data is not None:
        fullname_in = os.path.join(workspace, "inFile")
    fullname_out = os.path.join(workspace, "outFile")

    # If no further args are specified, run this
    if not args:
        commandargs = [command, '-o', fullname_out]
    # Otherwise, we concatenate the args and command
    else:
        # User can specify float args - we convert
        arglist = [str(a) for a in args]
        if data is not None:
            commandargs = [command, fullname_in] + arglist + ['-o', fullname_out]
        else:
            commandargs = [command] + arglist + ['-o', fullname_out]

    # We will clean up irregardless of following success.
    try:
        # Save the input to the temporary 'in' file
        if data is not None:
            np.savetxt(fullname_in, data, delimiter='\t')

        # Here we call TISEAN (or something else?)
        subp = subprocess.Popen(commandargs,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        # Communicate with the subprocess
        (_, err_bytes) = subp.communicate()
        # Read the temporary 'out' file
        res = _output_parser_remover(command, fullname_out, legacy)
        # We will read this
        err_string = err_bytes.decode('utf-8')

    # Cleanup
    finally:
        if data is not None:
            os.remove(fullname_in)
        try:
            os.rmdir(workspace)  # all leftover files within will be removed
        except OSError:
            print("Additional non-data files were created")
            if not silent:
                print("\tNonsilent mode chosen, displaying additional content:\n")
            for remnant_file in os.listdir(workspace):
                if not silent:
                    print("File {} contains:".format(remnant_file))
                    with open(os.path.join(workspace, remnant_file)) as remnant_content:
                        print(remnant_content.read())
                os.remove(os.path.join(workspace, remnant_file))
            os.rmdir(workspace)

    if not silent:
        print(err_string)

    # We assume that the user wants the (error) message as well.
    return res, err_string

def tiseano(command, *args, silent=False, legacy=True):
    """ TISEAN output wrapper.

        Run 'command' and return result.

        This function is meant as a wrapper around the TISEAN package.
    """
    return tiseanio(command, *args, data=None,
                    silent=silent, legacy=legacy)
