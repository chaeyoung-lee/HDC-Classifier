import string
import random
import operator
import numpy as np
import tqdm
import matplotlib.pyplot as plt

class HDC:
    SIZE = 10000

    @classmethod
    def rand_vec(cls):
        return np.random.randint(2, size=HDC.SIZE)
        # raise Exception("generate atomic hypervector with size HDC.SIZE") 
    
    @classmethod
    def dist(cls,x1,x2):
        # 1/N sum XOR(x1,x2)
        return np.divide(np.sum(np.bitwise_xor(x1, x2)), HDC.SIZE)
        # raise Exception("hamming distance between hypervectors") 
    
    @classmethod
    def bind(cls,x1,x2):
        # XOR(x1, x2)
        return np.bitwise_xor(x1, x2)
        # raise Exception("bind two hypervectors together") 

    @classmethod
    def bind_all(cls, xs):
        return np.bitwise_xor.reduce(xs)
        # raise Exception("convenience function. bind together a list of hypervectors") 

    @classmethod
    def bundle(cls,xs):
        # (x1+x2) > (K/2)
        return 1 * (np.sum(xs, axis=0) >= (len(xs) / 2))
        # raise Exception("bundle together xs, a list of hypervectors") 
          

    @classmethod
    def permute(cls,x,i):
        return np.roll(x, i)
        # raise Exception("permute x by i, where i can be positive or negative") 
    
    
    @classmethod
    def apply_bit_flips(cls,x,p=0.0):
        loc = np.random.randint(100, size=HDC.SIZE) < p * 100
        return np.bitwise_xor(x, loc)
        # raise Exception("return a corrupted hypervector, given a per-bit bit flip probability p") 
    


class HDItemMem:

    def __init__(self,name=None) -> None:
        self.name = name
        self.item_mem = {}
        # per-bit bit flip probabilities for the  hamming distance
        self.prob_bit_flips = 0.0

    def add(self,key,hv):
        assert(not hv is None)
        self.item_mem[key] = hv
    
    def get(self,key):
        return self.item_mem[key]

    def has(self,key):
        return key in self.item_mem

    def distance(self,query):
        res = {}
        for k, v in self.item_mem.items():
            if self.prob_bit_flips > 0:
                v = HDC.apply_bit_flips(v, self.prob_bit_flips)
            res[k] = HDC.dist(query, v)
        return res
        # raise Exception("compute hamming distance between query vector and each row in item memory. Introduce bit flips if the bit flip probability is nonzero") 

    def all_keys(self):
        return list(self.item_mem.keys())

    def all_hvs(self):
        return list(self.item_mem.values())

    def wta(self,query):
        dist = self.distance(query)
        key = min(dist, key=dist.get)
        return key, dist[key]
        # raise Exception("winner-take-all querying") 
        
    def matches(self,query, threshold=0.49):
        dist = self.distance(query)
        return {k: v for k,v in dist.items() if v < threshold}
        # raise Exception("threshold-based querying") 
        

# a codebook is simply an item memory that always creates a random hypervector
# when a key is added.
class HDCodebook(HDItemMem):

    def __init__(self,name=None):
        HDItemMem.__init__(self,name)

    def add(self,key):
        self.item_mem[key] = HDC.rand_vec()
        return self.item_mem[key]
    

def make_letter_hvs():
    letter_hvs = HDCodebook(name="letter")
    for letter in string.ascii_lowercase:
        letter_hvs.add(letter)
    return letter_hvs
    # raise Exception("return a codebook of letter hypervectors") 
    
def make_word(letter_codebook, word):
    res = []
    for i, letter in enumerate(word):
        vec = HDC.permute(letter_codebook.get(letter), i)
        res.append(vec)
    return HDC.bind_all(res)
    # raise Exception("make a word using the letter codebook") 
    
def monte_carlo(fxn,trials):
    results = list(map(lambda i: fxn(), tqdm.tqdm(range(trials))))
    return results

def plot_dist_distributions(key1, dist1, key2, dist2):
    plt.hist(dist1,  
            alpha=0.75, 
            label=key1) 
    
    plt.hist(dist2, 
            alpha=0.75, 
            label=key2) 
    
    plt.legend(loc='upper right') 
    plt.title('Distance distribution for Two Words') 
    plt.show()
    plt.clf()

def study_distributions():
    def gen_codebook_and_words(w1,w2,prob_error=0.0):
        letter_cb = make_letter_hvs()
        hv1 = make_word(letter_cb, w1)
        hv2 = make_word(letter_cb, w2)
        if prob_error > 0:
            hv1 = HDC.apply_bit_flips(hv1, prob_error)
            hv2 = HDC.apply_bit_flips(hv2, prob_error)
        return HDC.dist(hv1, hv2)
        # raise Exception("encode words and compute distance") 


    trials = 1000
    d1 = monte_carlo(lambda: gen_codebook_and_words("fox","box"), trials)
    d2 = monte_carlo(lambda: gen_codebook_and_words("fox","car"), trials)
    plot_dist_distributions("box",d1,"car",d2)

    perr = 0.10
    d1 = monte_carlo(lambda: gen_codebook_and_words("fox","box", prob_error=perr), trials)
    d2 = monte_carlo(lambda: gen_codebook_and_words("fox","car", prob_error=perr), trials)
    plot_dist_distributions("box",d1,"car",d2)


if __name__ == '__main__':
    HDC.SIZE = 10000

    letter_cb = make_letter_hvs()
    hv1 = make_word(letter_cb,"fox")
    hv2 = make_word(letter_cb,"box")
    hv3 = make_word(letter_cb,"xfo")
    hv4 = make_word(letter_cb,"care")

    print(HDC.dist(hv1, hv2))
    print(HDC.dist(hv1, hv3))
    print(HDC.dist(hv1, hv4))

    study_distributions()




