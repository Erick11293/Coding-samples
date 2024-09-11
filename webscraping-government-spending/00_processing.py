#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


import json


# #antes del 2011
# 1 PIA
# 2 PIM
# 3 Compromiso
# 4 Devengado
# 5 Girado
# 
# #Despues del 2011
# 1 PIA
# 2 PIM
# 3 Certificacion
# 4 Compromiso
# 5 Atencion del compromiso
# 6 Devengado
# 7 Girado
# 

# In[3]:


def process_obs(row, level_name, levels):
    try:
        df = pd.DataFrame(map(lambda y: y.split("/"), row.split(",")))
        #Eliminando Certificacion y atencion del compromiso
        if len(df.columns) == 8:
            df = df[[0,1,2,3,5,6]]
            df.columns = [0,1,2,3,4,5]
        df = df.rename(columns = {0: level_name,
                                  1: 'PIA',
                                  2: 'PIM',
                                  3: 'Compromiso',
                                  4: 'Devengado',
                                  5: 'Girado'}
                      )
        for level in levels.keys():
            df[level] = levels[level]
        #df.set_index([0])
        #df.index.name = level_name
        return df
    except:
        return pd.DataFrame()


# In[4]:


def dim_transform(list_):
    dim_ = {}
    for i, item in enumerate(list_[:-1:2]):
        dim_[item] = list_[2*i + 1]
    return [dim_, list_[-1]]


# In[ ]:





# In[5]:


def process_file(file):
    data_departamentos = pd.read_csv(file)

    data_departamentos.index.name = 'obs'
    data_departamentos['year'] = data_departamentos['url'].apply(lambda y: y.split("=")[1].split("&")[0])
    data_departamentos['hierarchy'] = data_departamentos['hierarchy'].str.replace("]","").str.replace("]","").str.split(",")
    data_departamentos['hierarchy'] = data_departamentos['hierarchy'].apply(lambda y: [value.split("/")[0] for value in y][1:])
    data_departamentos['detail'] = data_departamentos['hierarchy'].apply(dim_transform)
    
    data_all = pd.concat(data_departamentos.apply(lambda row: process_obs(row['data'], row['detail'][-1], row['detail'][0]), axis = 1).values, keys= data_departamentos.index)
    data_all['PIA'] = data_all['PIA'].apply(pd.to_numeric)
    data_all['PIM'] = data_all['PIM'].apply(pd.to_numeric)
    data_all['Compromiso'] = data_all['Compromiso'].apply(pd.to_numeric)
    data_all['Devengado'] = data_all['Devengado'].apply(pd.to_numeric)
    data_all['Girado'] = data_all['Girado'].apply(pd.to_numeric)
    
    data_all = data_all.join(data_departamentos['year'])

    return data_all


# In[6]:


file= "../../interm/public_spending/data_prov.csv"

data_2004_2019 = process_file(file)


# In[ ]:


file= "../../interm/public_spending/data_2017.csv"

data_2017 = process_file(file)


# In[ ]:


file= "../../interm/public_spending/data_2019_2021.csv"

data_2019_2021 = process_file(file)


# In[ ]:


file= "../../interm/public_spending/data_2022.csv"

data_2022 = process_file(file)


# In[ ]:


data = data_2004_2019[~data_2004_2019.year.isin(["2017","2019"])].append(data_2019_2021).append(data_2017).append(data_2022)


# In[ ]:


data['year'] = data['year'].apply(int)


# In[ ]:





# In[ ]:


clasiffication = pd.read_excel("../../external/classification.xlsx", sheet_name=None, dtype = str)


# In[ ]:


clasiffication['GENERICA_N_2'].iloc[:,0] = clasiffication['GENERICA_N_2'].iloc[:,0].apply(lambda y: y[:-1] + "-" + y[-1])


# In[ ]:


data_1 = data[data.year < 2009]
data_2 = data[data.year >= 2009]


# In[ ]:


data_1 = data_1.merge(clasiffication['FUNCION_C_1'], how = 'left').merge(clasiffication['GENERICA_N_1'], how = 'left')
data_2 = data_2.merge(clasiffication['FUNCION_C_2'], how = 'left').merge(clasiffication['GENERICA_N_2'], how = 'left')


# In[ ]:


data = pd.concat([data_1, data_2])


# In[ ]:


data.columns = data.columns.str.split("$").str[-1]


# In[ ]:


data['ubigeo'] = data["BtnDepartamentoMeta"] + data["BtnProvincia"].fillna("00")


# In[ ]:


data.to_pickle("../../output/public_spending/data_spending.pickle")

