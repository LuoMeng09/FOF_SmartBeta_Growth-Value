import pandas as pd
import numpy as np

def Tran_Nan (netvalue):
    for i in netvalue.columns:
        netvalue.loc[:,i] = pd.to_numeric(netvalue.loc[:,i],'coerce')
    return netvalue

def Tran_Return(netvalue):
    '''counting returns'''
    netvalue_chg = (netvalue - netvalue.shift(1))/netvalue.shift(1)
    netvalue_chg = netvalue_chg.dropna(axis = 0, how = 'all')
    return netvalue_chg


def Outlier_Seperate(factor):
    ''' processing outliers'''
    factor.dropna(axis=1, how='all', inplace=True) 
    factor = factor.T.drop_duplicates(keep='first').T
    factor_temp = pd.DataFrame(index=factor.index)
    for name in factor.columns: 
        fac_temp = pd.DataFrame()
        fac_temp = factor[name].dropna()
        std_upper, std_lower = fac_temp.mean() + fac_temp.std()*3, fac_temp.mean() - fac_temp.std()*3
        fac_temp[fac_temp > std_upper] = std_upper
        fac_temp[fac_temp < std_lower] = std_lower 
        factor_temp = pd.concat([factor_temp,fac_temp],axis=1)
    factor = factor_temp
    return factor

def Name_Process(data,direct='index'):
    if direct=='index':
        name = []
        for i in data.index:
            name.append(i)
        name = list(map(lambda x: re.sub(u"\\(.*?\\)|\\:|\\（.*?\\）|" "|.1","", \
                                     name[x]), [x for x in range(len(name))]))
        data.index = name
    elif direct=='columns':
        name = []
        for i in data.columns:
            name.append(i)
        name = list(map(lambda x: re.sub(u"\\(.*?\\)|\\:|\\（.*?\\）|" "|.1","", \
                                     name[x]), [x for x in range(len(name))]))
        data.columns = name
    elif direct=='extranameindex':
        name = []
        for i in data.index:
            name.append(i)
        name = list(map(lambda x: re.sub(u"\\(.*?\\)|[\u4e00-\u9fa5]|\n","",name[x]), [x for x in range(len(name))]))
        data.index = pd.to_datetime(name)
    elif direct=='extranamecolumns':
        name = []
        for i in data.columns:
            name.append(i)
        name = list(map(lambda x: re.sub(u"\\(.*?\\)|[\u4e00-\u9fa5]|\n","",name[x]), [x for x in range(len(name))]))
        data.columns = pd.to_datetime(name)
    return data

def Reindex_processing(index):
    '''processing reindex'''
    index= index[~index.index.duplicated(keep='first')]
    index.index.name = 'DATES'
    index.index = pd.to_datetime(index.index)
    return index

def Dropnan(factor):
    factor.dropna(axis=0,how='all',inplace=True)
    factor.dropna(axis=1,how='all',inplace=True)
    return factor

def StandardSeperate(factor):
    '''Standardize'''    
    factor = factor.T.drop_duplicates(keep='first').T
    factor_temp = pd.DataFrame( index = factor.index )
    for name in factor.columns:       
        fac_temp = pd.DataFrame(factor[name].dropna())
        index_f, columns_f = fac_temp.index , name
        standard_scale = StandardScaler().fit(fac_temp) 
        fac_temp = pd.DataFrame(standard_scale.transform(fac_temp), index = index_f, columns = [columns_f])
        factor_temp = pd.concat([factor_temp,fac_temp],axis=1)
    factor = factor_temp
    factor = factor.replace(0, np.nan).dropna(axis=1, how='all')
    return factor