import itertools

# Lists of parameters to use
channel = ["s", "t"]
mMed_lst= [100, 250, 500, 750, 1000, 1500, 2000]
mDark_lst = [10, 20]
ctau_lst = [1, 100, 1000, 1500, 2000]
template = "/uscms/home/roycruz/nobackup/EMJ/analysis/data/step_NANOAODv12_{}-channel_mMed-{}_mDark-{}_ctau-{}_unflavored-down_n-1000_wScores.root"

signals = []

for chan, mDark, ctau in itertools.product(channel, mDark_lst, ctau_lst):
    signal = {
        "name": chan + "chan", 
        "legname": r"${}$-channel".format(chan),
        "masses": mMed_lst,
        "template": template.format(chan, "{}", mDark, ctau),
        "xlabel": r"${}$ Mass [GeV]".format("Z'" if chan == "s" else "\Phi")
    }
    signals.append(signal)
