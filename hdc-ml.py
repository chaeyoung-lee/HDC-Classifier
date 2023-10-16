from torchvision.datasets import MNIST 
from torch.utils.data import Subset
import tqdm
import torch.utils
from hdc import *
import itertools 
import PIL
import math

MAX = 26

class MNISTClassifier:

    def __init__(self):
        self.classifier = HDItemMem()
        self.codebook = HDCodebook("pixels")
        for i in range(MAX):
            self.codebook.add('x' + str(i))
            self.codebook.add('y' + str(i))
        # self.codebook.add('B')
        # self.codebook.add('W')
        # raise Exception("initialize other stuff here")

    def encode_coord(self,i,j):
        hv_x = self.codebook.get('x' + str(i))
        hv_y = self.codebook.get('y' + str(j))
        return HDC.bind(hv_x, hv_y)
        # raise Exception("encode a coordinate in the image as a hypervector")

    def encode_pixel(self, i, j, v):
        hv = self.encode_coord(i, j)
        if v > 0: # white
            hv = HDC.permute(hv, 1)
        return hv
        # key_v = 'B' if v == 0 else 'W'
        # hv_v = HDC.permute(self.codebook.get(key_v), 2)
        # return HDC.bind(self.encode_coord(i, j), hv_v)
        # raise Exception("encode a pixel in the image as a hypervector")

    def encode_image(self,image):
        hv = []
        for i,j in itertools.product(range(MAX),range(MAX)):
            v = image.getpixel((i,j))
            hv.append(self.encode_pixel(i,j,v))
        return HDC.bundle(hv)
        # raise Exception("return hypervector encoding of image")

    def decode_pixel(self, image_hypervec, i, j):
        hv = self.encode_coord(i, j)
        hv_permuted = HDC.permute(hv, 1)
        if HDC.dist(hv, image_hypervec) < HDC.dist(hv_permuted, image_hypervec):
            return 0
        else:
            return 255
        # hv = HDC.bind(image_hypervec, self.encode_coord(i, j))
        # hv = HDC.permute(hv, -2)
        # return self.codebook.wta(hv)[0]
        # raise Exception("retrieve the value of the pixel at coordinate i,j in the image hypervector")

    def decode_image(self, image_hypervec):
        im = PIL.Image.new(mode="1", size=(MAX, MAX))
        for i,j in list(itertools.product(range(MAX),range(MAX))):
            v = self.decode_pixel(image_hypervec,i,j)
            # v = 0 if v == 'B' else 255
            im.putpixel((i,j),v)
        return im


    def train(self,train_data):
        for image,label in tqdm.tqdm(list(train_data)):
            hv_image = self.encode_image(image)
            if not self.classifier.has(label):
                self.classifier.item_mem[label] = hv_image
            else:
                self.classifier.item_mem[label] = HDC.bundle(self.classifier.get(label), hv_image)
            # raise Exception("do something with the image,label pair from the dataset") 

    def classify(self,image):
        raise Exception("classify an image using your classifier and return the label and distance")
        return label,dist

    def build_gen_model(self,train_data):
        self.gen_model = {}
        for image,label in tqdm.tqdm(list(train_data)):
            raise Exception("build generative model") 
            

    def generate(self, cat, trials=10):
        gen_hv = self.gen_model[cat]
        raise Exception("generate random image with label <cat> using generative model. Average over <trials> trials.")

def initialize(N=1000):
    alldata = MNIST(root='data', train=True, download=True)
    dataset = list(map(lambda datum: (datum[0].convert("1"), datum[1]),  \
                Subset(alldata, range(N))))

    train_data, test_data = torch.utils.data.random_split(dataset, [0.6,0.4])
    HDC.SIZE = 10000
    classifier = MNISTClassifier()
    return train_data, test_data, classifier

def test_encoding():
    train_data, test_data, classifier = initialize()
    image0,_ = train_data[0]
    hv_image0 = classifier.encode_image(image0)
    result = classifier.decode_image(hv_image0)
    image0.save("sample0.png")
    result.save("sample0_rec.png")


def test_classifier():
    train_data, test_data, classifier = initialize(2000)

    print("======= training classifier =====")
    classifier.train(train_data)

    print("======= testing classifier =====")
    correct, count = 0, 0
    for image, category in (pbar := tqdm.tqdm(test_data)):
        cat, dist = classifier.classify(image)
        if cat == category:
            correct += 1
        count += 1
        
        pbar.set_description("accuracy=%f" % (float(correct)/count))
    
    print("ACCURACY: %f" % (float(correct)/count))

def test_generative_model():
    train_data, test_data, classifier = initialize(1000)
    print("======= building generative model =====")
    classifier.build_gen_model(train_data)

    print("======= generate images =====")
    while True:
        cat = random.randint(0,9)
        img = classifier.generate(cat)
        print("generated image for class %d" % cat)
        img.save("generated.png")
        input("press any key to generate new image..")


if __name__ == '__main__':
    test_encoding()
    # test_classifier()
    # test_generative_model()