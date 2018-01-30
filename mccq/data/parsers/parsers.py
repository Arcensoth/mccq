from mccq.data.parsers.v1_mccq_data_parser import V1MCCQDataParser

# instantiate a copy of each supported parser
PARSERS = {
    # v1: for all 1.13 snapshots so far (18w01a to 18w03b)
    'v1': V1MCCQDataParser()
}
