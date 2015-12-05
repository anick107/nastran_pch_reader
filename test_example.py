import nastran_pch_reader

parser = nastran_pch_reader.PchParser('test-data/sol101.pch')

# summary of the forces at the elements
for element in [3000, 3001]:
    print('Element force at %d' % element)
    for subcase in parser.get_subcases():
        forces = parser.get_forces(subcase)
        fx, fy, fz, mx, my, mz = forces[element]
        print('\t subcase',subcase, '=>', (fx, fy, fz))