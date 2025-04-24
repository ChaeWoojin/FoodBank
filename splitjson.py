import pandas as pd
import json
from collections import defaultdict

# Load the data
with open("./기술문서_전체코드정보.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract list under "센터코드 정보"
entries = data.get("센터코드 정보", [])

# Dictionary to store code-name mappings
code_name_dicts = defaultdict(dict)

# Mapping known code-name pairs (manually identified patterns)
code_name_keys = {
    "지역코드": "지역코드명",
    "통합시군구코드": "통합시군구명",
    "센터코드": "센터코드명",
    "이용자구분코드": "이용자구분코드 명",
    "이용자분류코드": "이용자분류코드명",
    "시설유형명": None,
    "시설단체분류코드": "시설단체분류코드 명",
    "기부자구분코드": "기부자구분코드 명",
    "기부사업장종류코드": "기부사업장종류코드 명",
    "기부물품대분류코드": "기부물품대분류코드 명",
    "기부물품중분류코드": "기부물품중분류코드명",
    "지원센터단위코드": "지원센터단위코드 명",
    "지원센터구분코드": "지원센터구분코드 명",
    "지원센터상태코드": "지원센터상태코드 명",
    "운영주체대분류코드": "운영주체대분류코드 명",
    "운영주체소분류코드": "운영주체소분류코드 명",
    "신고구분코드": "신고구분코드 명",
}

# Process each entry and extract code-name pairs
for entry in entries:
    for code_key, name_key in code_name_keys.items():
        if code_key in entry:
            if name_key:
                code_name_dicts[code_key][entry[code_key]] = entry[name_key]
            else:
                code_name_dicts[code_key][entry[code_key]] = entry[code_key]


for key in ['지역코드', '통합시군구코드', '센터코드', '이용자구분코드', '이용자분류코드', '시설유형명', '시설단체분류코드', '기부자구분코드', '기부사업장종류코드', '기부물품대분류코드', '기부물품중분류코드', '지원센터단위코드', '지원센터구 분코드', '지원센터상태코드', '운영주체대분류코드', '운영주체소분류코드', '신고구분코드']:
    print(code_name_dicts[key])
