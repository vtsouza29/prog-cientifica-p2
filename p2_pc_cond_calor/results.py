import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import json
import scipy.interpolate

def readJSON(_filename):
    data = json.load(open(_filename))
    return data

resultado = readJSON("output.json")

temps = resultado["x"][0]

vpoints = int(resultado["vpoints"])
hpoints = int(resultado["hpoints"])

xs = resultado["xs"][0]
ys = resultado["ys"][0]

fig, (ax1, ax2) = plt.subplots(nrows=2)

n = 1000
xi = np.linspace(min(xs), max(xs), n)
yi = np.linspace(min(ys), max(ys), n)
zi = scipy.interpolate.griddata((xs, ys), temps, (xi[None,:], yi[:,None]), method='cubic')


clev = np.arange(0,zi.max(),0.1)
fig = plt.figure()
plt.title("Distribuição de Temperatura em Placa Plana")
plt.contourf(xi, yi, zi, clev, cmap='jet', antialiased=False)
plt.colorbar(fraction=0.15)
plt.xlabel("X")
plt.ylabel("Y")
plt.show()