#! /usr/bin/env python

import sys, getopt
import Barcode, MAF #, Tally, Likelihood, Probability

## globals
PADDING = 1
MAX_COI = 5
ERROR = 0.05
error_file = ""
CI_THRESHOLD = 0.95
get_MAF_from_barcode = 1
VALID_CHARS = set(['A','C','G','T','N','X'])

## cmd line interface usage fcns 
def usage_barcodeFormat():
	print("""Formatting issue with barcode file.  
	
	Barcode format criteria:
	All sample lines must have the same number of columns.
	No field may have spaces.
	Valid barcode sequence characters are A,C,G,T,X,N.
	All barcode sequences must be the same length.
	Only bi-allelic assays are permitted.
	""")
	
def usage_MAFFile():
	print("""Formatting issue with MAF file.
	
	MAF format criteria:
	# positions must be equal to # barcode positions.
	Minor allele frequency must be [0.0,0.5].
	""")
	
def usage_ErrorFile():
	print("""Formatting issue with Error File.
	
	Format criteria:
	Lines with '#' will not be read.
	2 columns: [position] [error rate].
	Error rate must be [0.0,1.0).
	Each assay must have an error rate specified.
	""")

def usage():
	print("""python COIL.py [options] -b [barcode file]
	
	Required:
	-b, --barcode [file]
		where [file] contains sample names and barcodes
	
	Optional:
	-m, --maf [file]
		where [file] contains minor allele frequencies for each assay
	-c, --max_coi [integer]
		where [integer] is the maximum allowable COI for analysis
		default = 5
	-s, --subset [file]
		where [file] is a list of samples contained in [barcode file]
	-e, --error [float]
		where [float] is a number [0.0,1.0)
		default = 0.05
	-E, --error_file [file]
		where [file] contains the error rate for each assay
	-i, --credible_inteval [float]
		where [float] is a number (0.0,1.0]
		default = 0.95
	""")

## for using COIL via web interface 
def exec_from_raw_input(barcode_file_lines, maf_file_lines=None): 
	# read barcodes
	barcodes = Barcode.SetOfBarcodes()
	barcodes.readBarcodeFileLines(barcode_file_lines)
	is_valid_barcode, err_msg = barcodes.validate()
	if not is_valid_barcode:
		print(err_msg)
		return([])
	# read mafs
	if not maf_file_lines: 
		mafs = barcodes.computeMAFFromBarcodes(PADDING)
	else: 
		mafs = MAF.MAF()
		mafs.readMAFFileLines(maf_file_lines)  
	# validate MAFs 
	is_valid_mafs, err_msg = mafs.validate()
	if not is_valid_mafs:
		print(err_msg)
		return([])
	# add genotyping errors
	mafs.setErrorFromConstant(ERROR)
	# compute COI predictions
	cois = [(id_,coi_pred) for (id_,seq,coi_pred,confidence_interval,posterior)
		 in barcodes.predictBarcodeCOIs(mafs, MAX_COI, CI_THRESHOLD)] 
	maf_vals = [(maf.pos, maf.minor_freq) for maf in mafs.mafs]
	return({'cois': cois, 'mafs': maf_vals})
	

## cmd line program
def main(argv):
	MAF_file = ""
	barcode_file = ""
	ERROR = 0.05
	MAX_COI = 15
	verbose = False
	CI_THRESHOLD = 0.95
	try: 
		opts, args = getopt.getopt(argv, "b:m:s:e:E:i:c:",
					   ["barcode=","maf=","subset=","error=","error_file=","credible_interval=","max_coi="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-b","--barcode"):
			barcode_file = arg
			get_MAF_from_barcode = 1
		elif opt in ("-m","--maf"):
			get_MAF_from_barcode = 0
			MAF_file = arg
		elif opt in ("-s","--subset"):
			subset_barcodes = 1
			subset_file = arg
		elif opt in ("-e","--error"):
			ERROR = float(arg)
			if ERROR < 0 or ERROR > 1:
				sys.exit("Error must be [0,1)")
		elif opt in ("-E", "--error_file"):
			ERROR = -1
			error_file = arg
		elif opt in ("-i","--credible_interval"):
			CI_THRESHOLD = float(arg)
			if CI_THRESHOLD<=0 or CI_THRESHOLD > 1:
				sys.exit("Credible Interval must be (0,1]")
		elif opt in ("-c","--max_coi"):
			MAX_COI = int(arg)
	
	###Read barcode file, create barcode set, validate barcodes
	barcodes = Barcode.SetOfBarcodes()
	barcodes.readBarcodeFile(barcode_file)
	print(len(barcodes.barcodes), "barcodes read")
	bc_valid = barcodes.validate(VALID_CHARS)
	if bc_valid[0] == 0:
		print(bc_valid[1])
		usage_barcodeFormat()
		sys.exit(2)
	
	###MAF Handling
	myMAF = MAF.MAF()
	if get_MAF_from_barcode == 0:
		myMAF.readMAFFile(MAF_file)
		maf_valid = myMAF.validate()
		if maf_valid[0]==0:
			print(maf_valid[1])
			usage_MAFFile()
			sys.exit(2)
	else:
		myMAF = barcodes.computeMAFFromBarcodes(PADDING)
	if verbose: print(myMAF.head(150))

	###Add genotyping error tolerance
	if ERROR >= 0:
		myMAF.setErrorFromConstant(ERROR)
	else:
		ret = myMAF.setErrorFromErrorFile(error_file)
		if ret == 0:
			usage_ErrorFile()
			sys.exit(2)
	###Allele Computations
	barcodes.predictBarcodeCOIs(myMAF, MAX_COI, CI_THRESHOLD, std_out=True)
	
	
if __name__ == "__main__":
	if len(sys.argv) == 1:
		sys.exit(usage())
	else:
		main(sys.argv[1:])
