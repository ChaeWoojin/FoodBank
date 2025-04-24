__all__ = ["getUserInfo", "getFcltyGrpInfo", "getCntrbtrInfo", "getRceptStat", "getProvdStat", "getCnttgInfo", "getSpctrInfo", "getPreferInfo"]

import requests
import xml.etree.ElementTree as ET
import pandas as pd

encode = "j6wUNyCq%2F4vEC5xyrSKR99EsHqzxY3LvbI%2BkQUn%2BDgwsT0EfL%2FfkpPnWEN3d%2B%2B3T2mbvOPPZUmnhYg3QxC5jFw%3D%3D"
decode = "j6wUNyCq/4vEC5xyrSKR99EsHqzxY3LvbI+kQUn+DgwsT0EfL/fkpPnWEN3d++3T2mbvOPPZUmnhYg3QxC5jFw=="

BASE_URL = "http://apis.data.go.kr/B460014/foodBankInfoService2"
SERVICE_KEY = decode

# 1. 이용자 통계데이터 조회
def getUserInfo(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', area_cd='02', unity_signgu_cd='', spctr_cd='', user_seccd='', user_clscd='', happy_trgter_yn=''):
    url = f"{BASE_URL}/getUserInfo"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrCd": spctr_cd,
        "userSeccd": user_seccd,
        "userClscd": user_clscd,
        "happyTrgterYn": happy_trgter_yn
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrCd": i.findtext("spctrCd"),
        "userSeccd": i.findtext("userSeccd"),
        "userClscd": i.findtext("userClscd"),
        "happyTrgterYn": i.findtext("happyTrgterYn"),
        "useAmt": float(i.findtext("useAmt", 0)),
        "useCo": int(i.findtext("useCo", 0)),
        "userCo": int(i.findtext("userCo", 0))
    } for i in root.findall(".//item")])

# 2. 이용시설단체 통계데이터 조회
def getFcltyGrpInfo(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', area_cd='', unity_signgu_cd='', spctr_cd='', fclty_se_nm='', fclty_grp_clscd=''):
    url = f"{BASE_URL}/getFcltyGrpInfo"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrCd": spctr_cd,
        "fcltySeNm": fclty_se_nm,
        "fcltyGrpClscd": fclty_grp_clscd
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrCd": i.findtext("spctrCd"),
        "fcltySeNm": i.findtext("fcltySeNm"),
        "fcltyGrpClscd": i.findtext("fcltyGrpClscd"),
        "useAmt": float(i.findtext("useAmt", 0)),
        "useCo": int(i.findtext("useCo", 0)),
        "fcltyGrpCo": int(i.findtext("fcltyGrpCo", 0))
    } for i in root.findall(".//item")])

# 3. 기부자 정보 조회
def getCntrbtrInfo(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', area_cd='', unity_signgu_cd='', spctr_cd='', cntrbtr_seccd='', cntr_bplc_kndcd='', cntrbtr_nm=''):
    url = f"{BASE_URL}/getCntrbtrInfo"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrCd": spctr_cd,
        "cntrbtrSeccd": cntrbtr_seccd,
        "cntrBplcKndcd": cntr_bplc_kndcd,
        "cntrbtrNm": cntrbtr_nm
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrCd": i.findtext("spctrCd"),
        "cntrbtrSeccd": i.findtext("cntrbtrSeccd"),
        "cntrBplcKndcd": i.findtext("cntrBplcKndcd"),
        "cntrbtrNm": i.findtext("cntrbtrNm"),
        "cntrAmt": float(i.findtext("cntrAmt", 0)),
        "cntrCo": int(i.findtext("cntrCo", 0)),
        "cntrbtrCo": int(i.findtext("cntrbtrCo", 0))
    } for i in root.findall(".//item")])

# 4. 접수현황 통계데이터 조회
def getRceptStat(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', area_cd='', unity_signgu_cd='', spctr_cd=''):
    url = f"{BASE_URL}/getRceptStat"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrCd": spctr_cd
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrCd": i.findtext("spctrCd"),
        "rceptAmt": float(i.findtext("rceptAmt", 0)),
        "rceptCo": int(i.findtext("rceptCo", 0))
    } for i in root.findall(".//item")])

# 5. 제공현황 통계데이터 조회
def getProvdStat(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', area_cd='', unity_signgu_cd='', spctr_cd='', food_yn='Y', cnttg_lclas_cd='', cnttg_mlsfc_cd=''):
    url = f"{BASE_URL}/getProvdStat"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrCd": spctr_cd,
        "foodYn": food_yn,
        "cnttgLclasCd": cnttg_lclas_cd,
        "cnttgMlsfcCd": cnttg_mlsfc_cd
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrCd": i.findtext("spctrCd"),
        "foodYn": i.findtext("foodYn"),
        "cnttgLclasCd": i.findtext("cnttgLclasCd"),
        "cnttgMlsfcCd": i.findtext("cnttgMlsfcCd"),
        "userCo": int(i.findtext("userCo", 0)),
        "provdCo": int(i.findtext("provdCo", 0)),
        "provdAmt": float(i.findtext("provdAmt", 0))
    } for i in root.findall(".//item")])

# 6. 기부물품 현황 조회
def getCnttgInfo(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', distb_tmlmt_use_yn='N', injry_goods_intrcp_yn='Y', food_yn='Y', cnttg_lclas_cd='', cnttg_mlsfc_cd=''):
    url = f"{BASE_URL}/getCnttgInfo"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "distbTmlmtUseYn": distb_tmlmt_use_yn,
        "injryGoodsIntrcpYn": injry_goods_intrcp_yn,
        "foodYn": food_yn,
        "cnttgLclasCd": cnttg_lclas_cd,
        "cnttgMlsfcCd": cnttg_mlsfc_cd
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "distbTmlmtUseYn": i.findtext("distbTmlmtUseYn"),
        "injryGoodsIntrcpYn": i.findtext("injryGoodsIntrcpYn"),
        "foodYn": i.findtext("foodYn"),
        "cnttgLclasCd": i.findtext("cnttgLclasCd"),
        "cnttgMlsfcCd": i.findtext("cnttgMlsfcCd"),
        "cnttgQy": int(i.findtext("cnttgQy", 0)),
        "acntbkAmt": float(i.findtext("acntbkAmt", 0))
    } for i in root.findall(".//item")])

# 7. 지원센터 정보 조회
def getSpctrInfo(page_no=1, num_of_rows=10, data_type='xml', stdr_ym='202402', area_cd='', unity_signgu_cd='', spctr_uncd='', spctr_secd='', spctr_cd='', spctr_stscd='', oper_mby_lclas_cd='', oper_mby_sclas_cd='', sttemnt_seccd='', regist_de=''):
    url = f"{BASE_URL}/getSpctrInfo"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "stdrYm": stdr_ym,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrUncd": spctr_uncd,
        "spctrSecd": spctr_secd,
        "spctrCd": spctr_cd,
        "spctrStscd": spctr_stscd,
        "operMbyLclasCd": oper_mby_lclas_cd,
        "operMbySclasCd": oper_mby_sclas_cd,
        "sttemntSeccd": sttemnt_seccd,
        "registDe": regist_de
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "stdrYm": i.findtext("stdrYm"),
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrUncd": i.findtext("spctrUncd"),
        "spctrSecd": i.findtext("spctrSecd"),
        "spctrCd": i.findtext("spctrCd"),
        "spctrTelno": i.findtext("spctrTelno"),
        "spctrAdres": i.findtext("spctrAdres"),
        "spctrDetailAdres": i.findtext("spctrDetailAdres"),
        "spctrStscd": i.findtext("spctrStscd"),
        "operMbyLclasCd": i.findtext("operMbyLclasCd"),
        "operMbySclasCd": i.findtext("operMbySclasCd"),
        "sttemntSeccd": i.findtext("sttemntSeccd"),
        "registDe": i.findtext("registDe"),
        "rceptAmt": float(i.findtext("rceptAmt", 0)),
        "provdAmt": float(i.findtext("provdAmt", 0)),
        "undtakeAmt": float(i.findtext("undtakeAmt", 0)),
        "trnsferAmt": float(i.findtext("trnsferAmt", 0)),
        "userCo": int(i.findtext("userCo", 0))
    } for i in root.findall(".//item")])

# 8. 선호물품 현황 조회
def getPreferInfo(page_no=1, num_of_rows=10, data_type='xml', area_cd='', unity_signgu_cd='', spctr_cd='', prefer_cnttg_clscd=''):
    url = f"{BASE_URL}/getPreferInfo"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": data_type,
        "areaCd": area_cd,
        "unitySignguCd": unity_signgu_cd,
        "spctrCd": spctr_cd,
        "preferCnttgClscd": prefer_cnttg_clscd
    }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    return pd.DataFrame([{
        "areaCd": i.findtext("areaCd"),
        "unitySignguCd": i.findtext("unitySignguCd"),
        "spctrCd": i.findtext("spctrCd"),
        "preferCnttgClscd": i.findtext("preferCnttgClscd"),
        "holdQy": int(i.findtext("holdQy", 0))
    } for i in root.findall(".//item")])