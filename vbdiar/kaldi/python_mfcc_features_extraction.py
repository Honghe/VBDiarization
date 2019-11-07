# -*- coding: utf-8 -*-
from python_speech_features import mfcc
from scipy.io import wavfile
import numpy as np

class PythonMFCCFeatureExtraction():
    def __init__(self):
        pass

    def audio2features(self, input_path):
        (rate, sig) = wavfile.read(input_path)
        mfcc_feat = mfcc(sig, rate)
        # TODO temporarily add 2 feats to meet Kaldi_mfcc_features_extraction API
        mfcc_feat = np.append(mfcc_feat, [mfcc_feat[-1]], axis=0)
        mfcc_feat = np.append(mfcc_feat, [mfcc_feat[-1]], axis=0)
        return mfcc_feat
