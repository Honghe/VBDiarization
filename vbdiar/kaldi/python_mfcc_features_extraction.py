# -*- coding: utf-8 -*-
import numpy as np
import speechpy
from scipy.io import wavfile

from python_speech_features import mfcc


class PythonMFCCFeatureExtraction():
    def __init__(self):
        pass

    def audio2features(self, input_path):
        (rate, sig) = wavfile.read(input_path)
        mfcc_feat = mfcc(sig, dither=0, highfreq=7700, useEnergy=True, wintype='povey', numcep=23)
        # TODO temporarily add 2 feats to meet Kaldi_mfcc_features_extraction API
        mfcc_feat = np.append(mfcc_feat, [mfcc_feat[-1]], axis=0)
        mfcc_feat = np.append(mfcc_feat, [mfcc_feat[-1]], axis=0)
        mfcc_cmvn = speechpy.processing.cmvnw(mfcc_feat, win_size=301, variance_normalization=False)
        return mfcc_cmvn.astype(np.float32)
