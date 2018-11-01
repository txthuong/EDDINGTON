import re
from expects import *

'''
all_regex = [r"+CME ERROR: (\d+)", r"(ERROR)"]
#regex = r"\+SRBLESCANPARAMS: %s" %[09]
string = '+CME ERROR: 916'
#string = '+SRBLESCANPARAMS:'
#regex = r"\+SRBTADDR: \"([\w|:]{17})\""
#string1 = '+SRBTADDR: "112:2:33:44:55:6:"'
#string2 = '+SRBTADDR: "11:22:33:44:55:663"'
print(regex)

match = re.search(regex, string, re.DOTALL)

if match:
    print(match[1])
else:
    print ('zzzzzzzzzzzzz')

if re.search(regex, string, re.DOTALL):
    print ('2')
else:
    print ('zzzzzzzzzzzzz')



adv_data = [0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74]
print(bytearray(adv_data))
print(''.join('\\' + '{:02X}'.format(x) for x in adv_data))

'''

all_regex = [r"\+CME ERROR: (\d+)", r"(ERROR)"]
string = '+CME ERROR: 916'
for regex in all_regex:
    match = re.search(regex, string, re.DOTALL)
    if match:
        print(match[0])



a, b = 1, 2
print(a)
print(b)