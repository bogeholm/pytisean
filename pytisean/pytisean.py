""" Wrapper to TISEAN files
"""

import tempfile
import subprocess
import os
from time import strftime
import numpy as np

__author__ = "Troels Bogeholm Mikkelsen"
__copyright__ = "Troels Bogeholm Mikkelsen 2016"
__credits__ = "Rainer Hegger, Holger Kantz and Thomas Schreiber"
__license__ = "MIT"
__version__ = "0.1"
__email__ = "bogeholm@nbi.ku.dk"
__status__ = "Development"

# Directory for temporary files
DIRSTRING = '/private/tmp/'
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

def gentmpfile():
    """ Generate temporary file and return file handle.
    """
    fhandle = tempfile.mkstemp(prefix=genfilename(),
                               suffix=SUFFIXSTR,
                               dir=DIRSTRING,
                               text=True)
    return fhandle

def tiseanio(command, *args, data=None, silent=False):
    """ TISEAN input/output wrapper.

        Accept numpy array 'data' - run 'command' on this and return result.
        This function is meant as a wrapper around the TISEAN package.
    """
    # Return values if 'command' (or something else) fails
    res = None
    err_string = 'Something failed!'

    # If user specifies '-o' the save routine below will fail.
    if '-o' in args:
        raise ValueError('User is not allowed to specify an output file.')

    # Handles to temporary files
    tf_in = gentmpfile()
    tf_out = gentmpfile()
    # Full names
    fullname_in = tf_in[1]
    fullname_out = tf_out[1]

    # If no further args are specified, run this
    if not args:
        commandargs = [command, '-o', fullname_out]
    # Otherwise, we concatenate the args and command
    else:
        # User can specify float args - we convert
        arglist = [str(a) for a in args]
        commandargs = [command, fullname_in] + arglist + ['-o', fullname_out]

    print(commandargs)

    # We will clean up irregardless of following success.
    try:
        # Save the input to the temporary 'in' file
        np.savetxt(fullname_in, data, delimiter='\t')

        # Here we call TISEAN (or something else?)
        subp = subprocess.Popen(commandargs,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        # Communicate with the subprocess
        (_, err_bytes) = subp.communicate()
        # Read the temporary 'out' file
        res = np.loadtxt(fullname_out)#, delimiter='\t')
        # We will read this
        err_string = err_bytes.decode('utf-8')

    # Cleanup
    finally:
        os.remove(fullname_in)
        os.remove(fullname_out)

    if not silent:
        print(err_string)

    # We assume that the user wants the (error) message as well.
    return res, err_string


def tiseano(command, *args, silent=False):
    """ TISEAN output wrapper.

        Run 'command' and return result.

        This function is meant as a wrapper around the TISEAN package.
    """
    # Return values if 'command' (or something else) fails
    res = None
    err_string = 'Something failed!'

    # Check for user specified args
    if '-o' in args:
        raise ValueError('User is not allowed to specify an output file.')

    # Handle to temporary file
    tf_out = gentmpfile()
    # Full names
    fullname_out = tf_out[1]

    # If no further args are specified, run this
    if not args:
        commandargs = [command, '-o', fullname_out]
    # Otherwise, we concatenate the args and command
    else:
        # User can specify float args - we convert
        arglist = [str(a) for a in args]
        commandargs = [command] + arglist + ['-o', fullname_out]

    # We will clean up irregardless of following success.
    try:
        # Here we call TISEAN (or something else?)
        subp = subprocess.Popen(commandargs,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=False)

        # Communicate with the subprocess
        (_, err_bytes) = subp.communicate()
        # Read the temporary 'out' file
        res = np.loadtxt(fullname_out)
        # We will read this
        err_string = err_bytes.decode('utf-8')

    # Cleanup
    finally:
        os.remove(fullname_out)

    if not silent:
        print(err_string)

    # We assume that the user wants the (error) message as well.
    return res, err_string


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    plt.ion()
    plt.close('all')

    # Generate 5000 iterates of the henon map
    henon, err = tiseano('henon', '-l5000')

    # Plot and prettyfi
    fig, ax = plt.subplots(1, 1)
    ax.scatter(henon[:, 0], henon[:, 1], color='k', s=0.1)
    ax.set_title('Henon map')
    ax.set_xlabel(r'$x$', fontsize=16)
    ax.set_ylabel(r'$y$', fontsize=16)

    # Generate some data and compute the autocorrelation
    N = 1000
    t = np.linspace(0, N/10*np.pi, N)
    x = np.sin(t) + 0.2*np.random.randn(N)
    acf, err = tiseanio('corr', '-D', 50, data=x)

    # Plot and prettyfi
    fig, ax = plt.subplots(2, 1)
    ax[0].set_title(r'Data and autodorrelation')
    ax[0].plot(t, x)
    ax[1].plot(acf[:, 0], acf[:, 1])
    ax[0].set_xlabel(r'$t$', fontsize=16)
    ax[0].set_ylabel(r'$x$', fontsize=16)
    ax[1].set_xlabel(r'Lag $k$', fontsize=16)
    ax[1].set_ylabel(r'ACF $\rho(k)$', fontsize=16)

    plt.draw()
