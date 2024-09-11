#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt



# ###### Population

# In[2]:


population = pd.read_pickle("../../output/population/populationperegion.pickle")


# In[3]:


population['ubigeo'] = population['Ubigeo'].replace({'0701':'1501'})


# In[4]:


populationpp = population.groupby("ubigeo").sum().sort_index(axis = 1)


# In[5]:


populationpr = populationpp.assign(ubigeo = lambda df: df.index.str[0:2] + '00').reset_index(drop = True).groupby('ubigeo').sum()


# In[6]:


populationb = pd.concat([populationpp,populationpr]).stack()


# In[7]:


populationb.index.names = ['ubigeo','year']


# ###### Spending

# In[8]:


spending = pd.read_pickle("../../output/public_spending/data_spending.pickle")


# In[9]:


spending['ubigeo'] = spending['ubigeo'].replace({'0701':'1501'})


# In[10]:


spending = spending[spending.year > 2006]


# In[11]:


data = spending.pipe(lambda df: df.groupby(['ubigeo','year','BtnTipoGobierno','TIPO_G'])[['Devengado','PIM']].sum()).rename(columns = lambda col: "USE_" + col)

data = data.join(populationb.rename("pop")).apply(lambda y: y/y['pop'], axis = 1).drop(columns = ['pop'])


# In[12]:


dataprovince = data.loc[data.index.get_level_values(0).str[2:] != '00']

dataregion = data.loc[data.index.get_level_values(0).str[2:] == '00']

dataprovince.loc[:,'region'] = dataprovince.index.get_level_values(0).str[:2]

dataregion.loc[:,'region'] = dataregion.index.get_level_values(0).str[:2]

dataprovince = dataprovince.set_index('region',append= True).stack().unstack([2,3,5])

dataregion = dataregion.set_index('region',append= True).stack().unstack([2,3,5]).reset_index('ubigeo', drop = True)


# In[13]:


datafinal = dataprovince.join(dataregion)

datafinal = datafinal.sort_index(axis = 1).fillna(0)


# In[14]:


datafinal.to_pickle("../../output/public_spending/data_spending_per_type.pickle")

