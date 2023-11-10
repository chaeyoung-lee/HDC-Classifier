"""
Convert .npy file into binary file readable by C
"""
import numpy as np

def npy2binary(model, codebook):
    # Headers
    header = {'10x10000' : [10,  0,  0,  0, 16, 39,  0,  0],
            '56x10000': [56,  0,  0,  0, 16, 39,  0,  0],
            }

    codebook = codebook.flatten()
    codebook = np.append(header['56x10000'], codebook).astype(np.uint8)
    codebook.tofile('model/codebook_56_10000.data')

    model = model.flatten()
    model = np.append(header['10x10000'], model).astype(np.uint8)
    model.tofile('model/model_10_10000.data')

def npy2header(model, codebook):
    res = "uint8_t model[10][10000] = {"
    for x in model:
        res += "{"
        for y in x:
            res += str(y)
            res += ","
        res = res[:-1] # remove the last comma
        res += "},"
    res = res[:-1]
    res += "};\n"

    res += "uint8_t codebook[56][10000] = {"
    for x in codebook:
        res += "{"
        for y in x:
            res += str(y)
            res += ","
        res = res[:-1] # remove the last comma
        res += "},"
    res = res[:-1]
    res += "};"

    with open('model/model.h', 'w') as f:
        f.write(res)

if __name__ == "__main__":
    codebook = np.load('model/codebook_56_10000.npy')
    model = np.load('model/model_10_10000.npy')

    npy2header(model, codebook)
    