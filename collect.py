#!/usr/bin/env python

# Copyright 2012 Jeff Trawick, http://emptyhammock.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import subprocess
import sys
import tempfile

from optparse import OptionParser

def gdb_collect(outfilename, pid, corefile, exe):
    if outfilename:
        fn = outfilename
        outfile = open(fn, "w")
    else:
        (outfilefd, fn) = tempfile.mkstemp()
        outfile = os.fdopen(outfilefd, "w")

    (scrfilefd, scrfilename) = tempfile.mkstemp()
    scrfile = os.fdopen(scrfilefd, "w")
    print >> scrfile, 'info sharedlibrary'
    print >> scrfile, 'info threads'
    print >> scrfile, 'thread apply all bt full'
    if not corefile:
        print >> scrfile, 'detach'
    print >> scrfile, 'quit'
    scrfile.close()

    if pid:
        pid_or_core = str(pid)
    else:
        pid_or_core = corefile

    if not pid_or_core:
        raise Exception('Either a process id or core file must be provided')

    if not exe:
        raise Exception('An executable file must be provided')

    cmdline = ['/usr/bin/gdb',
               '-n',
               '-batch',
               '-x',
               scrfilename,
               exe,
               pid_or_core]

    try:
        rc = subprocess.call(cmdline, stdout=outfile, stderr=subprocess.STDOUT)
    except:
        raise Exception("couldn't run, error", sys.exc_info()[0])
    outfile.close()

    os.unlink(scrfilename)

    output = open(fn).readlines()
    if not outfilename:
        os.unlink(fn)

    return output

def pstack_collect(outfilename, pid, corefile):
    if outfilename:
        fn = outfilename
        outfile = open(fn, "w")
    else:
        (outfilefd, fn) = tempfile.mkstemp()
        outfile = os.fdopen(outfilefd, "w")

    pid_or_core = pid
    if not pid_or_core:
        pid_or_core = corefile

    if not pid_or_core:
        raise Exception('Either a process id or core file must be provided')

    cmdline = ['/usr/bin/pstack',
               pid_or_core]
    try:
        rc = subprocess.call(cmdline, stdout=outfile, stderr=subprocess.STDOUT)
    except:
        raise Exception("couldn't run, error", sys.exc_info()[0])
    outfile.close()

    output = open(fn).readlines()
    if not outfilename:
        os.unlink(fn)

    return output

def main():
    parser = OptionParser()
    parser.add_option("-o", "--outfile", dest="debuglog", type="string",
                      action="store",
                      help="specify file for debugger output")
    parser.add_option("-p", "--pid", dest="pid", type="int",
                      action="store",
                      help="specify process id to analyze")
#   parser.add_option("-f", "--follow", dest="follow",
#                     action="store_true",
#                     help="describe child processes too")
    parser.add_option("-e", "--exe", dest="exe", type="string",
                      action="store",
                      help="point to executable for process")
    parser.add_option("-c", "--corefile", dest="corefile", type="string",
                      action="store",
                      help="point to core file to examine")
    
    (options, args) = parser.parse_args()

    if not options.debuglog:
        parser.error("--outfile is required")

    mutually_exclusive = {"pid": "corefile",
#                         "follow": "corefile"
                          }

    for (k,v) in mutually_exclusive.items():
        if eval('options.' + k) and eval('options.' + v):
            parser.error("--%s and --%s are mutually exclusive" % (k, v))

    if 'sunos' in sys.platform:
        pstack_collect(options.debuglog, options.pid, options.corefile)
    else:
        gdb_collect(options.debuglog, options.pid, options.corefile, options.exe)

if __name__ == "__main__":
    main()
