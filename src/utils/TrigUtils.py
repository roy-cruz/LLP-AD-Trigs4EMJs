"""
file_utils.py
By: Roy F. Cruz Candelaria
"""

def genFileName(mMed, mDark, ctau, channel="s"):
    return "step_NANOAODv12_{}-channel_mMed-{}_mDark-{}_ctau-{}_unflavored-down_n-1000_wScores.root".format(channel, mMed, mDark, ctau)