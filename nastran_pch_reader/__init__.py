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


- quasi-static results
-- displacement
-- element forces for CBUSH, CELAS
-- MPCF
-- SPCF

"""
import cmath

CONST_VALID_REQUESTS = ['ACCELERATION', 'DISPLACEMENTS', 'MPCF', 'SPCF', 'ELEMENT FORCES', 'ELEMENT STRAINS']

def dispatch_parse(output, data_chunks):
    num = int(len(data_chunks) / 2)
    if len(data_chunks) % 2 != 0:
        raise ValueError('Wrong number of chunks!',
                         'Output: %s, num of chunks: %d' % (output, len(data_chunks)))

    if output == 'MAGNITUDE-PHASE':
        return [data_chunks[i]*cmath.exp(1j*data_chunks[i+num]) for i in range(num)]
    elif output == 'REAL-IMAGINARY':
        return [data_chunks[i] + 1j*data_chunks[i+num] for i in range(num)]
    else:
        return [data_chunks[i] for i in range(len(data_chunks))]


def parse_data_chunks(request, output, entity_type_id, data_chunks):
    if request in CONST_VALID_REQUESTS:
        return dispatch_parse(output, data_chunks)
    else:
        raise NotImplementedError("Request %s is not implemented", request)


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
        self.parsed_data = {'FREQUENCY': {}, 'SUBCASES': set()}
        for request in CONST_VALID_REQUESTS:
            self.parsed_data[request] = {}

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
                    self.parsed_data['SUBCASES'].add(self.current_subcase)

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
            if self.current_subcase not in self.parsed_data[self.request]:
                self.parsed_data[self.request][self.current_subcase] = {}
                self.parsed_data['FREQUENCY'][self.current_subcase] = {}

            if self.is_frequency_response:
                values = []
                # incremented by frequency, entity is given
                if self.output_sort == 2:
                    self.current_frequency = self.current_data_chunks[0]
                    values = self.current_data_chunks[1:]

                # incremented by entity, frequency is given
                elif self.output_sort == 1:
                    self.current_entity_id = int(self.current_data_chunks[0])
                    values = self.current_data_chunks[1:]

                # insert frequency in the database
                if self.current_frequency not in self.parsed_data['FREQUENCY'][self.current_subcase]:
                    self.parsed_data['FREQUENCY'][self.current_subcase][self.current_frequency] = len(self.parsed_data['FREQUENCY'][self.current_subcase])

                # ensure that this dictionary exists
                if self.current_entity_id not in self.parsed_data[self.request][self.current_subcase]:
                    self.parsed_data[self.request][self.current_subcase][self.current_entity_id] = []

                vector = parse_data_chunks(self.request, self.current_output, self.current_entity_type_id, values)
                self.parsed_data[self.request][self.current_subcase][self.current_entity_id].append(vector)

            else:
                self.current_entity_id = int(self.current_data_chunks[0])
                self.parsed_data[self.request][self.current_subcase][self.current_entity_id] = \
                    parse_data_chunks(self.request,
                                      self.current_output,
                                      self.current_entity_type_id,
                                      self.current_data_chunks[1:])

    def health_check(self):
        frequency_steps = []
        for subcase in self.parsed_data['SUBCASES']:
            frequency_steps.append(len(self.parsed_data['FREQUENCY'][subcase]))
        assert min(frequency_steps) == max(frequency_steps)

    def get_subcases(self):
        return sorted(self.parsed_data['SUBCASES'])

    def __get_data_per_request(self, request, subcase):
        self.health_check()
        if subcase in self.parsed_data[request]:
            return self.parsed_data[request][subcase]
        else:
            raise KeyError('%s data for subase %d is not found' % (request, subcase))

    def get_accelerations(self, subcase):
        return self.__get_data_per_request('ACCELERATION', subcase)

    def get_displacements(self, subcase):
        return self.__get_data_per_request('DISPLACEMENTS', subcase)

    def get_mpcf(self, subcase):
        return self.__get_data_per_request('MPCF', subcase)

    def get_spcf(self, subcase):
        return self.__get_data_per_request('SPCF', subcase)

    def get_forces(self, subcase):
        return self.__get_data_per_request('ELEMENT FORCES', subcase)

    def get_frequencies(self):
        return sorted(self.parsed_data['FREQUENCY'].keys())

