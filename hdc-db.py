from hdc import *
import csv


class HDDatabase:

    def __init__(self):
        self.db = HDItemMem("db")
        self.codebook = HDCodebook("string")
        # raise Exception("other instantiations here")
        
    def encode_string(self,value):
        if self.codebook.has(value):
            return self.codebook.get(value)
        else:
            return self.codebook.add(value)
        # raise Exception("translate a string to a hypervector") 
        
    def decode_string(self,hypervec):
        return self.codebook.wta(hypervec)[0]
        # raise Exception("translate a hypervector to a string") 

    def encode_row(self, fields):
        res = []
        for k, v in fields.items():
            bundled_hv = HDC.bundle([self.encode_string(k), self.encode_string(v)])
            res.append(bundled_hv)
        return HDC.bind_all(res)
        # raise Exception("translate a dictionary of field-value pairs to a hypervector") 
        
    def decode_row(self, hypervec):
        res = {}
        keys = ['Number', 'Digimon', 'Stage', 'Type', 'Attribute', 'Memory', 'Equip Slots', 'Lv 50 HP', 'Lv50 SP', 'Lv50 Atk', 'Lv50 Def', 'Lv50 Int', 'Lv50 Spd']
        for key in keys:
            key_hv = self.encode_string(key)
            inverted_hv = HDC.bundle([key_hv, hypervec])
            value = self.codebook.wta(inverted_hv)[0]
            res[key] = value
        return res
        # raise Exception("reconstruct a dictionary of field-value pairs from a hypervector.") 

    def add_row(self, primary_key, fields):
        row_hv = self.encode_row(fields)
        self.db.add(primary_key, row_hv)

    def get_row(self,key):
        hv = self.db.get(key)
        return self.decode_row(hv)
        # raise Exception("retrieve a dictonary of field-value pairs from a hypervector row")

    def get_value(self,key, field, ret_dist=False):
        hv = self.db.get(key)
        field_hv = self.encode_string(field)
        return self.codebook.wta(HDC.bundle([field_hv, hv]))[0]
        # raise Exception("given a primary key and a field, get the value assigned to the field")
        
    def get_matches(self, field_value_dict, threshold=0.4):
        query = self.encode_row(field_value_dict)
        return self.db.matches(query, threshold=threshold)
        # raise Exception("get database entries that contain provided dictionary of field-value pairs")
        
    def get_analogy(self, target_key, other_key, target_value):
        field = self.get_value(target_key, target_value)
        return self.codebook.wta(HDC.bundle([self.db.get(other_key), self.encode_string(field)]))
        # raise Exception("analogy query")


def load_json():
    data = {}
    with open("digimon.csv","r") as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            key = rows['Digimon']
            data[key] = rows
    return data

def build_database(data):
    HDC.SIZE = 10000
    db = HDDatabase()

    for key, fields in data.items():
        db.add_row(key,fields)

    return db

def summarize_result(data,result, summary_fn):
    print("---- # matches = %d ----" % len(list(result.keys())))
    for digi, distance in result.items():
        print("%f] %s: %s" % (distance, digi, summary_fn(data[digi])))


def digimon_basic_queries(data,db):
    
    print("===== virus-plant query =====")
    thr = 0.40
    digis = db.get_matches({"Type":"Virus", "Attribute":"Plant"}, threshold=thr)
    summarize_result(data,digis, lambda row: "true match" if row["Type"] == "Virus" and row["Attribute"] == "Plant" else "false positive")

    print("===== champion query =====")
    thr = 0.40
    digis = db.get_matches({"Stage":"Champion"}, threshold=thr)
    summarize_result(data,digis, lambda row: "true match" if row["Stage"] == "Champion" else "false positive")


def digimon_test_encoding(data,db):
    strn = "tester"
    hv_test = db.encode_string(strn)
    rec_strn = db.decode_string(hv_test)
    print("original=%s" % strn)
    print("recovered=%s" % rec_strn)
    print("---")

    row = data["Wormmon"]
    hvect = db.encode_row(row)
    rec_row = db.decode_row(hvect)
    print("original=%s" % str(row))
    print("recovered=%s" % str(rec_row))
    print("---")


def digimon_value_queries(data,db):
    value = db.get_value("Lotosmon", "Stage")
    print("Lotosmon.Stage = %s" % value)
    
    targ_row = db.get_row("Lotosmon")
    print("Lotosmon" + str(targ_row))


def analogy_query(data, db):
    # Lotosmon is to Data as Crusadermon is to <what field>

    targ_row = db.get_row("Lotosmon")
    other_row = db.get_row("Crusadermon")
    print("Lotosmon has a a field with a Data value, what is the equivalent value in Crusadermon's entry")
    value, dist = db.get_analogy(target_key="Lotosmon", other_key="Crusadermon", target_value="Data")
    print("Lotosmon" + str(targ_row))
    print("Crusadermon" + str(other_row))
    print("------")
    print("value: %s (dist=%f)" % (value,dist))
    print("expected result: Virus, the type of Crusadermon")
    print("")


def __main__():
    data = load_json()
    db = build_database(data)
    digimon_basic_queries(data,db)
    digimon_value_queries(data,db)
    digimon_test_encoding(data, db)
    analogy_query(data,db)

if __name__ == '__main__':
    __main__()