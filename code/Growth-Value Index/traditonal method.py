'''
Traditional growth-value index building method 
Taking the Wind Style Index as a benchmark, replicating and tracking the index by deconstructing the compilation method 
to provide a more accurate analysis of the investment portfolio for different investment requirements.
Traditional fund style classification system: 
The valuation method is used to create style indices. 
Funds are categorized into nine style indices based on their large, medium, or small cap size and growth, value, 
or balanced style. The investment scope and target weights of the funds change during operation, and adjustments 
to the style fund basket are made in May and September each year.
Valuation indicators for stocks include five common indicators: PE (Price-to-Earnings Ratio), 
PB (Price-to-Book Ratio), PS (Price-to-Sales Ratio), PCF (Price-to-Cash Flow Ratio), 
and PEG (Price-to-Earnings Growth Ratio). By averaging these indicators equally, the funds are divided into n groups. 
The net value performance of each group is calculated and categorized according to the attributes of growth, balanced, and value.
'''
import pandas as pd
import numpy as np
import time

def Covert_Code(str,stock):
    if str is None or str is np.nan:
        return np.nan
    else:
        aa = str.split(',')
        ret = []
        for i in range(len(aa)):
            if aa[i] in stock['证券代码']:
                ret.append(stock.loc[aa[i],'证券代码'])
        return ret


def Data_Reading(filename,re_date):
    pw_list = ['ratio1','ratio2','ratio3','ratio4','ratio5','ratio6','ratio7',
            'ratio8','ratio9','ratio10']
    position_weight = {}
    position_cumweight = {}
    for p in range(len(pw_list)):
        p_c = pd.read_excel(filename+pw_list[p]+'.xlsx',sheet_name='Sheet0',index_col='证券代码')
        p_c = p_c.iloc[:,1:].replace('——',0).sort_index().T.sort_index()
        p_c.index = re_date
        position_cumweight[p] = p_c
        if p>=1:
            p_w = p_c - position_cumweight[p-1]
        else:
            p_w = p_c
        position_weight[p] = p_w.fillna(0)

    END = time.time()
    print(f'{END-START}s')
    return p_w


def Index_PB(PB,fundrate,re_date):
    quantile = 5
    dates = fundrate.index
    indices = np.array([np.nan]*len(dates)*quantile).reshape(len(dates),quantile)
    for t in range(len(dates)):
        START = time.time()
        fundrate_t = fundrate.iloc[t,:]
        d = dates[t][-10:]
        if d <= '2019-09-30':
            rep = re_date[0]
        elif d <= '2019-12-31':
            rep = re_date[1]
        elif d <= '2020-03-31':
            rep = re_date[2]
        elif d <= '2020-06-30':
            rep = re_date[3]
        elif d <= '2020-09-30':
            rep = re_date[4]
        elif d <= '2020-12-31':
            rep = re_date[5]
        elif d <= '2021-03-31':
            rep = re_date[6]
        elif dates[t] <= '2021-06-30':
            rep = re_date[7]
        elif dates[t] <= '2021-09-30':
            rep = re_date[8]
        elif dates[t] <= '2021-12-31':
            rep = re_date[9]
        elif dates[t] <= '2022-03-31':
            rep = re_date[10]
        elif dates[t] <= '2022-06-30':
            rep = re_date[11]
        else:
            rep = re_date[12]
        PB_t = PB.loc[rep,:]
    return PB_t


    
def Cons_Index(series,PB_t,position_weight,rep):
    '''
    Calculate the valuation of each fund as the sum of the top ten holdings
    ' Price-to-Book (PB) values multiplied by their respective weights 
    in the fund divided by 100 (current basket).
    '''
    fund_pb = pd.Series([0]*len(series.index),index=series.index)
    for i in range(len(series.index)):
        lis = series.iloc[i]
        if lis is not None:
            for l in range(len(lis)):
                try:
                    fund_pb.iloc[i] += PB_t.loc[lis[l]] * position_weight[l].loc[rep,series.index[i]] 
                except:
                    pass
    return fund_pb



    
def Div_Style(x,fundPB):  # param:quantile
    '''The funds are categorized into three tiers: 
    Growth type/Value type, with 1 representing 
    Growth and 0 representing Value.'''
    if x == np.nan:
        return np.nan
    elif x > np.nanquantile(fundPB, 4 / 5):
        return 5
    elif x > np.nanquantile(fundPB, 3 / 5):
        return 4
    elif x > np.nanquantile(fundPB, 2 / 5):
        return 3
    elif x > np.nanquantile(fundPB, 1 / 5):
        return 2
    else:
        return 1


    
def Index_Building(fundscale,t,rep,quantile,fundstyle,indices,fundrate_t):
    '''
    Construct the Growth/Value Index by multiplying the z-score 
    of the valuation of funds in that category by the proportion 
    of the fund's size and the daily price change.
    '''
    b = fundscale.loc[rep, :] / np.nansum(fundscale.loc[rep, :])
    for j in range(quantile):
        a = fundstyle[fundstyle==j+1]
        indices[t,j] = np.nansum(b[a.index]*fundrate_t[a.index])

    END = time.time()
    print(f'{t}finished,taking{END-START}s')
    return indices




