# Copyright 2018-2021 Clemson University
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

def single_rate_entry(file):
    return {'type': 'single_rate', 'rate': float(file.readline().rstrip())}

def table_entry(file):
    n_entries = int(file.readline())
    t9 = []
    rate = []
    sef = []
    for n in range(n_entries):
        line = file.readline()
        words = line.split()
        if len(words) == 2:
            words.append("1")
        t9.append(float(words[0]))
        rate.append(float(words[1]))
        sef.append(float(words[2]))
    return {'type': 'rate_table', 't9': t9, 'rate': rate, 'sef': sef}

def non_smoker_fit(file):
    def read_data(file):
        line = file.readline()
        words = line.split()
        result = {}
        result['Zt'] = words[0]
        result['At'] = words[1]
        result['Zf'] = words[2]
        result['Af'] = words[3]
        result['Q'] = words[4]
        result['spint'] = words[5]
        result['spinf'] = words[6]
        result['TlowHf'] = words[7]
        result['Tlowfit'] = words[8]
        result['Thighfit'] = "10"
        result['acc'] = words[9]

        line = file.readline()
        words = line.split()
        result['a1'] = words[0]
        result['a2'] = words[1]
        result['a3'] = words[2]
        result['a4'] = words[3]
       
        line = file.readline()
        words = line.split()
        result['a5'] = words[0]
        result['a6'] = words[1]
        result['a7'] = words[2]
        result['a8'] = words[3]

        file.readline()

        return result

    n_fits = int(file.readline())

    data = {'type': 'non_smoker_fit'}

    fits = []

    for i in range(n_fits):
        note = file.readline().rstrip()
        if note == "":
            note = file.readline().rstrip()
        fit = read_data(file)
        fit['note'] = note
        fits.append(fit)

    data['fits'] = fits

    return data
        
def user_rate(file, delimiter):
    data = {'type': 'user_rate'}
    n_props = int(file.readline())
    n_tags = int(file.readline())
    for m in range(n_props):
        line = file.readline()
        if not delimiter:
            words = line.split()
        else:
            words = line.split(delimiter)
        key = words[0]
        s_prop = ""
        if n_tags == 0 or words[0] == "note":
            for n in range(1, len(words)):
                s_prop += " " + words[n].strip()
        elif n_tags == 1:
            key = (key, words[1].strip())
            for n in range(2, len(words)):
                s_prop += " " + words[n].strip()
        elif n_tag2 == 2:
            key = (key, words[1].strip(), words[2].strip())
            for n in range(3, len(words)):
                s_prop += " " + words[n].strip()
        else:
            print('Invalid number of property tags')
            exit()
        data[key] = s_prop.lstrip(' ')
    return data

def main():
            
    parser = argparse.ArgumentParser(
                description='Convert a reaction text file to XML'
             )

    parser.add_argument('in_text', metavar='in_text', help='input text file')
    parser.add_argument('out_xml', metavar='out_xml', help='output xml file')
    parser.add_argument('--user_delim', metavar='DELIM',
                        type=str, default="",
                        help="delimiter for user rate properties")
    parser.add_argument('--validate', dest='validate',
                        default=False, action='store_true',
                        help="validate the new XML (default: False)")

    args = parser.parse_args()

    new_xml = wx.New_Xml(xml_type = 'reaction_data')

    reactions = {}

    file = open(args.in_text)

    while True:
        reaction_type = file.readline().rstrip()

        if len(reaction_type) == 0:
            break

        reaction = wx.Reaction()

        if reaction_type == 'user_supplied_fit':
            key = file.readline().rstrip()

        reaction.source = file.readline().rstrip()

        n_reactants = int(file.readline())

        reactant = []

        for n in range(n_reactants):
            reaction.reactants.append(file.readline().rstrip())

        n_products = int(file.readline())

        products = []

        for n in range(n_products):
            reaction.products.append(file.readline().rstrip())

        if reaction_type == 'single_rate':
            reaction.data = single_rate_entry(file)
            file.readline()
        elif reaction_type == 'rate_table':
            reaction.data = table_entry(file)
            file.readline()
        elif reaction_type == 'non_smoker_fit':
            reaction.data = non_smoker_fit(file)
        elif reaction_type == 'user_supplied_fit':
            reaction.data = user_rate(file, args.user_delim)
            reaction.data['key'] = key
            file.readline()

        reactions[reaction.get_string()] = reaction

    new_xml.set_reaction_data(reactions)
    new_xml.write(args.out_xml)

    if args.validate:
        wx.Xml(args.out_xml).validate()

if __name__ == "__main__":
    main()
