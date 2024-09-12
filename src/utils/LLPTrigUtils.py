import os
import uproot
import itertools
import awkward as ak

from .TrigUtils import genFileName

def compute_efficiencies(interestTrigs, data_dir, mMed_lst, mDark_lst, ctau_lst, channel, mode, unprescaled=[], excludedtrigs=[], entry_stop=-1):
    if mode not in ["L1", "HLT"]: raise ValueError("Mode must be either L1 or HLT")
    # menu = None
    effs_dict = {}
    
    for ctau, mDark in itertools.product(ctau_lst, mDark_lst):

        print("Loading sample: ctau = {}, mDark = {}".format(ctau, mDark))
        data_cache = {}
        effs_dict[(ctau, mDark)] = {}
        effs_dict[(ctau, mDark)][mode] = []

        for trig in interestTrigs: 
            if not trig.startswith(mode): raise ValueError("Mode does not match type of triggers given. Use HLT or L1 for mode.")

        # Load data
        for mMed in mMed_lst:
            data_file = os.path.join(data_dir, genFileName(mMed, mDark, ctau, channel=channel))
            data_cache[mMed] = uproot.open(data_file)["Events"].arrays(filter_name=mode + "_*", entry_stop=entry_stop)
        menu = data_cache[mMed_lst[0]].fields

        # Compute efficiencies
        print("Computing efficiency...")

        for trig in interestTrigs:
            effs_dict[(ctau, mDark)][trig] = []
            effs_dict[(ctau, mDark)]["best_name"] = []
            effs_dict[(ctau, mDark)]["best"] = []
            effs_dict[(ctau, mDark)]["best+" + trig] = []
            for mMed in mMed_lst:
                data = data_cache[mMed]
                
                # LLP alone
                denom = len(data)
                numrtr = ak.sum(data[trig])
                eff = numrtr / denom
                effs_dict[(ctau, mDark)][trig].append(eff)

                # best
                best_name = findBestTrig(data[menu], unprescaled=unprescaled, exclude=interestTrigs+excludedtrigs)
                numrtr = ak.sum(data[best_name])
                eff = numrtr / denom
                effs_dict[(ctau, mDark)]["best_name"].append(best_name)
                effs_dict[(ctau, mDark)]["best"].append(eff)

                # LLP + best
                numrtr = ak.sum(ak.any([data[trig], data[best_name]], axis=0))
                eff = numrtr / denom
                effs_dict[(ctau, mDark)]["best+" + trig].append(eff)

    return effs_dict

def findBestTrig(trig_rslts, unprescaled, exclude=[]):
    trigs_unprescaled = [trig for trig in trig_rslts.fields if trig not in exclude and trig in unprescaled]
    trues = [ak.sum(trig_rslts[trig]) for trig in trigs_unprescaled]
    best_idx = ak.argmax(trues)
    return(trigs_unprescaled[best_idx])

def printBestTrigs(effs_dict, printeff=True):
    for key in effs_dict.keys():
        best_names = effs_dict[key]["best_name"]
        best_effs = effs_dict[key]["best"]
        print("Best triggers for ctau = {} and dark hadron mass = {}:".format(key[0], key[1]))
        print(best_names)
        if printeff: print(best_effs)
        print()