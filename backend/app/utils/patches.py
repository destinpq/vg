import sys
import numpy as np
from collections import abc

# This fix was previously for madmom, but we're now using librosa
# Keeping it for compatibility with any code that might rely on it
sys.modules['collections'].MutableSequence = abc.MutableSequence

# Fix np.float and np.int deprecation
np.float = float
np.int = int 