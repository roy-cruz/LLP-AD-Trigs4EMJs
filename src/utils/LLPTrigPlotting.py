import matplotlib.pyplot as plt
import numpy as np
import os
import itertools
from pypdf import PdfMerger

colors = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # gray
    "#bcbd22",  # olive
    "#17becf",  # teal
    "#aec7e8",  # light blue
    "#ffbb78",  # light orange
    "#98df8a",  # light green
    "#ff9896",  # light red
    "#c5b0d5",  # light purple
    "#ff5f00",  # vivid orange
    "#ff00ff"   # magenta
]

markers = ['v','o','^','s','d', "*", "P", "X", ">", "<"] * 2

def plot_efficiencies(
    effs_dict, mMed_lst, ctau_lst, mDark_lst, trigs, 
    figsize=(12,8), 
    plotbest=True, 
    title="", 
    savefig=True, 
    outdir="./plots/LLPEffPlots", 
    outfname=None,
    unitymax=True,
    cleandir = True
):
    tempoutflist = []
    if savefig is False:
        plots = []

    for idx, (ctau, mDark) in enumerate(itertools.product(ctau_lst, mDark_lst)):
        print("Plotting: ctau = {}, mDark = {}".format(ctau, mDark))
        fig, ax = plt.subplots(figsize=figsize)
        maxeff = 0

        for i, trig in enumerate(trigs):
            effs = effs_dict[(ctau, mDark)][trig]
            if maxeff < max(effs): maxeff = max(effs)
            ax.plot(
                mMed_lst, effs, 
                label=trig, 
                marker=markers[i], linestyle="--", color=colors[i], markerfacecolor='none', markeredgecolor=colors[i], markersize=10.0, markeredgewidth=2
            )
        if plotbest: 
            ax.plot(
                mMed_lst, effs_dict[(ctau, mDark)]["best"], 
                label="best", 
                marker=markers[i+1], linestyle="--", color=colors[i + 1], markerfacecolor='none', markeredgecolor=colors[i+1], markersize=10.0, markeredgewidth=2
            )
            if max(effs_dict[(ctau, mDark)]["best"]) > maxeff: maxeff = max(effs_dict[(ctau, mDark)]["best"])


        # Changing plot aesthetics
        ax.set_title(title+f"($c\\tau$ = {ctau} mm, Dark Hadron Mass = {mDark} GeV)", fontsize=16)
        if unitymax:
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, maxeff * 1.05)
        ax.set_xlim(95, 2000)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.set_ylabel("Efficiency", fontsize=12)
        ax.set_xlabel("Z' Mediator Mass [GeV]", fontsize=12)
        ax.grid()
        fig.tight_layout()

        # Plot showing/saving
        if savefig:
            tempoutfname = f"plot{idx}.pdf"
            tempoutflist.append(tempoutfname)
            plt.savefig(os.path.join(outdir, tempoutfname))
        else: 
            plots.append((fig, ax))
            
    # Merging plots into a single PDF
    if savefig:
        if outfname is None: raise ValueError("No output file name provided.")
        print("Merging PDFs")
        merger = PdfMerger()
        for pdf in tempoutflist:
            merger.append(os.path.join(outdir, pdf))
        merger.write(os.path.join(outdir, outfname+".pdf"))
        merger.close()
        if cleandir: 
            clean_dir(tempoutflist, outdir)
    else:
        return plots


def plot_improvements(
    effs_dict, mMed_lst, ctau_lst, mDark_lst, trigs, 
    figsize=(12,8), 
    plotbest=True, 
    title="", 
    savefig=False, 
    outdir="./plots/", 
    outfname=None,
    unitymax=True,
    cleandir = True
):
    tempoutflist = []

    if savefig is False:
        plots = []

    for idx, (ctau, mDark) in enumerate(itertools.product(ctau_lst, mDark_lst)):
        print("Plotting: ctau = {}, mDark = {}".format(ctau, mDark))
        fig, (ax, ax_ratio) = plt.subplots(2, 1, figsize=figsize, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        maxeff = 0

        # Plotting 
        for i, trig in enumerate(trigs):
            effs = effs_dict[(ctau, mDark)]["best+"+trig]
            if maxeff < max(effs): maxeff = max(effs)
            ax.plot(
                mMed_lst, effs, label="best+"+trig, 
                marker=markers[i], linestyle="--", color=colors[i], markerfacecolor='none', markeredgecolor=colors[i], markersize=10.0, markeredgewidth=2
            )
            ratio = np.array(effs_dict[(ctau, mDark)]["best+"+trig])/np.array(effs_dict[(ctau, mDark)]["best"])
            ax_ratio.plot(mMed_lst, ratio, label="best+" + trig, marker=markers[i], linestyle="--", markersize=10.0, color=colors[i])
        
        if plotbest: 
            print("Printing best: " + str(effs_dict[(ctau, mDark)]["best_name"]))
            ax.plot(
                mMed_lst, effs_dict[(ctau, mDark)]["best"], label="best",
                marker=markers[i+1], linestyle="--", color=colors[i + 1], markerfacecolor='none', markeredgecolor=colors[i+1], markersize=10.0, markeredgewidth=2
            )

        if max(effs_dict[(ctau, mDark)]["best"]) > maxeff: maxeff = max(effs_dict[(ctau, mDark)]["best"])

        ax.set_title(title+f"($c\\tau$ = {ctau} mm, Dark Hadron Mass = {mDark} GeV)", fontsize=16)
        if unitymax:
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, maxeff * 1.05)
        ax.set_xlim(95, 2000)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.set_ylabel("Efficiency", fontsize=12)
        ax.grid()

        ax_ratio.set_xlabel("Z' Mediator Mass [GeV]", fontsize=10)
        ax_ratio.set_ylabel("best+LLP/best", fontsize=10)
        ax_ratio.tick_params(axis='both', which='major', labelsize=10)
        ax_ratio.grid()

        fig.tight_layout()

        if savefig:
            tempoutfname = f"plot{idx}.pdf"
            tempoutflist.append(tempoutfname)
            plt.savefig(os.path.join(outdir, tempoutfname))
        else:
            plots.append((fig, ax, ax_ratio))

    if savefig:
        if outfname is None: raise ValueError("No output file name provided.")
        print("Merging PDFs")
        merger = PdfMerger()
        for pdf in tempoutflist:
            merger.append(os.path.join(outdir, pdf))
        merger.write(os.path.join(outdir, outfname+".pdf"))
        merger.close()
        if cleandir:
            clean_dir(tempoutflist, outdir)
    else:
        return plots

def clean_dir(file_list, outdir):
    for file in file_list:
        f_name = os.path.join(outdir, file)
        if os.path.exists(f_name):
            os.remove(f_name)
            print(f"{f_name} has been deleted.")
        else:
            print(f"{f_name} does not exist.")