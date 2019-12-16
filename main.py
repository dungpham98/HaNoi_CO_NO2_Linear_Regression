import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt
import regression_model as rm


fileName = 'Variables.csv'
cooks_d = rm.model(fileName)
while(len(cooks_d) > 0):
	print(cooks_d)
	ds = pd.read_csv(fileName)
	for(index,value) in cooks_d:
		ds = ds.drop([index],axis = 0)
	idx = 0
	fileName = 'Variables'+str(idx)+'.csv'
	ds.to_csv(fileName, index=False, encoding='utf8')
	cooks_d = rm.model(fileName)
	idx = idx + 1