import pandas as pd 
import sumolib 
import sys 

def prep_sources_targets(origs_path, dest_path, net_path):
    '''
    Reads and prepares the source and target ids from prepared origins and destinations
    '''

    # read origins first
    origs = pd.read_csv(origs_path, usecols=[1])
    origs.rename(columns={'id': 'orig_id'}, inplace=True)
    origs_arr = origs.values

    # read destinations
    dests = pd.read_csv(dest_path, usecols=[1])
    dests.rename(columns={'id': 'orig_id'}, inplace=True)
    dests = dests.values

    # read net file 
    net = sumolib.net.readNet(net_path)

    return origs, dests, net

def main(out_path):
    '''
    '''
    return 0
