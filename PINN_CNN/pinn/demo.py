"""Quick diagnostic for NASA .mat structure — round 2."""
from scipy.io import loadmat

mat = loadmat("D:\\Repositories\\ScuderiaAMG\\PINN_CNN\\data\\nasa_pcoe\\B0005.mat")
b = mat["B0005"][0, 0]
print(f"Total cycles: {len(b['cycle'][0])}")

for i in range(len(b["cycle"][0])):
    t = b["cycle"][0, i]["type"][0]
    if hasattr(t, "decode"):
        t = t.decode()
    t = str(t).strip().lower()
    if t == "charge":
        d = b["cycle"][0, i]["data"][0, 0]
        print(f"\nFirst charge cycle (idx={i}):")
        print(f"  Fields: {list(d.dtype.names)}")

        # Show shapes of all fields
        for fname in d.dtype.names:
            val = d[fname]
            print(f"  {fname}: type={type(val)}, shape={val.shape}, dtype={val.dtype}")
            # If it's nested, dig deeper
            if val.shape == (1, 1) or val.shape == ():
                try:
                    inner = val[0, 0] if val.shape == (1, 1) else val[()]
                    print(f"    → inner: type={type(inner)}, shape={inner.shape if hasattr(inner, 'shape') else 'N/A'}")
                    if hasattr(inner, 'shape') and inner.shape == (1, 1):
                        inner2 = inner[0, 0]
                        print(f"    → inner2: type={type(inner2)}, shape={inner2.shape if hasattr(inner2, 'shape') else 'N/A'}")
                except Exception as e:
                    print(f"    → cannot unpack: {e}")

        # Also check discharge cycle for comparison
        for j in range(len(b["cycle"][0])):
            t2 = b["cycle"][0, j]["type"][0]
            if hasattr(t2, "decode"):
                t2 = t2.decode()
            if str(t2).strip().lower() == "discharge":
                d2 = b["cycle"][0, j]["data"][0, 0]
                print(f"\nFirst discharge cycle (idx={j}):")
                for fname in d2.dtype.names:
                    val = d2[fname]
                    print(f"  {fname}: type={type(val)}, shape={val.shape}, dtype={val.dtype}")
                    if val.shape == (1, 1) or val.shape == ():
                        try:
                            inner = val[0, 0] if val.shape == (1, 1) else val[()]
                            print(f"    → inner: type={type(inner)}, shape={inner.shape if hasattr(inner, 'shape') else 'N/A'}")
                            if hasattr(inner, 'shape') and inner.shape == (1, 1):
                                inner2 = inner[0, 0]
                                print(f"    → inner2: type={type(inner2)}, shape={inner2.shape if hasattr(inner2, 'shape') else 'N/A'}")
                        except Exception as e:
                            print(f"    → cannot unpack: {e}")
                break
        break
