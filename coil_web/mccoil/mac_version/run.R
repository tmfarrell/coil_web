path= "/seq/plasmodium/COIL/THEREALMCCOIL/categorical_method/"  ##enter your path here
setwd(path)
source("McCOIL_categorical_linux.R")

args = commandArgs(trailingOnly=TRUE)
datai = read.table(paste(path, args[1], sep=""), head=T)
data = datai[,-1]
rownames(data) = datai[,1]

McCOIL_categorical(data, maxCOI=25, totalrun=5000, burnin=100, M0=15, e1=0.05, e2=0.05, err_method=3, path=getwd(), output="output_test.txt")
#eof
