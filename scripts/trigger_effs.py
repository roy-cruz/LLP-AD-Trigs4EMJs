
# Credit: Kevin Pedro (FNAL)

import uproot as up
import awkward as ak
import numpy as np
import os, sys
from collections import defaultdict

thresholds = {
    "axol1tl_score": {
        1: 982.3125,
        5: 734.8125,
        10: 610.8125,
    },
    "CICADA_score_v1p1p1": {
        1: 16.575,
        5: 12.082,
        10: 10.910,
    },
    "CICADA_score_v2p1p1": {
        1: 11.871,
        5: 9.296,
        10: 8.549,
    },
    "CICADA_score_v2p1p2": {
        # 50: 127.0, 
        # 150: 121.0,
        # 300: 116.0,
        20: 131.0,
        50: 127.0,
        150: 121.0,
        300: 116.0,
        600: 113.0,
    },
}

ranges = {
    "axol1tl_score": (0,3000),
    "CICADA_score_v1p1p1": (0,25),
    "CICADA_score_v1p1p2": (0,200),
    "CICADA_score_v2p1p1": (0,25),
    "CICADA_score_v2p1p2": (0,200),
}

def get_effs(template, mass, unprescaled):
    f = up.open(template.format(mass))
    t = f["Events"]
    keys = [b for b in list(unprescaled) if b in t.keys()]
    ax_key = "axol1tl_score"
    ci_keys = ["CICADA_score_v1p1p1","CICADA_score_v1p1p2","CICADA_score_v2p1p1","CICADA_score_v2p1p2"]
    ad_keys = [ax_key]+ci_keys
    # account for potentially missing keys
    ad_keys = [k for k in ad_keys if k in t.keys()]
    arrays = t.arrays(ad_keys+keys)

    denom = t.num_entries
    def get_eff(numer):
        return float(numer)/float(denom)
    effs = {"mass": mass}

    pass_all = ak.any([arrays[k] for k in keys],axis=0)
    effs["L1"] = get_eff(ak.sum(pass_all))

    pass_best = ak.sum([arrays[k] for k in keys],axis=1)
    arg_best = ak.argmax(pass_best)
    effs["best"] = get_eff(pass_best[arg_best])
    l1_best_name = keys[arg_best]

    for ad_key in ad_keys:
        if ad_key not in thresholds: continue
        pass_ad = {}
        for rate,cut in thresholds[ad_key].items():
            pass_ad[rate] = arrays[ad_key]>=cut
            effs["{}_AD@{}kHz".format(ad_key,rate)] = get_eff(ak.sum(pass_ad[rate]))
            effs["{}_best+AD@{}kHz".format(ad_key,rate)] = get_eff(ak.sum(ak.any([pass_ad[rate],arrays[l1_best_name]],axis=0)))
            effs["{}_L1+AD@{}kHz".format(ad_key,rate)] = get_eff(ak.sum(ak.any([pass_ad[rate],pass_all],axis=0)))

    effs_dtype = {"names": list(effs.keys()), "formats": ['f8']*len(effs.keys())}
    effs_array = np.array([tuple(effs.values())],effs_dtype)

    hists = {}
    for ad_key in ad_keys:
        hists[ad_key] = np.histogram(arrays[ad_key], bins=50, range=ranges[ad_key])

    return l1_best_name, effs_array, hists

def get_effs_sig(signal, unprescaled):
    print(signal["name"])
    results = None
    all_hists = {}
    for mass in signal["masses"]:
        print(mass)
        best, effs, hists = get_effs(signal["template"], mass, unprescaled)
        print(best)
        if results is None:
            results = effs
        else:
            results = np.append(results,effs)
        for key,hist in hists.items():
            if key not in all_hists: all_hists[key] = {}
            all_hists[key][mass] = {"counts": list(hist[0]), "bins": list(hist[1])}

    signal["hists"] = all_hists
    signal["results"] = results

if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--signals", type=str, required=True, help="name of Python file containing list named signals")
    parser.add_argument("-o", "--output", type=str, required=True, help="suffix for output file")
    parser.add_argument("-m", "--prescales", type=str, required=True, help="prescale csv path")
    parser.add_argument("-p", "--path", type=str, required=False, help="directory where the output file will be saved", default=".")
    args = parser.parse_args()

    # get unprescaled triggers
    prescales = np.genfromtxt(fname=args.prescales, delimiter=',', dtype='i8,U128,i8,i8,i8,i8,i8,i8,i8,i8,i8', names=True)
    unprescaled = prescales["Name"][prescales["2E34"]==1]
   
    signals_file = os.path.basename(args.signals).replace(".py", "")
    sys.path.append(os.path.dirname(args.signals))
    signals = getattr(__import__(signals_file, fromlist=["signals"]), "signals")
    # signals = getattr(__import__(args.signals.replace(".py","").split("/")[-1], fromlist=["signals"]), "signals")
    for signal in signals:
        get_effs_sig(signal, unprescaled)

    output_file = os.path.join(args.path, "trigger_eff_results_{}.py".format(args.output))

    with open(output_file, 'w') as rfile:
        rfile.write("from numpy import array\n")
        rfile.write("signals = "+repr(signals))
