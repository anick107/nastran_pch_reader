"""
Parser for the NASTRAN punch files.

Supported formats:
- frequency response analysis
-- displacement 
-- acceleration 
-- element forces for CBUSH, CELAS
-- MPCF
-- SPCF

Supported output types: real/imaginary, mag/phase
"""
import cmath


def dispatch_parse(labels, output, data_chunks):
    if len(data_chunks) / len(labels) != 1 and len(data_chunks) / len(labels) != 2:
        raise ValueError('Wrong number of chunks!',
                         'Output: %s, num of labels: %d, num of chunks: %d' % (output, len(labels), len(data_chunks)))

    if output == 'MAGNITUDE-PHASE':
        return {label: data_chunks[i]*cmath.exp(1j*data_chunks[i+len(labels)]) for i, label in enumerate(labels)}
    elif output == 'REAL-IMAGINARY':
        return {label: data_chunks[i] + 1j*data_chunks[i+len(labels)] for i, label in enumerate(labels)}
    else:
        return {label: data_chunks[i] for i, label in enumerate(labels)}


def parse_data_chunks(request, output, entity_type_id, data_chunks):
    # nodal requests
    if request in ['ACCELERATION', 'DISPLACEMENTS', 'MPCF', 'SPCF']:
        # define the labels
        if request == 'ACCELERATION' or request == 'DISPLACEMENTS':
            labels = ['TX', 'TY', 'TZ', 'RX', 'RY', 'RZ']
        else:
            labels = ['FX', 'FY', 'FZ', 'MX', 'MY', 'MZ']
        return dispatch_parse(labels, output, data_chunks)

    # elemental requests
    elif request == 'ELEMENT FORCES':
        if entity_type_id == 102:
            labels = ['FX', 'FY', 'FZ', 'MX', 'MY', 'MZ']
            return dispatch_parse(labels, output, data_chunks)

        elif entity_type_id == 11 or entity_type_id == 12:
            labels = ['ELAS']
            return dispatch_parse(labels, output, data_chunks)

        else:
            print('Not implemented:', request, output, entity_type_id)
            return


class PchParser:
    def reset_current_frame(self):
        self.current_data_chunks = []
        self.is_frequency_response = False
        self.output_sort = 0
        self.current_subcase = 0
        self.current_output = 0
        self.current_frequency = 0
        self.current_entity_id = 0
        self.current_entity_type_id = 0

    def __init__(self, filename):
        # define the dictionary
        self.parsed_data = {}

        # initiate current frame
        self.reset_current_frame()

        # start reading
        with open(filename, 'r') as pch:
            # read only first 72 characters from the punch file
            for line in pch:
                line = line[0:72]

                # reset all variables
                if line.startswith('$TITLE   ='):
                    # insert the last frame remaining in memory
                    self.insert_current_frame()
                    # reset the frame
                    self.reset_current_frame()

                # parse the subcase
                if line.startswith('$SUBCASE ID ='):
                    self.current_subcase = int(line[13:].strip())

                # identify NASTRAN request
                if line.startswith('$DISPLACEMENTS'):
                    self.request = 'DISPLACEMENTS'
                elif line.startswith('$ACCELERATION'):
                    self.request = 'ACCELERATION'
                elif line.startswith('$MPCF'):
                    self.request = 'MPCF'
                elif line.startswith('$SPCF'):
                    self.request = 'SPCF'
                elif line.startswith('$ELEMENT FORCES'):
                    self.request = 'ELEMENT FORCES'
                elif line.startswith('$ELEMENT STRAINS'):
                    self.request = 'ELEMENT STRAINS'

                # identify output type
                if line.startswith('$REAL-IMAGINARY OUTPUT'):
                    self.current_output = 'REAL-IMAGINARY'
                elif line.startswith('$MAGNITUDE-PHASE OUTPUT'):
                    self.current_output = 'MAGNITUDE-PHASE'
                elif line.startswith('REAL OUTPUT'):
                    self.current_output = 'REAL'

                # parse of frequency response results
                if line.find('IDENTIFIED BY FREQUENCY') != -1:
                    self.is_frequency_response = True
                    self.output_sort = 2
                elif line.find('$FREQUENCY =') != -1:
                    self.is_frequency_response = True
                    self.output_sort = 1

                # parse entity id
                if line.startswith('$POINT ID ='):
                    self.current_entity_id = int(line[11:23].strip())
                elif line.startswith('$ELEMENT ID ='):
                    self.current_entity_id = int(line[13:23].strip())
                elif line.startswith('$FREQUENCY = '):
                    self.current_frequency = float(line[12:28].strip())

                # parse element type
                if line.startswith('$ELEMENT TYPE ='):
                    self.current_entity_type_id = int(line[15:27].strip())

                # ignore other comments
                if line.startswith('$'):
                    continue

                if self.request == 0:
                    raise NotImplementedError('Unknown request in the frame',
                                              'Check request type for the following string: %s' % line)

                # start data parsing
                line = line.replace('G', ' ')
                if line.startswith('-CONT-'):
                    line = line.replace('-CONT-', '')
                    self.current_data_chunks += [float(_) for _ in line.split()]
                else:
                    # insert the last frame
                    self.insert_current_frame()

                    # update the last frame with a new data
                    self.current_data_chunks = [float(_) for _ in line.split()]

            # last block remaining in memory
            self.insert_current_frame()

    def insert_current_frame(self):
        # last block remaining in memory
        if len(self.current_data_chunks) > 0:
            if self.request not in self.parsed_data:
                self.parsed_data[self.request] = {}

            if self.current_subcase not in self.parsed_data[self.request]:
                self.parsed_data[self.request][self.current_subcase] = {}

            if self.is_frequency_response:
                # incremented by frequency, entity is given
                if self.output_sort == 2:
                    self.current_frequency = self.current_data_chunks[0]
                    values = self.current_data_chunks[1:]

                # incremented by entity, frequency is given
                else:
                    self.current_entity_id = int(self.current_data_chunks[0])
                    values = self.current_data_chunks[1:]

                # ensure that this dictionary exists
                if self.current_entity_id not in self.parsed_data[self.request][self.current_subcase]:
                    self.parsed_data[self.request][self.current_subcase][self.current_entity_id] = {}

                self.parsed_data[self.request][self.current_subcase][self.current_entity_id][self.current_frequency] = \
                    parse_data_chunks(self.request,
                                      self.current_output,
                                      self.current_entity_type_id,
                                      values)
            else:
                self.current_entity_id = int(self.current_data_chunks[0])
                self.parsed_data[self.request][self.current_subcase][self.current_entity_id] = \
                    parse_data_chunks(self.request,
                                      self.current_output,
                                      self.current_entity_type_id,
                                      self.current_data_chunks[1:])

    def get_data(self):
        return self.parsed_data
