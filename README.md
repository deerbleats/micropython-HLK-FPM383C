# micropython-HLK-FPM383C
#uart=1,rx=22,tx=23,freq=57600 \
from finger import FINGER
fp = FINGER()
fp.register_fingerprinter()
fp.verify_finger()
