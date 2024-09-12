# Credit: Kevin Pedro (FNAL)

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from trigger_effs import thresholds
import mplhep as hep
hep.style.use("CMS")

mpl.rcParams.update({
    "axes.labelsize" : 18,
    "legend.fontsize" : 16,
    "xtick.labelsize" : 14,
    "ytick.labelsize" : 14,
    "font.size" : 18,
    "legend.frameon": True,
})

markers = ['v','o','^','s','d'] * 2

colors = ["#9c9ca1", "#e42536", "#5790fc", "#964a8b", "#f89c20", "#7a21dd", "#86c8dd", "#228B22", "#FFD700"]
info = {
    "axol1tl_score": {"xlabel": "AXOL1TL score", "title": "NN_v3"},
    "CICADA_score_v1p1p1": {"xlabel": "CICADA score", "title": "v1p1p1"},
    "CICADA_score_v1p1p2": {"xlabel": "CICADA score", "title": "v1p1p2"},
    "CICADA_score_v2p1p1": {"xlabel": "CICADA score", "title": "v2p1p1"},
    "CICADA_score_v2p1p2": {"xlabel": "CICADA score", "title": "v2p1p2"},
}

for key in info.keys():
    info[key]["rates"] = list(thresholds[key].keys()) if key in thresholds.keys() else [1, 5, 10]

def make_leg_extra(text):
    return Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0, label=text)

def make_leg(fig, ax,leg_loc,version,signame):
    leg_extra = [
        make_leg_extra("{} (124X, L1Nano)".format(version)),
        make_leg_extra(signame),
    ]
    handles, labels = ax.get_legend_handles_labels()
    handles = leg_extra + handles
    leg = ax.legend(handles=handles,framealpha=0.5,**leg_loc)
    if "bbox_to_anchor" in leg_loc: leg.get_frame().set_linewidth(0.0)
    lctr = 0
    for handle, label in zip(leg.legend_handles, leg.texts):
        if lctr>=len(leg_extra): break
        label.set_ha('left')
        label.set_position((-1.5*handle.get_window_extent(fig.canvas.get_renderer()).width, 0))
        lctr += 1

def plot_effs(signal,leg_loc,panels):
    for key in info:
        plot_eff(signal,key,"AD","ADonly",leg_loc,panels)
        plot_eff(signal,key,"best+AD","BESTandAD",leg_loc,panels)
        plot_eff(signal,key,"L1+AD","L1andAD",leg_loc,panels)

def plot_eff(signal,key,plttype,out,leg_loc,panels):
    results = signal["results"]
    columns = ["{}".format("best" if plttype in ["AD", "best+AD"] else "L1")]
    columns +=  ["{}" + "{}@{}kHz".format(plttype,rate) for rate in info[key]["rates"]]

    if not any(key in col for col in results.dtype.names):
        return

    heights = [6,3]
    if panels=="both":
        fig, axs = plt.subplots(nrows=2, sharex=True, figsize=(10,sum(heights)), gridspec_kw={"height_ratios":heights})
    else:
        fig, axs = plt.subplots(nrows=1, figsize=(10,heights[0]))
        axs = [axs]

    ctr = 0
    if panels=="both" or panels=="eff":
        axs[ctr].set_ylabel("Efficiency")
        axs[ctr].set_ylim(0,1)
        axs[ctr].grid(True)
        axs[ctr].grid(which='minor', alpha=0.4, axis='y')
        axs[ctr].grid(which='major', alpha=0.6, linestyle='-', zorder=-100)
        if panels=="both": ctr += 1

    if panels=="both" or panels=="ratio":
        axs[ctr].set_xlabel(signal["xlabel"])
        if panels=="both":
            axs[ctr].set_ylabel("{} / {}".format(columns[1].format("").split('@')[0],columns[0]))
        else:
            axs[ctr].set_ylabel("Efficiency gain from {}".format(key.split('_')[0].upper()))
        axs[ctr].grid(True)
        axs[ctr].grid(which='minor', alpha=0.4, axis='y')
        axs[ctr].grid(which='major', alpha=0.6, linestyle='-', zorder=-100)

    ratio_min = 1
    ratio_max = 0
    for i,col in enumerate(columns):
        col_leg = col.format("")
        if '+' in col_leg:
            col_leg = col_leg.split('+')[1]
            if panels!="ratio": col_leg = '+'+col_leg
        col_actual = col.format(key+"_")

        ctr = 0
        if panels=="both" or panels=="eff":
            axs[ctr].scatter(
                results["mass"], results[col_actual],
                s=200, marker=markers[i], facecolors='none', edgecolors=colors[i], linewidth=3, label=col_leg
            )
            if panels=="both": ctr += 1

        if (panels=="both" or panels=="ratio") and i>0:
            ratios = results[col_actual]/results[columns[0]]
            ratio_min = min(ratio_min, min(ratios))
            ratio_max = max(ratio_max, max(ratios))
            axs[ctr].scatter(
                results["mass"], ratios,
                s=200, marker=markers[i], facecolors='none' if panels=="both" else colors[i], edgecolors=colors[i], linewidth=3, label=col_leg
            )
    axs[ctr].set_ylim(ratio_min,ratio_max+(ratio_max-1)*.2)

    make_leg(fig, axs[0], leg_loc, info[key]["title"], signal["legname"])

    plotname = ""
    if panels=="both":
        plotname = "_and_ratio"
    elif panels=="ratio":
        plotname = "_ratio"
    hep.cms.label(label="Preliminary", rlabel="", ax=axs[0])
    plt.savefig('efficiency{}_{}_{}_{}.pdf'.format(plotname,out,signal["name"],key),bbox_inches='tight')

def plot_dists(signal,bkg,leg_loc):
    for key,val in signal["hists"].items():
        bkg_hist = None
        if bkg is not None and key in bkg["hists"]:
            bkg_hist = bkg["hists"][key][0]
        plot_dist(key,val,signal,leg_loc,bkg_hist)

def plot_dist(key,hists,signal,leg_loc,bkg=None):
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlabel(info[key]["xlabel"])
    ax.set_ylabel("Arbitrary units")
    ax.set_yscale("log")

    if bkg is not None:
        ax.hist(
            bkg["bins"][:-1], bkg["bins"], weights=bkg["counts"], histtype="step", density=True,
            color=colors[0], label="MinBias"
        )
    for im,mass in enumerate(signal["masses"]):
        hist = hists[mass]
        ax.hist(
            hist["bins"][:-1], hist["bins"], weights=hist["counts"], histtype="step", density=True,
            color=colors[im+1], label=signal["xlabel"].replace(" [GeV]"," = ")+str(mass)
        )

    if key in thresholds:
        for rate,cut in thresholds[key].items():
            ax.axvline(x=cut, color='k', linestyle='--')

    make_leg(fig, ax, leg_loc, info[key]["title"], signal["legname"])

    hep.cms.label(label="Preliminary", rlabel="", ax=ax)

    plt.savefig('{}_{}.pdf'.format(key,signal["name"]),bbox_inches='tight')

if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", type=str, required=True, help="suffix for output file")
    parser.add_argument("--plots", type=str, default="both", choices=["both","eff","dist"], help="plots to make")
    parser.add_argument("--panels", type=str, default="both", choices=["both","eff","ratio"], help="panels to show for efficiency plots")
    parser.add_argument("--leg", type=str, default="side", help="legend location")
    args = parser.parse_args()

    if args.leg=="side":
        args.leg = {"loc": "center left", "bbox_to_anchor": (1, 0.5)}
    else:
        args.leg = {"loc": args.leg}

    signals = getattr(__import__("trigger_eff_results_{}".format(args.output), fromlist=["signals"]), "signals")

    bkg = next((signal for signal in signals if signal["name"]=="bkg"),None)
    for signal in signals:
        if signal["name"]=="bkg":
            continue
        if args.plots=="both" or args.plots=="eff": plot_effs(signal,args.leg,args.panels)
        if args.plots=="both" or args.plots=="dist": plot_dists(signal,bkg,args.leg)
