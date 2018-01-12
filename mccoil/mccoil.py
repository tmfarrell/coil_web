#!/usr/bin/env python

### prelims 
## import rpy2
from rpy2 import robjects
import rpy2.rlike.container as rlc
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage

## import COIL modules
import sys
sys.path.append('coil_python/')
import MAF, Barcode

mccoil_R = 'mccoil/mac_version/McCOIL_categorical.R'

### functions  
## zygosity matrix => R dataframe
def to_R_zygosity_df(zygosity_matrix, header=True, index=True): 
    '''  converts python zygosity dataframe into R dataframe  '''
    # fill in samples/ positions
    samples = []
    positions = []
    if header: samples = range(1, len(zygosity_matrix))
    else:      samples = range(len(zygosity_matrix))
    if index: positions = range(1, len(zygosity_matrix[0]))
    else:     positions = range(len(zygosity_matrix[0]))
    # add header fields to data_dict (used to init R DataFrame)
    data_dict = {}
    pos_to_col_map = {}
    if header:
        for pos in positions: 
            pos_to_col_map[pos] = zygosity_matrix[0][pos]
            data_dict[zygosity_matrix[0][pos]] = []
    else: 
        for pos in positions: data_dict[pos] = []
    # fill data_dict
    for sample in samples:
        for pos in positions: 
            if header: 
                data_dict[pos_to_col_map[pos]] = data_dict[pos_to_col_map[pos]] + [zygosity_matrix[sample][pos]]
            else: 
                data_dict[pos] = data_dict[pos] + [zygosity_matrix[sample][pos]]
    # transform into R data struct
    data_ordered = []
    for pos in positions:
        if header: 
            data_ordered = data_ordered + [(pos_to_col_map[pos], robjects.FloatVector(data_dict[pos_to_col_map[pos]]))]
        else: 
            data_ordered = data_ordered + [(pos, robjects.FloatVector(data_dict[pos]))]
    return(robjects.DataFrame(rlc.OrdDict(data_ordered)))

# takes barcode and maf file lines and uses mccoil to predict cois and mafs
# equivalent to COIL.exec_from_raw_input()
def run_mccoil(barcode_file_lines, maf_file_lines=None, verbose=False): 
    ## init barcode set
    barcode_set = Barcode.SetOfBarcodes()
    barcode_set.readBarcodeFileLines(barcode_file_lines)
    # validate
    is_valid_barcode_set, err_msg = barcode_set.validate()
    if not is_valid_barcode_set: print err_msg; return([])
    ## init mafs
    if not maf_file_lines: 
        mafs = barcode_set.computeMAFFromBarcodes(1)
    else: 
        mafs = MAF.MAF()
        mafs.readMAFFileLines(maf_file_lines)
    mafs_R_vector = robjects.Vector(mafs.minor_allele_freqs())
    # validate
    is_valid_mafs, err_msg = mafs.validate()
    if not is_valid_mafs: print err_msg; return({})
    ## compute zygosity matrix, then convert to R DataFrame
    zygosity_matrix = barcode_set.to_zygosity_matrix(mafs, header=True, index=True)
    if verbose: print(zygosity_matrix)
    data = to_R_zygosity_df(zygosity_matrix)
    if verbose: print(data)
    ## import MCCOIL
    mccoil_R_code = open(mccoil_R, 'r').read()
    mccoil = SignatureTranslatedAnonymousPackage(mccoil_R_code, 'mccoil') 
    ## compute result
    result = mccoil.McCOIL_categorical(data, P=mafs_R_vector) 
    #print result
    ## get sites/samples
    sites, samples = list(result[-2]), list(result[-1])
    ## get maf/coi predictions, which map 1-to-1 sites/samples  
    # (i.e. maf_prediction[i] is prediction for site[i])
    maf_predictions, coi_predictions = list(result[6]), list(result[5])
    return({'mafs': zip(sites, maf_predictions), 'cois': zip(samples, coi_predictions)}) 


### main 
def main(): 
    pass

if __name__ == '__main__': 
    main()
