

adv_data = [[0x02, 0x01, 0x06], [0x0A, 0x09, 0x45, 0x64, 0x64, 0x69, 0x6E, 0x67, 0x74, 0x6F, 0x6E],
            [0x04, 0x08, 0x45, 0x64, 0x64]]

for data in adv_data:
    if data[1] == 0x08:
        print("Flags")
    length_data = data[0]
    print(length_data)
    print(bytes(data[2:len(data)]))
    if data == "\02\01\06":
        print("00000000")

a = 3
b = 4

if a == 3 or b == 5:
    print("test")


adv_data_123 = [0x02, 0x01, 0x06, 0x0A, 0x09, 0x45, 0x64, 0x64, 0x69, 0x6E, 0x67, 0x74, 0x6F, 0x6E,
            0x04, 0x08, 0x45, 0x64, 0x64]

#class AdvertisingData:
#    def __init__(self, length, adv_type, data):
#        self.length = length
#        self.adv_type = adv_type
#        self.data = data

def split_adv_data(adv_data):
    list_adv_data = []
    i=0
    while len(adv_data) > 0:
        length = adv_data[i]
        adv_type = adv_data[i+1]
        data = adv_data[(i+2):(length+1)]
        adv = [length, adv_type] + data
        list_adv_data.append(adv)
        adv_data = adv_data[(length+2):len(adv_data)]
    return list_adv_data

list_list_adv_data_123 = split_adv_data(adv_data_123)
for ad in list_list_adv_data_123:
    print(ad)

