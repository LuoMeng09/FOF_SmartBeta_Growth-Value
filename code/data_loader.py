import pandas as pd
def DataLoad(df,date='Date'):
    df_dict = {}  
    names = []
    df = df.T
    df['group'] = (df.isnull().all(axis=1)).cumsum()

    dfs = [v.T for k, v in df.groupby('group')]
    selected_columns = []
    for data in dfs:
        temp = data.loc[date:,:]
        selected_columns.append(temp.columns[~temp.columns.str.contains('Unnamed')][0])
        temp.set_axis(temp.loc[date,:],axis='columns',inplace=True)
        temp = temp.loc[:, temp.columns.notnull()]
        temp.drop(labels=[date,'group'],axis=0,inplace=True)
        if temp.columns.str.contains(date).any():
            temp.drop(labels=[date],axis=1,inplace=True)
        temp.dropna(how='all',inplace=True,axis=1)
        temp.dropna(inplace=True,axis=0)

        name = selected_columns[-1]
        print(name)
        temp.index = pd.to_datetime(temp.index)
        df_dict[name] = temp
    return df_dict