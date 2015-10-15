__author__ = 'yoshi'

import  mypystan
reload(mypystan)

m = mypystan.StanModel(file='bernoulli.stan')
fitResult = m.sampling(sample_file='bernoulli.data.R', algorithm='NUTS', save_warmup=False, chains=2)
fitResult.plot()
fitResult.csvFileNames
fitResult.summary()
fitResult.stanprint()
m.optimizing(sample_file='bernoulli.data.R')

m = mypystan.StanModel(file='logistic.stan')
fitResult = m.sampling(sample_file='data2.dat', algorithm='NUTS', save_warmup=False, chains=2)
fitResult.plot()
fitResult.csvFileNames
fitResult.summary()
fitResult.stanprint()
m.optimizing(sample_file='data2.dat')