# -*- coding: utf-8 -*-
"""
class StanModel:
    self.model_name
    self.model_code

    self.__init__()
    self.show()
    self.execute()
    self.sampling()
    self.optimizing()


class StanFit4Model:
    self.csvFileNames

    self.__init__(self, csvFileNames=None)
    self.plot()
    self.extract()
    self.summary()
    self.stanprint()
"""

__author__ = 'yoshi'

import os, pandas, pystan, collections, numpy, scipy
from exceptions import Exception

import pymc.plots

class StanModel:
    """
    class StanModel:
        self.model_name
        self.model_code

        self.__init__()
        self.show()
        self.execute()
        self.sampling()
        self.optimizing()
    """
    def __init__(self, file=None, model_name='anon_model', model_code=None, cmdstan_home=None):
        try:
            if (file is None and model_code is None) or (file is not None and model_code is not None):
                raise Exception("Exactly one of file or model_code must be specified.")
            elif model_code != None:
                self.model_name = model_name
                self.model_code = model_code
                f = open(model_name + '.stan', 'w')
                f.write(model_code)
                f.close()
                if(cmdstan_home is None):
                    os.system('stanmake ' + model_name)
                else:
                    pwd = os.getcwd()
                    os.chdir(cmdstan_home)
                    os.system('make ' + pwd + '/' + model_name)
                    os.chdir(pwd)
            else:
                if file[-5:] != '.stan':
                    raise Exception('file must has the extension .stan.')
                self.model_name = file[:-5]
                f = open(file)
                self.model_code = f.read()
                if(cmdstan_home is None):
                    os.system('stanmake ' + file)
                else:
                    pwd = os.getcwd()
                    os.chdir(cmdstan_home)
                    os.system('make ' + pwd + '/' + file)
                    os.chdir(pwd)


        except:
            print 'StanModel initialization error.'
            raise

    def show(self):
        outputstr = 'StanModel object ' + '\'' + self.model_name + '\' ' + 'coded as follows\n' + self.model_code
        print outputstr

    def execute(self, args):
        """StanModelで作成した実行ファイルを直接実行する。ターミナルで次のコマンドを実行するのと等価である。
        $./model_name args"""
        command = './' + self.model_name + ' ' + args
        print '$' + command + 'を実行します.'
        os.system(command)
        print 'output.csvが作成されました.'


    def sampling(self, data=None, chains=4, iter=2000, warmup=None, thin=1, save_warmup=False, sample_file=None, algorithm=None, wait_during_sampling=False):
        # generate .stan file
        if ((data is not None) and (sample_file is not None)) or ((data is None) and (sample_file is None)) :
            raise Exception('Exactly one of data or sample_file must be specified.')
        if data is not None:
            if isinstance(data, dict):
                data_dict = data
            elif isinstance(data, pandas.DataFrame):
                data_dict = data.to_dict()
            else:
                raise Exception('data must be a dict or a pandas.DataFrame.')
            self.sample_file =  '.input.data.R'
            pystan.stan_rdump(data_dict, self.sample_file)
        elif sample_file is not None:
            self.sample_file = sample_file

        # num_samples and num_warmup definitions
        if warmup is None:
            warmup = iter // 2

        num_samples = iter - warmup # PyStanとCmdStanで指定の仕方が違うので注意。CmdStanのnum_samplesはwarmup後のデータ数
        num_warmup  = warmup

        # algorithm definition
        if algorithm == 'Fixed_param':
            algorithmAndEigine = 'algorithm=fixed_param'
        elif (algorithm == 'NUTS') or (algorithm is None):
            algorithmAndEigine = 'algorithm=hmc engine=nuts'
        elif algorithm == 'HMC':
            algorithmAndEigine = 'algorithm=hmc engine=static'
        else:
            raise Exception('algorithm must be one of Fixed_param, NUTS (default), and HMC.')

        for i in range(chains):
            command = ''
            command += './' + self.model_name + ' id='+str(i+1)+ ' sample '
            command += 'num_samples=' + str(num_samples) + ' num_warmup=' + str(num_warmup)
            if save_warmup is True:
                command += ' save_warmup=1'
            command += ' ' + algorithmAndEigine
            command += ' data file=' + self.sample_file + ' output file=output' + str(i+1) + '.csv'
            # if wait_during_sampling is true, the final '&' will be omitted.
            if (wait_during_sampling == False) or (i < chains-1): 
                command += '&'
            command += '\n'
            os.system(command)
            print command

        outputFiles = []
        for i in range(1, chains+1):
            outputFiles.append('output' + str(i) + '.csv')
        return StanFit4model(outputFiles)


    def optimizing(self, data=None, sample_file=None, algorithm=None):
        # generate .stan file
        if ((data is not None) and (sample_file is not None)) or ((data is None) and (sample_file is None)) :
            raise Exception('Exactly one of data or sample_file must be specified.')
        if data is not None:
            if isinstance(data, dict):
                data_dict = data
            elif isinstance(data, pandas.DataFrame):
                data_dict = data.to_dict()
            else:
                raise Exception('data must be a dict or a pandas.DataFrame.')
            sampleFileName =  '.input.data.R'
            pystan.stan_rdump(data_dict, sampleFileName)
        elif sample_file is not None:
            sampleFileName = sample_file

        if (algorithm is not None) and (isinstance(algorithm, str) is False):
            raise Exception('algorithm must be a string.')
        elif algorithm is None:
            algorithm = 'LBFGS'

        command = ''
        command += './' + self.model_name + ' optimize '
        command += 'algorithm=' +algorithm.lower()
        command += ' data file=' + sampleFileName
        os.system(command) # this generates a output.csv as default
        outputDataFrame = pandas.read_csv('output.csv', comment='#')
        retDict = outputDataFrame.to_dict()
        del retDict['lp__']

        return collections.OrderedDict(retDict) # PyStanではOrderedDictを返すので真似た。


    def variational(self, data=None, sample_file=None, \
                    algorithm='meanfield', iter=10000, 
                    grad_samples=1, elbo_samples=100, eta=100, 
                    tol_rel_obj=0.01, output_samples=1000):
        """ interface of the  variational inference """
        if ((data is not None) and (sample_file is not None)) or ((data is None) and (sample_file is None)) :
            raise Exception('Exactly one of data or sample_file must be specified.')
        if data is not None:
            if isinstance(data, dict):
                data_dict = data
            elif isinstance(data, pandas.DataFrame):
                data_dict = data.to_dict()
            else:
                raise Exception('data must be a dict or a pandas.DataFrame.')
            sampleFileName =  '.input.data.R'
            pystan.stan_rdump(data_dict, sampleFileName)
        elif sample_file is not None:
            sampleFileName = sample_file

        command = ''
        command += './' + self.model_name + ' variational'
        command += ' algorithm=' +algorithm.lower()
        command += ' iter=' + str(iter)
        command += ' grad_samples=' + str(grad_samples)
        command += ' elbo_samples=' + str(elbo_samples)
        command += ' eta=' + str(eta)
        command += ' tol_rel_obj=' + str(tol_rel_obj)
        command += ' output_samples=' + str(output_samples)
        command += ' data file=' + sampleFileName
        
        os.system(command) # this generates a output.csv as default
    
        outputFiles = []
        outputFiles.append('output.csv')
        return StanFit4model(outputFiles)
        
        
class StanFit4model:
    """
    class StanFit4Model:
        self.csvFileNames

        self.__init__(self, csvFileNames=None)
        self.plot()
        self.extract()
        self.summary()
        self.stanprint()
    """
    def __init__(self, csvFileNames=None):
        if csvFileNames is None:
            self.csvFileNames = ['output.csv']
        elif isinstance(csvFileNames[0], str) is False:
            raise Exception('csvFileNames must be a liest of strings.')
        else:
            self.csvFileNames = csvFileNames

    def plot(self, pars=None):
        """PyStanではpymcのtraceplotを流用している。ここでもそうする。"""
        paraSerieses = self.extract(self)
        paraSeriesesPlot = collections.OrderedDict()
        if pars is None:
            for para, series in paraSerieses.items():
                if para.find('.') == -1:
                    paraSeriesesPlot[para] = series
                else:
                    pass # arrayのモデルパラメータ達はプロットしない。一方PyStanではそういうパラメータもプロットするので注意。
        else:
            for par in pars:
                paraSeriesesPlot[par] = paraSerieses[par]

        pymc.plots.traceplot(paraSeriesesPlot, paraSeriesesPlot.keys())


    def extract(self, pars=None, permuted=True):
        """ OrderedDictを返す。返り値はOrderedDict({'parName': array, ...})の形になっている。
        形式がPyStanとは違う。PyStanでは、
        'parName'がarrayでないモデルパラメータの時はarrayは一次元である。
        'parName'がarrayのモデルパラメータ達の時はarrayは２次元で、サイズはnum_samples * パラメータ数である
        となっているが、本関数では二つを区別していない。"""
        if permuted is True:
            ret = collections.OrderedDict()
            for i in range(0, len(self.csvFileNames)):
                file = self.csvFileNames[i]
                df = pandas.read_csv(file, comment='#')
                for key in df.keys():
                    if key[-2:] == '__': # 最後が__で終わるのはstep_size, lp__等の情報でモデルパラメータではない
                        continue
                    elif i == 0:
                        ret[key] = numpy.array(df[key].tolist())
                    else:
                        ret[key] = numpy.append(ret[key], numpy.array(df[key].tolist()))
                    if i == len(self.csvFileNames) - 1:
                        ret[key] = numpy.random.permutation( ret[key] )
            return ret
        else:
            # 返り値のarrayのshapeを決定する
            df = pandas.read_csv(self.csvFileNames[0], comment='#')
            num_samples = len(df)
            chains = len(self.csvFileNames)
            num_para = 0
            for key in df.keys():
                    if key[-2:] != '__': # 最後が__で終わるのはstep_size, lp__等の情報でモデルパラメータではない
                        num_para += 1

            ret = numpy.zeros([num_samples, chains, num_para ])
            for i_file in range(0, len(self.csvFileNames)):
                file = self.csvFileNames[i_file]
                df = pandas.read_csv(file, comment='#')
                j_para = 0
                for key in df.keys():
                    if key[-2:] == '__': # 最後が__で終わるのはstep_size, lp__等の情報でモデルパラメータではない
                        continue
                    else:
                        ret[:,i_file,j_para] = numpy.array(df[key].tolist())
                        j_para += 1

            return ret


    def extract_array(self, pars=None, permuted=True):
        """ Extract method that store the array-parameters as dictionary of arrays 
        
            Currently, only the vector-parameter and matrix-parameters are supported
        """
        dic = self.extract(pars, permuted)
        ret = collections.OrderedDict()
        # check if key is an array-parameter
        for key, value in dic.items():
            split_key = key.split('.')
            # scalar parameter
            if len(split_key)==1: 
                ret[split_key[0]] = value
            # array parameter
            else:
                # first attribute
                if split_key[0] not in ret:
                    ret[split_key[0]] = []
                    # vector parameter
                    if len(split_key) == 2:
                        ret[split_key[0]].append(value)
                    # matrix parameter
                    elif len(split_key) == 3:
                        ret[split_key[0]].append([value])
                    # tensor parameter
                    else:
                        raise "tensor parameter is not currently supported"
                    
                # not the first attribute
                else:
                    # vector parameter
                    if len(split_key) == 2:
                        ret[split_key[0]].append(value)
                    # matrix parameter
                    elif len(split_key) == 3:
                        row = int(split_key[1])-1
                        # first column
                        if len(ret[split_key[0]]) <= row:
                            ret[split_key[0]].append([value])
                        else:
                            ret[split_key[0]][row].append(value)
                    else:
                        raise "tensor parameter is not currently supported"
                    
        return ret                
        
        
    # def _extract(self):
    #     """.plot用にextractする。"""
    #     # 返り値のarrayのshapeを決定する
    #     df = pandas.read_csv(self.csvFileNames[0], comment='#')
    #     num_samples = len(df)
    #     chains = len(self.csvFileNames)
    #     num_para = 0
    #     retList = []
    #     for key in df.keys():
    #         if key[-2:] != '__': # 最後が__で終わるのはstep_size, lp__等の情報でモデルパラメータではない
    #             num_para += 1
    #             retList.append(key)
    #
    #     retArray = numpy.zeros([num_samples, chains, num_para ])
    #     for i_file in range(0, len(self.csvFileNames)):
    #         file = self.csvFileNames[i_file]
    #         df = pandas.read_csv(file, comment='#')
    #         j_para = 0
    #         for key in df.keys():
    #             if key[-2:] == '__': # 最後が__で終わるのはstep_size, lp__等の情報でモデルパラメータではない
    #                 continue
    #             else:
    #                 retArray[:,i_file,j_para] = numpy.array(df[key].tolist())
    #                 j_para += 1
    #
    #     return (retList, retArray)


    def summary(self):
        """stanprintと同じ"""
        self.stanprint()

    def stanprint(self):
        self.csvFileNames
        os.system('stanprint ' + ' '.join(self.csvFileNames) + ' > summary.txt')
        f = open('summary.txt')
        print f.read()

#    def get_csv_content(self):
#        f = open(self.csvFileName)
#        fileContent = f.read()
#        f.close()
#        return fileContent