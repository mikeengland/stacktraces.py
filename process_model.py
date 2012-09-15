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

import sys

LVL_SHOW_PROCESSES = 0
LVL_SHOW_THREADS = 1
LVL_SHOW_FRAMES = 2
LVL_SHOW_ARGS = 3
LVL_SHOW_VARS = 4

class thread:

    def __init__(self, tid):
        self.tid = tid
        self.frames = []
        self.name = None
        self.state = None
        self.exited = False

    def __str__(self):
        s = ''
        s += '[%s]' % self.tid
        s += ' '
        if self.name:
            s += self.name
            s += ' '
        if self.state:
            s += '(%s) ' % self.state
        s += '\n  '
        for f in self.frames:
            s += f.__str__()
            s += ', '
        return s

    def describe(self, level = 0):
        if level < LVL_SHOW_FRAMES:
            return self.__str__()
        s = ''
        s += '[%s]' % self.tid
        s += ' '
        if self.name:
            s += self.name
            s += ' '
        if self.state:
            s += '(%s) ' % self.state
        s += '\n'
        for f in self.frames:
            s += ' ' + f.describe(level)
        return s

    def set_exited(self, flag = True):
        self.exited = flag

    def add_frame(self, frame):
        self.frames.append(frame)

    def set_name(self, name):
        self.name = name

    def set_state(self, state):
        self.state = state

    def same_backtrace(self, thr2):
	if len(self.frames) != len(thr2.frames):
	    return False
        for i in range(len(self.frames)):
	    if self.frames[i].fn != thr2.frames[i].fn:
		return False
	return True

class threadgroup:
    """ group of threads with same characteristics, such as active frames """

    def __init__(self, thr):
	self.count = 0
	self.threads = [thr]

    def __str__(self):
	return self.threads[0].__str__()

    def add_thread(self, thr):
	self.threads.append(thr)

class process_group:

    def __init__(self):
        self.processes = []

    def add_process(self, proc):
        self.processes.append(proc)

    def __str__(self):
        s = ''
        for p in self.processes:
            s += p.__str__()
            s += '\n'
        return s

    def describe(self, level = 0):
        if level >= 1:
            s = ''
            for p in self.processes:
                s += p.describe(level)
                s += '\n'
            return s
        else:
            return self.__str__()

class process:

    def __init__(self, pid = None):
        self.pid = pid
        self.threads = []
	self.threadgroups = []

    def __str__(self):
        s = ''
        for tg in self.threadgroups:
	    s += '%d * ' % len(tg.threads)
            s += tg.__str__()
            s += '\n'
        return s

    def describe(self, level = 0):
        if level >= 1:
            s = ''
            for t in self.threads:
                s += t.describe(level)
                s += '\n'
        else:
            s = self.__str__()
        return s
            
    def add_thread(self, thr):
        self.threads.append(thr)

    def group(self):
	for t in self.threads:
            if t.exited:
                continue
	    found = False
	    for g in self.threadgroups:
		if t.same_backtrace(g.threads[0]):
		    g.add_thread(t)
		    found = True
		    break
	    if not found:
		self.threadgroups.append(threadgroup(t))

    def get_pid(self):
        return self.pid

class frame:

    def __init__(self, id, fn, args = None):
        self.id = id
        self.fn = fn
        self.args = args;
        self.vars = {}

        if '@@GLIBC' in fn:
            self.fn = fn[:fn.index('@@GLIBC')]

    def __str__(self):
        return self.fn

    def describe(self, level = 0):
        if level < LVL_SHOW_ARGS:
            return self.__str__()
        s = '#%s %s' % (self.id, self.fn)
        if level >= LVL_SHOW_ARGS and self.args:
            s += self.args
        s += '\n'
        if level >= LVL_SHOW_VARS and len(self.vars):
            for k in self.vars.keys():
                s += '  %s=%s\n' % (k, self.vars[k])
        return s

    def add_var(self, var, val):
        self.vars[var] = val

if __name__ == "__main__":
    print >> sys.stderr, "Don't run this directly."
