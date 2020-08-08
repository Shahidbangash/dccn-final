import base64
import json

data = {}
encoded = base64.b64encode(b'data to be encoded')  # b'ZGF0YSB0byBiZSBlbmNvZGVk' (notice the "b")
data['bytes'] = encoded.decode('ascii')            # 'ZGF0YSB0byBiZSBlbmNvZGVk'
decoded = base64.b64decode(data['bytes'])

print("Printing decoding data")
print(decoded)

print(json.dumps(data))