
import json
import numpy as np
import math

def readJSON(filename):
    with open(filename, 'r') as fid:
        data = json.load(fid)
        if 'coords' in data:
            nE = data['nE']
            h = float(data['h'])
            k = float(data['constMola'])
            mass = float(data['mass'])
            numPassos = int(data['numPassos'])
            
            conect = np.zeros((nE, 5), dtype=int)
            f = np.zeros((nE, 2))
            restr = np.zeros((nE, 2), dtype=int)
            x0 = np.zeros((nE, 1))
            y0 = np.zeros((nE, 1))

            for i in range(nE):
                x0[i] = float(data['coords'][i][0])
                y0[i] = float(data['coords'][i][1])
                conect[i, :] = [int(x) for x in data['conect'][i]]
                f[i, 0] = float(data['force'][i][0])
                f[i, 1] = float(data['force'][i][1])
                restr[i, :] = [int(x) for x in data['restr'][i]]

            radius = float(data['radius']) if 'radius' in data else 0
            return nE, x0, y0, radius, h, k, mass, f, conect, restr, numPassos

def main(filename):
    nE, x0, y0, radius, h, k, m, f, conect, restr, N = readJSON(filename)
    
    nDOFs = 2 * nE

    a = np.zeros((nDOFs, 1))
    v = np.zeros((nDOFs, 1))
    u = np.zeros((nDOFs, 1))
    fi = np.zeros((nDOFs, 1))
    u_t = np.zeros((N, 1))
    result_index = nE * 2 - 1

    a = (f - fi) / m
    for ii in range(N):
        v += a * (0.5 * h)
        u += v * h

        fi.fill(0)
        for jj in range(nE):
            u[jj * 2 - 1] *= (1 - restr[jj * 2 - 1])
            u[jj * 2] *= (1 - restr[jj * 2])
            xj = x0[jj] + u[jj * 2 - 1]
            yj = y0[jj] + u[jj * 2]

            for ww in range(conect[jj, 0]):
                neighbour = conect[jj, ww + 1]
                xw = x0[neighbour] + u[neighbour * 2 - 1]
                yw = y0[neighbour] + u[neighbour * 2]
                dx = xj - xw
                dy = yj - yw
                d = math.sqrt(dx*dx + dy*dy)
                spring_deform = d - 2 * radius
                dx = spring_deform * dx / d
                dy = spring_deform * dy / d
                fi[jj * 2 - 1] += k * dx
                fi[jj * 2] += k * dy

        u_t[ii] = u[result_index]
        a = (f - fi) / m
        v += a * h

    outputRes(u_t[:, 0])

def outputRes(_res):
    result_dict = {"resultado": _res.tolist()}
    with open("output.json", "w") as f:
        json.dump(result_dict, f)

main("input_70.json")