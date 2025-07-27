import json
print("输入从Cookie Editor复制来的Cookie们，两次换行结束输入：")
lines = []
while line := input():
    lines.append(line)
data = json.loads('\n'.join(lines))
cookies = {x["name"]: x["value"] for x in data}
with open("cookies.json", "w") as f:
    json.dump(cookies, f, indent=4)
print("cookies.json已生成，请检查")