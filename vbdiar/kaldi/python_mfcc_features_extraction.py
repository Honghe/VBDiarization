# -*- coding: utf-8 -*-
from python_speech_features import mfcc
from scipy.io import wavfile


class PythonMFCCFeatureExtraction():
    def __init__(self):
        pass

    def audio2features(self, input_path):
        (rate, sig) = wavfile.read(input_path)
        mfcc_feat = mfcc(sig, rate)
        return mfcc_feat
