#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


spending = pd.read_pickle("../../output/public_spending/data_spending_per_type.pickle")


# In[3]:


spending['period'] = pd.cut(spending.index.get_level_values('year'), [2007,2012, 2017, 2022], include_lowest=True)


# In[4]:


spendinga = spending.groupby(['ubigeo','period']).mean()


# In[5]:


spendinga.to_pickle("../../output/public_spending/dataspendingperprovinceagg.pickle")

