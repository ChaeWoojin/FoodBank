from utils import *

if __name__ == '__main__':
    # for df in [getUserInfo(), getFcltyGrpInfo(), getCntrbtrInfo(), getRceptStat(), getProvdStat(), getCnttgInfo(), getSpctrInfo(), getPreferInfo()]:
    #     print(df.head())
    
    df = getUserInfo()
    print(df.head())