# Copyright 2018 Clemson University
#
# Author: Bradley S. Meyer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# To obtain a copy of the GNU General Public License,
# see <https://www.gnu.org/licenses/>.

import argparse
import wnutils.xml as wx

def single_rate_fission(in_file, data):
    data['rate_data'] = float(in_file.readline().strip())

def table_entry_fission(in_file, data):
    data['rate_data'] = []
    n_entries = int(in_file.readline())
    for n in range(n_entries):
        line = in_file.readline().strip()
        words = line.split()
        if len(words) == 2:
            words.append('1')
        data['rate_data'].append((words[0], words[1], words[2]))

def write_data(out_file, data):
    out_file.write(data['type'] + '\n')
    out_file.write(data['source'] + '\n')
    out_file.write(str(len(data['reactants'])) + '\n')
    for reactant in data['reactants']:
        out_file.write(reactant + '\n')
    out_file.write(str(len(data['products'])) + '\n')
    for product in data['products']:
        out_file.write(product + '\n')
    if data['type'] == 'single_rate':
        out_file.write(str(data['rate_data'] * data['factor']) + '\n')
    if data['type'] == 'rate_table':
        out_file.write(str(len(data['rate_data'])) + '\n')
        for tup in data['rate_data']:
            out_file.write(
                tup[0] + ' ' + str(float(tup[1]) * data['factor']) + tup[2]
                + '\n')
    out_file.write('\n')

def print_reaction(data):
    s = ''
    for i in range(len(data['reactants'])):
        s += data['reactants'][i]
        if i < len(data['reactants']) - 1:
            s += ' + '
        else:
            s += ' -> '
    for i in range(len(data['products'])):
        s += data['products'][i]
        if i < len(data['products']) - 1:
            s += ' + '

    print(s)

def print_nuclide_error(nuclide):
    s = '({0[0]}, {0[1]})'.format(nuclide)
    print(s + ' not present')

def main():
            
    parser = argparse.ArgumentParser(
                description='Convert a reaction text file to XML'
             )

    parser.add_argument('in_xml', metavar='in_xml', help='input nuclear xml')
    parser.add_argument('in_text', metavar='in_text', help='input text file')
    parser.add_argument('out_text', metavar='out_text', help='output text file')

    args = parser.parse_args()

    # Set nuclide hash

    xml = wx.Xml(args.in_xml)

    nuclides = {}

    nd = xml.get_nuclide_data()

    for sp in nd:
        nuclides[(str(nd[sp]['z']), str(nd[sp]['a']))] = sp

    # Read in reaction data

    in_file = open(args.in_text, "r")

    out_file = open(args.out_text, "w")

    while True:
        reaction_type = in_file.readline().strip()

        if not reaction_type:
            break

        data = {}
        data['type'] = reaction_type

        data['source'] = in_file.readline().strip()

        data['n_reactants'] = int(in_file.readline().strip())

        data['reactants'] = []

        zr = 0
        ar = 0

        for n in range(data['n_reactants']):
            line = in_file.readline()
            words = line.split()
            nuclide = (words[0], words[1])
            zr += int(words[0])
            ar += int(words[1])
            if nuclide in nuclides:
                data['reactants'].append(nuclides[nuclide])
            else:
                print_nuclide_error(nuclide)
                exit()
           
        if data['type'] == 'single_rate':
            single_rate_fission(in_file, data)
        elif data['type'] == 'rate_table':
            table_entry_fission(in_file, data)
        else:
            print('Invalid rate type')
            exit()

        while True:
            line = in_file.readline().strip()
            if line:
                words = line.split()
                data['products'] = []
                zp = 0
                ap = 0
                for i in range(0, len(words) - 1, 2):
                    nuclide = (words[i], words[i+1]) 
                    zp += int(words[i])
                    ap += int(words[i+1])
                    if nuclide in nuclides:
                        data['products'].append(nuclides[nuclide])
                    else:
                        print_nuclide_error(nuclide)
                        exit()
                if not(zr == zp and ar == ap):
                    print('Invalid reaction: ' )
                    print_reaction(data)
                    exit()
                data['factor'] = float(words[len(words)-1])

                write_data(out_file, data)
            else:
                break


if __name__ == "__main__":
    main()
