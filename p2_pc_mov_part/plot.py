import json
import matplotlib.pyplot as plt

def readJSON(_filename):
    data = json.load(open(_filename))
    return data

res1 = readJSON("output_70.json")
res2 = readJSON("output_280.json")
res3 = readJSON("output_1750.json")
print(len(res2["resultado"]))

plt.plot(res1["resultado"], label="n = 70")
plt.plot(res2["resultado"], label="n = 280")
plt.plot(res3["resultado"], label = "n = 1750")
plt.title("Deslocamento de uma partícula na extremidade livre da placa")
plt.legend()
plt.xlabel("iter")
plt.ylabel("Deslocamento (m)")
plt.show()