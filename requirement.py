import subprocess

pyqt5 = ["pip", "install", "PyQt5"]
gitpython = ["pip", "install", "GitPython"]

### install PyQt5 gui package
print("{}".format(" ".join(pyqt5)), end="\n")
out = subprocess.check_output(pyqt5, shell = True)
print(out.decode(), end = "\n\n")

### install GitPython pacakage
print("{}".format(" ".join(gitpython)), end="\n")
out = subprocess.check_output(gitpython, shell = True)
print(out.decode(), end = "\n\n")