import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.outliers_influence import variance_inflation_factor

def directionDefine(colName):
	if(colName[-2] == '_1' or colName[-1] == '_2' or colName[-1] == '_3' or colName[-1] == '_4' or colName[-1] == '_5' or colName[-1] == '_7'):
		return False
	else:
		return True

def paramDefine(param):
	if(param > 0):
		return  True
	else:
		return False

def model(csv_file):
	ds = pd.read_csv(csv_file)
	#target
	y = ds['CO']
	row_len=y.shape[0]
	count = 0
	start_r2 = None
	adj_r2_b1= []
	params= None
	removeName = 0

	#calculate adj r2
	colNames = []
	colNamesB2 = []
	for (columnName, columnData) in ds.iteritems():
		colNames.append(columnName)
		colNamesB2.append(columnName)
	colNames=colNames[5:]
	colNamesB2 = colNamesB2[5:]

	while(len(colNames) > 0):
		start_r2 = None
		adj_r2_b1= []
		for colName in colNames:
			x = ds[colName]
			X_1=sm.add_constant(x)
			#print(X_1)
			results = sm.OLS(y, X_1).fit()
			if(start_r2 is None):
				start_r2 = results.rsquared_adj
				removeName = colName
				params = results.params
				adj_r2_b1=[colName,results.rsquared_adj]
			else:
				if(start_r2 < results.rsquared_adj):
					start_r2 = results.rsquared_adj
					removeName = colName
					params = results.params
					adj_r2_b1=[colName,results.rsquared_adj]
		#compare direction of effect vs params
		if(directionDefine(removeName) == paramDefine(params[1])):
			break
		else:
			print('rev')
			colNames.remove(removeName)
	colNamesB2.remove(removeName)
	approveNames = [removeName]
	params_b2 = []
	adj_r2_b2 = None
	results_b2 = 0
	#update the model with adj r2
	while(len(colNamesB2) > 0):
		increase = None
		approve = 0
		currentName = 0
		params_arr = []
		results_b1 = 0
		#stack the current variables
		len_name = len(approveNames)
		sum_x = np.reshape(np.array(ds[approveNames[0]]),(row_len,1))
		if(len_name != 1):
			for name in approveNames[1:]:
				x2 = np.reshape(np.array(ds[name]),(row_len,1))
				sum_x = np.hstack((sum_x,x2))
		#run model and get the maximum adj r2
		for colName in colNamesB2:
			x = ds[colName]
			x1 = np.reshape(np.array(x),(row_len,1))
			xx = np.hstack((x1,sum_x))
			X_1=sm.add_constant(xx)
			#print(X_1)
			results = sm.OLS(y, X_1).fit()
			#compare adj rsquare increase
			col_increase = results.rsquared_adj-adj_r2_b1[1]
			if(increase is None):
				increase = results.rsquared_adj-adj_r2_b1[1]
				currentName = colName
				results_b1 = results
				adj_r2_b2=[colName,results.rsquared_adj]
				params_arr = []
				i = 2
				for name in approveNames:
					params_arr.append((name,results.params[i],results.pvalues[i]))
					i = i + 1
				params_arr.append((colName,results.params[1],results.pvalues[1]))
			else:
				if(col_increase > increase):
					increase = col_increase
					currentName = colName
					results_b1 = results
					adj_r2_b2=[colName,results.rsquared_adj]
					params_arr = []
					i = 2
					for name in approveNames:
						params_arr.append((name,results.params[i],results.pvalues[i]))
						i = i + 1
					params_arr.append((colName,results.params[1],results.pvalues[1]))
		if(increase > 0.01):
			approve = approve + 1
		#compare between predefine params and current direction
		direction = True
		for (name,param,value) in params_arr:
			if(directionDefine(name) != paramDefine(param)):
					direction = False
		if(direction):
			approve = approve +1
		if(approve == 2):
			#print('approve')
			#print(params_arr)
			#print(increase)
			approveNames.append(currentName)
			params_b2 = params_arr
			results_b2 = results_b1
			adj_r2_b1 = adj_r2_b2
		colNamesB2.remove(currentName)
	print(params_b2)
	print(results_b2.summary())

	params_b3 = []
	#p-value 
	sum_x = []
	p_check = True
	while(p_check):
		params_b3 = []
		p_check = False
		len_name = len(approveNames)
		if(len_name == 0):
			break
		sum_x = np.reshape(np.array(ds[approveNames[0]]),(row_len,1))
		if(len_name != 1):
			for name in approveNames[1:]:
				x2 = np.reshape(np.array(ds[name]),(row_len,1))
				sum_x = np.hstack((sum_x,x2))
		X_1=sm.add_constant(sum_x)
		results = sm.OLS(y, X_1).fit()
		#print(results.summary())
		i = 1
		for name in approveNames:
			params_b3.append((name,results.pvalues[i]))
			i = i + 1
		print(params_b3)
		for (name,value) in params_b3:
			if(value > 0.1):
				approveNames.remove(name)
				p_check = True

	print(params_b3)
	print(approveNames)

	vif_check = False
	while(vif_check == False):
		vif_check = True
		removeName = []
		print(approveNames)
		len_name = len(approveNames)
		if(len_name == 0):
			break
		sum_x = np.reshape(np.array(ds[approveNames[0]]),(row_len,1))
		if(len_name != 1):
			for name in approveNames[1:]:
				x2 = np.reshape(np.array(ds[name]),(row_len,1))
				sum_x = np.hstack((sum_x,x2))
		Xc = sm.add_constant(sum_x)
		for i in range(Xc.shape[1]):
			vif = variance_inflation_factor(Xc,i)
			if(i > 0):
				print(approveNames[i-1])
				print(vif)
			if(vif > 3):
				if(i > 0):
					removeName.append(approveNames[i-1])
					vif_check = False
		for name in removeName:
			approveNames.remove(name)



	len_name = len(approveNames)
	final_cooks = []
	if(len_name != 0):
		sum_x = np.reshape(np.array(ds[approveNames[0]]),(row_len,1))
		if(len_name != 1):
			for name in approveNames[1:]:
				x2 = np.reshape(np.array(ds[name]),(row_len,1))
				sum_x = np.hstack((sum_x,x2))
		X_VIF=sm.add_constant(sum_x)
		results_vif = sm.OLS(y, X_VIF).fit()

		print(approveNames)
		print(results_vif.summary())

		infl = results_vif.get_influence()
		sm_fr = infl.summary_frame()
		cooks_d = sm_fr['cooks_d']
		
		for i in range(len(cooks_d)):
			if(cooks_d[i] > 1):
				final_cooks.append((i,cooks_d[i]))
	return final_cooks