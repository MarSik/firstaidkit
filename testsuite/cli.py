# First Aid Kit - diagnostic and repair tool for Linux
# Copyright (C) 2008 Joel Granados <jgranado@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import unittest, subprocess, os, os.path, difflib, exceptions

clioutputdir="testsuite/cli/outputs"
class Cli(unittest.TestCase):
    def generateDiff(self, args, filename):
        fd = os.open(os.path.join(clioutputdir, filename+".current"), \
                os.O_WRONLY|os.O_CREAT)
        subprocess.Popen(args, stdout=fd).wait()
        os.close(fd)

        fda = open(os.path.join(clioutputdir, filename+".current"), "r")
        fdb = open(os.path.join(clioutputdir, filename), "r")
        linesa = fda.readlines()
        linesb = fdb.readlines()
        fda.close()
        fdb.close()
        return difflib.unified_diff(linesa, linesb)


    def setUp(self):
        # All the diff objects will be in this list.
        self.udiffs = {}

        # We generate all the needed cli call files from a dict.
        # The key is considered the filename.
        self.clicallfiles = {
            "firstaidkit_-a" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-a"],
            "firstaidkit_-a_fix" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-a", \
                    "fix"],
            "firstaidkit_-a_nonexistent" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-a", \
                    "nonexistent"],
            "firstaidkit_-a_-x_plugincli1" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-a", \
                    "-x", "plugincli1"],
            "firstaidkit_-f_nonexistent" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-f", \
                    "nonexistent"],
            "firstaidkit_-f_plugincli1" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-f", \
                    "plugincli1"],
            "firstaidkit_-f_plugincli1_fix" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-f", \
                    "plugincli1", "fix"],
            "firstaidkit_-f_plugincli1_nonexistent" : \
                    ["./firstaidkit", "-P", "testsuite/cli/", "-f", \
                    "plugincli1", "nonexistent"]
            }

        for (key, arg) in self.clicallfiles.iteritems():
            self.udiffs[key] = self.generateDiff(arg, key)

    def tearDown(self):
        for (key, arg) in self.clicallfiles.iteritems():
            os.remove(os.path.join(clioutputdir, key+".current"))

class AutoExec(Cli):
    def testfirstaidkit__a(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-a"].next)

    def testfirstaidkit__a_fix(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-a_fix"].next)

    def testfirstaidkit__a_nonexistent(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-a_nonexistent"].next)

    def testfirstaidkit__a__x_plugincli1(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-a_-x_plugincli1"].next)



class FlowExec(Cli):
    def testfirstaidkit__f_nonexistent(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-f_nonexistent"].next)

    def testfirstaidkit__f_plugincli1(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-f_plugincli1"].next)

    def testfirstaidkit__f_plugincli1_fix(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-f_plugincli1_fix"].next)

    def testfirstaidkit__f_plugincli1_nonexistent(self):
        self.failUnlessRaises(exceptions.StopIteration, \
                self.udiffs["firstaidkit_-f_plugincli1_nonexistent"].next)



