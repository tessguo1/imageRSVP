from pandas import Series, DataFrame
#calculate mean at each level of list
# http://pandas.pydata.org/pandas-docs/dev/groupby.html
lst = [1, 2, 3, 1, 2, 3]

s = Series([1, 2, 3, 10, 20, 30], lst)

grouped = s.groupby(level=0)

grouped.mean()

import numpy as np
intensities = np.array([.7,.7,.7,.7,.7,.8,.8,.8,.8,.9,.9,.9,1.0,1.0,1.0,2.0,2.0,2.0]) #debug, example data
responses= np.array([0,0,0,0,0 ,     0,1,0,0,     1,1,0,    1,1,1,        1,1,1]) #debug, example data

df= DataFrame({'intensity': intensities, 'response': responses})
grouped = df.groupby('intensity')
print('mean at each intensity')
grouped = grouped.mean()
print( grouped )
y=list(grouped['response'])
print('list(grouped)=',y)

