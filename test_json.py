import json

s = '''{
  "key": "value with
  newline"
}'''

try:
    print(json.loads(s, strict=False))
except Exception as e:
    print("Error:", e)
