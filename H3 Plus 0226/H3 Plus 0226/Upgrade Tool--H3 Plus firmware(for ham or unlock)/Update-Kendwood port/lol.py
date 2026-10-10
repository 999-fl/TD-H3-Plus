from pathlib import Path
import math
from collections import Counter

p = Path("TID-H3-Plus-1.0.47.fw")
data = p.read_bytes()

counts = Counter(data)
entropy = -sum(
    (n / len(data)) * math.log2(n / len(data))
    for n in counts.values()
)

print("Size:", len(data), "bytes")
print("First 64 bytes:", data[:64].hex(" "))
print("ASCII preview:", repr(data[:64]))
print("Entropy:", round(entropy, 4), "bits/byte")