#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import tidy
import keyword



def prepare_files(filename, newfilename):

    # first strip comments using stripcmt
    os.system("stripcmt %s > %s" % (filename, "struct2class.h-o"))

    # strip commas and semicolons using sed
    os.system("sed -i -e 's/,/ /g' struct2class.h-o")
    os.system("sed -i -e 's/;/ /g' struct2class.h-o")


    f = open("struct2class.h-o", "r")
    pyout = open(newfilename, "w")

    return f, pyout

def cleanup():
    '''
    remove the temporary files 
    '''

    i = os.system("rm -f struct2class.h-o struct2class.h-o-e")

    return i


class header:

    def __init__(
        self,
        name,
        variables,
        types,
        ):
        self.name = name
        self.variables = variables
        self.types = types

def strip(character, string):
    ''' strip a character from a string'''
    new_string = ""
    for s in string:
        if s != character:
            new_string += s
    return new_string


def strip_brackets(s, opening='[', closing=']'):
    '''
....remove anything between a set of brackets e.g x[1]
....from a string
....'''

    safe = True

    s_new = ''

    for i in range(len(s)):

        if s[i] == opening:
            safe = False

        if safe:
            s_new += s[i]

        if s[i] == closing:
            safe = True

    return s_new


def convert_h_to_classes(f, pyout):
    '''
....Read a file object f, which is a C file containing structure definitions,
....and output to a file pyout which will contain class definitions
....with the same names, and any #define statements as variables 
....'''

    klist = np.array(keyword.kwlist)    # list of python keywords

    defs_array = np.array([])
    defvals_array = np.array([])
    structures = []
    nstructs = 0

    typedefs = np.array([])

    inbrack = False
    instruct = False

    for line in f:

        # strip any brackets and what they contain

        line2 = strip_brackets(line)

        data = line2.split()

        if len(data) > 0:

            # then this line contains information

            # check if we ar einside a structure. If so we want to record values

            if instruct:
                if data[0] == '{':
                    inbrack = True
                elif data[0] == '}':
                    inbrack = False
                    instruct = False


            if data[0] == '#define':  # we have a define statement

                defname = data[1]
                defval = data[2]

                defs_array = np.append(defs_array, defname)
                defvals_array = np.append(defvals_array, defval)

            if data[0] == 'struct' or data[0] == 'typedef':  # we have a structure declaration

                # it's a structure- check it doesnt correspond to an already assigned typedef
                if data[0] == 'struct':
                    structname = data[1]
                    check = typedefs == structname
                    check_for_typedef = np.sum(check)

                # its a typedef
                elif data[0] == 'typedef' and data[1] == 'struct':
                    structname = data[2]
                    check = typedefs == structname
                    check_for_typedef = np.sum(check)
                    typedefs = np.append(typedefs, structname)

                # check we havent already created a class for it. If not, stick it in the array
                if check_for_typedef == 0:
                    structures.append(header(structname, [], []))
                    nstructs += 1
                    instruct = True

                print 'found structure %i, name %s. Creating class.' % (nstructs,
                        structname)




            if instruct and inbrack:

            # we have a variable in the structure

                if data[0] == 'int' or data[0] == 'double' or data[0] \
                    == 'char' or data[0] == 'long' or data[0] \
                    == 'float':

                    # check there are no brackets left

                    i_bracks_open = line2.find('[')

                    if i_bracks_open != -1:
                        print 'Error, found bracket in line which should be stripped'

                    # store the variables in an array

                    for i in range(len(data[1:])):

                        var = data[i + 1]

                        t = data[0]

                        # check if its a pointer, remove * and comment on it
                        if "*" in var:
                            var = strip("*", var)
                            t = "pointer, " + t

                        # finally, check if it is a python keyword
                        check = (klist == var)
                        if np.sum(check) > 0:   # it's a keyword, so add a _
                            var = "_" + var


                        structures[nstructs
                                   - 1].variables.append(var)
                        structures[nstructs - 1].types.append(t)

    pyout.write('''

#definitions from C
''')
    for i in range(len(defs_array)):
        pyout.write('%s = %s\n' % (defs_array[i], defvals_array[i]))
    pyout.write('''



''')

    pyout.write('''

#structures from C as py classes
''')

    for i in range(len(structures)):

        if len(structures[i].variables) > 0:

            classname = structures[i].name

            pyout.write('''
class %s:
''' % classname)

            pyout.write('\tdef __init__(self')

            for j in range(len(structures[i].variables)):
                pyout.write(', %s' % structures[i].variables[j])

            pyout.write('):\n')

            for j in range(len(structures[i].variables)):

                pyout.write('\t\tself.%s = %s    #type %s\n'
                            % (structures[i].variables[j],
                            structures[i].variables[j],
                            structures[i].types[j]))

            pyout.write('''

    ''')
    pyout.close()

    try:
        tidy.tidy_up (file_in=pyout.name, file_out=pyout.name)        # use tidy module to tidy up
    except SyntaxError:
        print "Error: syntax error when trying to tidy code. Can't deal with this."


    


if len(sys.argv) < 2:
    print "Not enough arguments, exiting."
    sys.exit(0)

filename = sys.argv[1]
newfilename = sys.argv[2]

(hfile, clsfile) = prepare_files(filename, newfilename)

convert_h_to_classes(hfile, clsfile)

cleanup()

