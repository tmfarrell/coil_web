#! /usr/bin/env python

# imports
import sys
import numpy as np
import MAF

# globals
VALID_CHARS = set(['A','C','G','T','N','X'])

# classes
class Barcode:
	def __init__(self, id, sequence):
		self.id = id
		self.rough_coi = 0
		self.seq = sequence
		
	def __len__(self):
		return(len(self.seq))
		
	def getSeqChars(self):
		charset = set([])
		for s in self.seq:
			charset.add(s)
		return charset
		
	def setRoughCOI(self):
		n_count = self.seq.count('N')
		if n_count <= 0:
			self.rough_coi = 1
		elif n_count == 1:
			self.rough_coi = 2
		else:
			self.rough_coi = 3
			
	def getPosition(self, pos): ##pos is base 0
		return self.seq[pos:pos+1]
		
	def getPositionForMAF(self, pos): ##pos is base 0
		base = self.seq[pos:pos+1]
		#right now, no N seqs are returned so this if statement is never used
		if base == 'N':
			base = 'N'*self.coi
		return base
		
	def predictCOI(self, myMAF, max_coi, threshold, std_out=False):
		# get list of (base, position), filtering out missing positions
		positions = map(lambda (pos, base): (base, pos),\
				myMAF.filter_missing_positions(self.seq))
                #- start -#
		#- bayesian inference computation -#
		coi = 1
		rawCOIs = []
		while coi <= max_coi:
			pos_probs = [myMAF.getProbability(pos, coi) for pos in positions]
			rawCOIs.append(np.prod(pos_probs))
			#~ if self.seq == 'ANN':
				#~ print self.seq, coi, pos_probs
				#~ print np.prod(pos_probs)
			coi += 1
		coi_sum = np.sum(rawCOIs)
		COIs = [x/coi_sum for x in rawCOIs]
		max_posterior_prob = np.amax(COIs)
		coi_prediction_idx = COIs.index(max_posterior_prob)
		confidence_interval = self.getCredibleInterval(COIs, coi_prediction_idx, max_coi, threshold)
		#- end -#
		p = (self.id, self.seq, coi_prediction_idx + 1, confidence_interval, max_posterior_prob)
		if std_out: print('\t'.join(p))
		return(p)
	
	def getCredibleInterval(self, cois, coi_index, max_coi, threshold):
		low = coi_index
		high = coi_index
		sum = cois[coi_index]
		while sum < threshold:
			if low == 0:
				high+=1
				sum += cois[high]
			elif high == max_coi-1:
				low -=1
				sum += cois[low]
			elif cois[low-1] >= cois[high+1]:
				low -=1
				sum += cois[low]
			else:
				high +=1
				sum += cois[high]
		return (low+1, high+1)
	
	def to_zygosity_array(self, mafs, index=False): 
		zygosity_arr = []
		pos_to_maf = mafs.position_to_maf_map()
		if index: zygosity_arr.append(self.id)
		for pos in range(len(self)):
			if not pos in pos_to_maf.keys():  # skip
				continue
			base = self.seq[pos]
			if (base == 'X'): 
				zygosity_arr.append(-1)
				continue
			if (base == 'N'): 
				zygosity_arr.append(0.5) 
				continue
			pos_maf = pos_to_maf[pos]
			if (base != pos_maf.major): 
				zygosity_arr.append(0)
			else: 
				zygosity_arr.append(1)
		return(zygosity_arr)
	
	@staticmethod
	def from_zygosity_array(zygosity_arr, mafs, barcode_id): 
		sequence = ''
		pos_to_maf = mafs.position_to_maf_map()
		for pos in range(len(zygosity_arr)): 
			if not pos in pos_to_maf.keys():  #skip
				continue
			zygosity = zygosity_arr[pos]
			if (zygosity == -1): 
				sequence = sequence + 'X'
				continue
			if (zygosity == 0.5): 
				sequence = sequence + 'N'
				continue
			pos_maf = pos_to_maf[pos]
			if (zygosity == 0): 
				sequence = sequence + pos_maf.minor
			else: 
				sequence = sequence + pos_maf.major
		return(Barcode(barcode_id, sequence))

	def __str__(self): 
		return('Barcode('+self.id+','+self.seq+')')

	def __repr__(self): 
		return('Barcode('+self.id+','+self.seq+')')


class SetOfBarcodes:
	def __init__(self):
		self.barcodes = []  #list of Barcode objects
		self.positions = []
		
	def readBarcodeFile(self, file):
		bc_lines = open(file, 'r').readlines()
		print "Reading barcodes"
		self.readBarcodeFileLines(bc_lines)
	
	def readBarcodeFileLines(self, bc_lines): 
		for bcl in bc_lines:
			if bcl.find("#") == 0:
				continue
			bcl = bcl.rstrip()
			line = bcl.split()
			id_ = line[0]
			myBC = Barcode(id_, line[1])
			myBC.setRoughCOI()
			self.barcodes.append(myBC)
		self.positions = range(len(self.barcodes[0]))
			
	def validate(self, validCharSet=VALID_CHARS):
		first_len = len(self.barcodes[0]) 
		for b in self.barcodes:
			#check for length
			if not len(b) == first_len:
				ret_str = b.id + " length is not the same as first barcode length"
				return (0, ret_str)
			bchar = b.getSeqChars()
			#check for invalid characters
			if not bchar.issubset(validCharSet):
				ret_str = "Invalid character in barcode: " + b.id
				return (0, ret_str)
			if b.seq.count('X') > (first_len/2):
				print "WARNING: " + b.id + " has poor data quality. Consider excluding from analysis"
		return (1, "Barcodes OK")
		
	def computeMAFFromBarcodes(self, padding):
		###does not count barcode if there are any N values
		###Missing data (X) is not added to count for position
		myMAF = MAF.MAF()
		for i in range(len(self.barcodes[0])): 
			myPos = MAF.MAFPosition(i)
			for b in self.barcodes:
				if b.rough_coi > 1: continue
				else: myPos.addChar(b.getPositionForMAF(i))
			myPos.getMAFFromChars()
			myPos.setAlleleProbability(padding)
			#~ if myPos.isPositionInformative():
				#~ myMAF.addPosition(myPos)
			myMAF.addPosition(myPos)  #add position regardless of informative-ness
		return myMAF
	
	def to_zygosity_matrix(self, mafs, header=False, index=False): 
		'''
		converts a set of barcodes { b_ij | b in {A,T,C,G,X,N}, i in {1,...,N}, j in {1,...,M} }  
		         where N is length of the barcodes, M is number of samples, X is a missing base call 
			 and N is a polymorphic base call;

		to a zygosity matrix { x_ij | x in {-1,0,0.5,1}, i in {1,...,N}, j in {1,...,M} }
		         where N and M are the same, and -1 indicates missing base call, 0.5 a het (polymorphic) call, 
			 1 a homo_ref call and 0 a homo_alt call. 
		'''
		zygosity_matrix = []
		if header:  # add position ids
			if index: idx = ['']
			else:     idx = []
			zygosity_matrix.append(idx + map(lambda maf: str(maf.pos), mafs.mafs))
		for b in self.barcodes: 
			zygosity_matrix.append(b.to_zygosity_array(mafs, index=index))
		return(zygosity_matrix)
	
	@staticmethod 
	def from_zygosity_matrix(zygosity_matrix, mafs, header=False, index=False): 
		''' inverse of to_zygosity_matrix '''
		barcode_set = SetOfBarcodes()
		if header: zygosity_matrix.pop(0) # ignore header
		for (barcode_id, zygosity_arr) in enumerate(zygosity_matrix): 
			if index: 
				barcode_set.barcodes.append(Barcode.from_zygosity_array(zygosity_arr[1:], mafs, zygosity_arr[0]))
			else: 
				barcode_set.barcodes.append(Barcode.from_zygosity_array(zygosity_arr, mafs, str(barcode_id)))
		barcode_set.positions = range(len(barcode_set.barcodes[0]))
		return(barcode_set) 
	
	def predictBarcodeCOIs(self,myMAF,max_coi, threshold, std_out=False):
		ps = []
		if std_out: 
			print('\t'.join(("Sample","Barcode","Predicted COI","Confidence Interval","Posterior Probability")))
		for b in self.barcodes:
			ps = ps + [b.predictCOI(myMAF, max_coi, threshold, std_out=std_out)]
		return(ps)

	def __str__(self): 
		return('['+','.join(map(str, self.barcodes))+']')

	def __repr__(self): 
		return('['+','.join(map(repr, self.barcodes))+']')
