import joblib
import numpy as np
from collections import Counter
from itertools import product

# -----------------------------------
# Load models and scalers
# -----------------------------------
xgb_model = joblib.load("xgb_model.pkl")
hybrid_model = joblib.load("hybrid_model.pkl")
scaler18 = joblib.load("scaler18.pkl")
scaler256 = joblib.load("scaler256.pkl")

print("ML model expects features:", xgb_model.n_features_in_)
print("Hybrid model expects features:", hybrid_model.n_features_in_)
print("Scaler18 features:", scaler18.mean_.shape[0])
print("Scaler256 features:", scaler256.mean_.shape[0])

# -----------------------------------
# Test feature extraction
# -----------------------------------
def gc_content(seq):
    return (seq.count("G") + seq.count("C")) / len(seq)

def kmer4(seq):
    kmers = [''.join(p) for p in product('ACGT', repeat=4)]
    counts = Counter([seq[i:i+4] for i in range(len(seq)-3)])
    return [counts.get(k, 0) for k in kmers]

def max_repeat(seq):
    max_r = 1
    curr = 1
    for i in range(1, len(seq)):
        if seq[i] == seq[i-1]:
            curr += 1
            max_r = max(max_r, curr)
        else:
            curr = 1
    return max_r

def extract_features(seq):
    seq = seq.upper()
    seq = ''.join([b for b in seq if b in "ACGT"])
    if len(seq) < 10:
        return None
    features = [gc_content(seq)]
    features.extend(kmer4(seq))  # 256 features
    features.append(max_repeat(seq))
    return np.array(features)

# Test sequence
seq = "ATGCGTACGTAGCTAGCTGA"
features = extract_features(seq)
print("Extracted features shape:", features.shape)
print("First 18 features (for ML):", features[:18])
