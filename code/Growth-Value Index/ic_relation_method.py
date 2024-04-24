'''
IC (Information Coefficient) is a measure used to analyze the coefficient 
of the selected factor's exposure to the cross-sectional changes in the benchmark. 
This indicator is often used to judge the predictive power of multi-factor models. 
The determination of a fund's style depends on its relationship with value and growth funds. 
When the value IC is greater than the growth IC, the fund is judged to be value-oriented; 
otherwise, it is growth-oriented.
To address the issue of fund style drift, 
we map the relationship between growth and value ICs onto a two-dimensional coordinate system (X0, Y0), 
drawing a straight line at a 45-degree angle with the origin (0, 0) as the midpoint. 
The further away from this line, the more pronounced the corresponding style characteristic.
'''

import pandas as pd
import numpy as np

def get_reg_result(y01, y02, factor_dict, time, count, part, year):
    '''IC test : ic value'''
    reg_result = pd.DataFrame()
    
    for factor_sheet in factor_dict:
        factor_data = factor_dict[factor_sheet]
        factor_data = pd.DataFrame(factor_data)

        for factor in factor_data.columns:
            begin = max(pd.Timestamp('{}-1-1'.format(year)), factor_data[factor].dropna().index[0])
            end = factor_data[factor].dropna().index[-1]

            reg_data01 = pd.concat([y01, factor_data[factor]], axis=1).loc[begin: end].fillna(method='ffill')
            reg_data02 = pd.concat([y02, factor_data[factor]], axis=1).loc[begin: end].fillna(method='ffill')
            reg_data01 = reg_data01.dropna()
            reg_data02 = reg_data02.dropna()

            if len(factor_data[factor].loc[begin: end].dropna()) <= time and count=='True':
                factor = factor+'_1year'
            reg_result.loc[factor, 'begin_date'] = begin
            reg_result.loc[factor, 'end_date'] = end
            reg_result.loc[factor, 'IC_value'] = reg_data01.corr().iloc[0,1]
            reg_result.loc[factor, 'IC_growth'] = reg_data02.corr().iloc[0,1]
            

            print(year, begin, end, factor_sheet, factor)
    return reg_result

def get_all_result(y, factor_dict, part):
    ''' IC test : factor selected'''
    reg_result = pd.DataFrame()
    year = y.dropna().index[0]
    for factor_sheet in factor_dict:
        factor_data = factor_dict[factor_sheet]
        factor_data = pd.DataFrame(factor_data)

        for factor in factor_data.columns:
            begin = max(year, factor_data[factor].dropna().index[0])
            end = factor_data[factor].dropna().index[-1]

            reg_data = pd.concat([y, factor_data[factor]], axis=1).loc[begin: end].fillna(method='ffill')
            reg_data = reg_data.dropna()

            reg_result.loc[factor, 'begin_date'] = begin
            reg_result.loc[factor, 'end_date'] = end
            m1 = sm.OLS(reg_data.iloc[:, 0], sm.add_constant(reg_data.iloc[:, 1]), missing='drop').fit()
            reg_result.loc[factor, 'IC'] = reg_data.corr().iloc[0,1]
            reg_result.loc[factor, 'RankIC'] = reg_data.corr(method='spearman').iloc[0, 1]
            reg_result.loc[factor, 'param'] = m1.params.values[1]
            reg_result.loc[factor, 'pvalue'] = m1.pvalues.values[1]
            reg_result.loc[factor, 'tvalue'] = m1.tvalues.values[1]
            reg_result.loc[factor, 'adjR2'] = m1.rsquared_adj            

            print( year, begin, end, factor_sheet, factor)

    return reg_result

def Euclidean_distance(k,point,part):
    '''Calculate the distance from a point to a line'''
    pointindex = point.copy()
    for i in pointindex.index:
        x = pointindex.loc[i,'IC_value']
        y = pointindex.loc[i,'IC_growth']
        pointindex.loc[i,'distance'] = math.fabs(k*x-y)/math.sqrt(k*k+1)
    pointindex.dropna(axis=0, how='any',inplace=True)

    return pointindex


def Compare(netvalue,part):
    '''Classify funds based on their size relationships.'''
    comparevalue = netvalue.copy()
    comparevalue = Euclidean_distance(1,comparevalue,part)
    for i in comparevalue.index:
        if comparevalue.loc[i,'IC_value'] >= comparevalue.loc[i,'IC_growth']:
            comparevalue.loc[i,'size_relationship'] = 1
        else :
            comparevalue.loc[i,'size_relationship'] = 0

    return comparevalue 


def Scale_weight(scale):
    '''Allocate fund weights according to their proportional sizes.'''
    scale_index = scale.copy()
    scale_sum = pd.DataFrame(scale_index.sum(axis=0))
    for i in scale.index:
        for j in scale.columns:
            scale_index.loc[i,j] = scale_index.loc[i,j]/scale_sum.loc[j,0]
    return scale_index

def Style_change(compareyears,position,part,dis_compress):
    '''Select the most recent period for style rotation selection, and observe changes in fund styles.'''
    backet_growth = pd.DataFrame()
    backet_value = pd.DataFrame()
    for i in compareyears.index:
        if compareyears.loc[i][part] == 1:
            backet_value.loc[i,'style'] = 'value'
            if dis_compress == 'True' and compareyears.loc[i][-2] != compareyears.loc[i][-1] and compareyears.loc[i][-2] != compareyears.loc[i][-3]:
                backet_value.loc[i,'size'] = 0
            else :
                backet_value.loc[i,'size'] = position.loc[i][part]
        elif compareyears.loc[i][part] == 0:
            backet_growth.loc[i,'style'] = 'growth'
            if dis_compress == 'True' and compareyears.loc[i][-2] != compareyears.loc[i][-1] and compareyears.loc[i][-2] != compareyears.loc[i][-3]:
                backet_growth.loc[i,'size'] = 0
            else :
                backet_growth.loc[i,'size'] = position.loc[i][part]

    return backet_value, backet_growth


