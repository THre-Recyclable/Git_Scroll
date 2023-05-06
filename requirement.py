import subprocess

pyqt5 = ["pip", "install", "PyQt5"]

### install PyQt5 gui package
print("{}".format(" ".join(pyqt5)), end="\n")
out = subprocess.check_output(pyqt5, shell = True)
print(out.decode(), end = "\n\n")
