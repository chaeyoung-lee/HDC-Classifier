from torchvision.datasets import MNIST
from torch.utils.data import Subset
import torch.utils
import numpy as np
import tqdm
import itertools 
import PIL

IMAGE_SIZE = 28 # MNIST image size
N_CLASS = 10    # MNIST class label
N_DIM = 10000    # HV dimension

def initialize(N=1000):
    alldata = MNIST(root='data', train=True, download=True)
    dataset = list(map(lambda datum: (datum[0].convert("1"), datum[1]),  \
                Subset(alldata, range(N))))
    train_data, test_data = torch.utils.data.random_split(dataset, [0.6,0.4])
    print("================ MNIST Data Loaded ===============")
    return train_data, test_data

def bind(x1, x2):
    return np.bitwise_xor(x1, x2)

def bundle(xs):
    return 1 * (np.sum(xs, axis=0) >= (len(xs) / 2))

def distance(x1, x2):
    return np.divide(np.sum(np.bitwise_xor(x1, x2)), N_DIM)

def encode(image, position_table):
    img_hv = []
    for i, j in itertools.product(range(IMAGE_SIZE), range(IMAGE_SIZE)):
        v = image.getpixel((i, j))
        hv = bind(position_table[i], position_table[IMAGE_SIZE + j]) # position encoding
        if v > 0: # white pixel
            hv = np.roll(hv, 1) # value encoding
        img_hv.append(hv)
    return bundle(img_hv)

def decode(image_hv, position_table):
    image = PIL.Image.new(mode="1", size=(IMAGE_SIZE, IMAGE_SIZE))
    for i, j in list(itertools.product(range(IMAGE_SIZE), range(IMAGE_SIZE))):
        hv = bind(position_table[i], position_table[IMAGE_SIZE + j])
        hv_perm = np.roll(hv, 1)
        v = 0 if distance(hv, image_hv) < distance(hv_perm, image_hv) else 255
        image.putpixel((i, j), v)
    return image

def train(item_memory, position_table, train_data):
    item_memory_ = item_memory.copy()
    datasets = {}

    for image, label in tqdm.tqdm(list(train_data)):
        hv_image = encode(image, position_table)
        if label not in datasets.keys():
            datasets[label] = []
        datasets[label].append(hv_image)
        
    for label in datasets.keys():
        label_hv = bundle(datasets[label])
        item_memory_[label] = label_hv
    
    return item_memory_

def predict(item_memory, position_table, image):
    result = []
    hv_image = encode(image, position_table)
    for i in range(len(item_memory)): # i = class label
        result.append(distance(item_memory[i], hv_image))
    label = np.argmin(result)
    return label, result[label]

def test(item_memory, position_table, test_data):
    correct, count = 0, 0
    for image, category in (pbar := tqdm.tqdm(test_data)):
        cat, dist = predict(item_memory, position_table, image)
        if cat == category:
            correct += 1
        count += 1
        pbar.set_description("accuracy=%f" % (float(correct)/count))
    print("ACCURACY: %f" % (float(correct)/count))


def main(mode):
    train_data, test_data = initialize()
    
    if mode == 'train':
        print("================ Training Begins ================")
        position_table = np.random.randint(2, size=(IMAGE_SIZE * 2, N_DIM))
        test_encoding(train_data[0][0], position_table)
        item_memory = np.random.randint(2, size=(N_CLASS, N_DIM))
        item_memory = train(item_memory, position_table, train_data)
        np.save('model_{}_{}'.format(N_CLASS, N_DIM), item_memory) # save model
        np.save('codebook_{}_{}'.format(N_CLASS, N_DIM), position_table) # save codebook
        print("Training successful. Saved model at model_{}_{}.npy".format(N_CLASS, N_DIM))

        print("================ Testing Begins ================")
        test(item_memory, position_table, test_data)

    elif mode == 'test':
        item_memory = np.load('../embedded-hdc/model/model_{}_{}.npy'.format(N_CLASS, N_DIM))
        position_table = np.load('../embedded-hdc/model/codebook_{}_{}.npy'.format(IMAGE_SIZE * 2, N_DIM))
        test(item_memory, position_table, test_data)

    return 0

def test_encoding(image, position_table):
    hv_image = encode(image, position_table)
    result = decode(hv_image, position_table)
    image.save("sample0.png")
    result.save("sample0_rec.png")

if __name__ == '__main__':
    mode = 'test'
    main(mode)