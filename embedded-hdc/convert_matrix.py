"""
Convert .npy file into binary file readable by C
"""
import numpy as np

# Headers
header = {'10x10000' : [10,  0,  0,  0, 16, 39,  0,  0],
          '56x10000': [56,  0,  0,  0, 16, 39,  0,  0],
          }

position_table = np.load('model/codebook_56_10000.npy').flatten()
position_table = np.append(header['56x10000'], position_table).astype(np.uint8)
position_table.tofile('model/codebook_56_10000.data')

item_memory = np.load('model/model_10_10000.npy').flatten()
item_memory = np.append(header['10x10000'], item_memory).astype(np.uint8)
item_memory.tofile('model/model_10_10000.data')