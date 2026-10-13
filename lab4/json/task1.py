import json

file_path = r'C:\Users\parsi\pp2\lab4\json\sample-data.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print(f"{'-' * 50} {'-' * 20} {'-' * 6} {'-' * 6}")

for item in data.get("imdata", []):
    attr = item.get("l1PhysIf", {}).get("attributes", {})
    
    dn = attr.get("dn", "")
    desc = attr.get("descr", "") 
    speed = attr.get("speed", "")
    mtu = str(attr.get("mtu", ""))
    
    print(f"{dn:<50} {desc:<20} {speed:<7} {mtu:<6}")