import json
import numpy as np


def readJSON(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    if "n" in data:  # Importing number of points in the mesh
        n = data["n"]

    conect = np.empty((n, 4), dtype=np.int16)  # Importing connectivity matrix
    if "conect" in data:
        for i in range(n):
            conect[i, 0] = int(data["conect"][i][0])
            conect[i, 1] = int(data["conect"][i][1])
            conect[i, 2] = int(data["conect"][i][2])
            conect[i, 3] = int(data["conect"][i][3])

    coords = np.empty((n, 2), dtype=np.float64)
    if "coords" in data:
        for i in range(n):
            coords[i, 0] = float(data["coords"][i][0])
            coords[i, 1] = float(data["coords"][i][1])

    h = float(data["h"]) if "h" in data else None
    k = float(data["k"]) if "k" in data else None
    hpoints = float(data["hpoints"]) if "hpoints" in data else None
    vpoints = float(data["vpoints"]) if "vpoints" in data else None

    bc = np.empty((n, 2), dtype=np.float64)
    if "bc" in data:
        for i in range(n):
            bc[i, 0] = float(data["bc"][i][0])
            bc[i, 1] = float(data["bc"][i][1])

    return n, conect, coords, h, k, bc, hpoints, vpoints


def blocoF(h, k):
    a = 2 * ((h/k)**2 + 1)
    b = - (h/k)**2
    return [a, -1, -1, b, b]


def main(filename):
    n, conect, coords, h, k, bc, hpoints, vpoints = readJSON(filename)
    bloco = blocoF(h, k)

    # Initialize A, b, and x
    A = np.zeros((n, n), dtype=np.float64)
    b = np.zeros((n, 1), dtype=np.float64)
    x = np.zeros((n, 1), dtype=np.float64)

    # Fill A and b
    for i in range(n):
        A[i, i] = bloco[0]
        for j in range(4):  # Assuming 'conect' has 4 columns
            loc = conect[i, j]
            if loc > 0:
                if bc[loc - 1, 0] == 0:
                    A[i, loc - 1] = bloco[j + 1]
                else:
                    b[i, 0] += bc[loc - 1, 1]

    # Adjust A and b for boundary conditions
    for i in range(n):
        if bc[i, 0] == 1:
            A[i, :] = np.zeros(n)
            A[i, i] = 1.0
            b[i, 0] = bc[i, 1]

    # Solve the system of equations
    x = np.linalg.solve(A, b)

    # Prepare and save the results
    xs = coords[:, 0]
    ys = coords[:, 1]
    outputRes(x, vpoints, hpoints, xs, ys)


def outputRes(x, vpoints, hpoints, xs, ys):
    result = {
        "x": [x.flatten().tolist()],
        "vpoints": vpoints,
        "hpoints": hpoints,
        "xs": [xs.tolist()],
        "ys": [ys.tolist()]
    }
    with open("output.json", "w") as f:
        json.dump(result, f)


main("./input.json")
