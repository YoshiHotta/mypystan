# mypystan

mypystanはCmdStanの自作ラッパーである。次の二つが不満でラッパーを自作するに至った。  
* PyStanがCmdStanに比べて10倍くらい遅い。  
* PyStanが未完成である。例えばoutput.csvとdiagnostic_fileが読めなかったり、CmdStanから利用できるオプションがPyStanからでは
　利用できないことがある。  

## インストール方法
1. CmdStanをインストールします。  
2. CmdStanインストール時に作成されるmakeをstanmakeに、printをstanprintにエイリアスしてパスを通します。
具体的には、
2.1. .bashrc を開き 　`gedit .bashrc`
2.2. 末尾に、
`Aliasing stanmake, stanprint commands.
alias stanmake='make -f /home/keisukefujii/stan/cmdstan-2.9.0/makefile'
alias stanprint='/home/keisukefujii/stan/cmdstan-2.9.0/bin/print'
`
を記載します。 

## 使用方法
関数名、メソッド名はpystanと同じです。[pystanのAPIの説明](https://pystan.readthedocs.org/en/latest/api.html)を参照して下さい。
めったに使わない引数はサポートしていません。
