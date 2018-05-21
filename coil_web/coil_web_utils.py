#!/usr/bin/python

import sys
#sys.path.append('/home/tfarrell/anaconda2/lib/python2.7/site-packages/')
import StringIO
import pandas as pd
# COIL
sys.path.append('coil_python/')
import COIL, Barcode
# MCCOIL
sys.path.append('mccoil/')
import mccoil


## utilities
# fcn to include html files 
def include_html(fname):
	f = open(fname, 'r')
	for line in f.readlines(): 
		print(line.replace('\n',''))
	f.close()

def print_form(fieldstorage): 
	for k in fieldstorage.keys(): 
		print_html_line(k + ': ' + str(fieldstorage[k].value))
		
def print_html_line(line): 
	print('<p style="margin: 0px 40px">' + line + '</p>') 
	print('<br>')
        
def print_modules_info(): 
	for module_name in list(set(sys.modules) & set(globals())): 
		module = sys.modules[module_name]
		print_html_line(module_name + ': ' + str(getattr(module, '__version__', 'unknown')))

def print_for_debugging(debugging_input=[]): 
	print("Content-Type: text/html")
	print
	print
	#include_html('../htdocs/coil_header.html')
	print
	print_form(form)
	print
	for i in debugging_input: 
		print_html_line(i) 
	print_html_line('PYTHON_VERSION: ' + str(sys.version))
	print_html_line('PLATFORM: ' + str(sys.platform))
	print
	print_modules_info()
	print
	#include_html('../htdocs/broad_footer.html')

def format_predictions_file(predictions, format='csv'): 
	delimiter = '\t'
	if format == 'csv': delimiter = ','
	prediction_file = delimiter.join(['id','seq','coi','confidence_interval','posterior_prob']) + '\n' 
	for prediction in predictions: 
		prediction_file = prediction_file + (delimiter.join(map(lambda p: str(p).replace(', ','-'), prediction)) + '\n')
	return(prediction_file)

def format_cois_mafs_file(predictions, format='csv'): 
	delimiter = '\t'
	if format == 'csv': delimiter = ','
	prediction_file = delimiter.join(['id (sample/pos)','prediction (coi/maf)']) + '\n' 
	for predict_type in ['cois', 'mafs']: 
		for prediction in predictions[predict_type]: 
			prediction_file = prediction_file + (delimiter.join(map(str, prediction)) + '\n')
	return(prediction_file)

def serve_file_for_download(file_, name='result.csv'): 
	return ("<p>Content-type: application/octet-stream</p>" +\
	        ("<p>Content-Disposition: attachment; filename=%s</p>" % name) +\
		'<p>' + file_ + '</p>')

def get_field_to_col_index_map(csv_header): 
	field_to_col_index = {}
	fields = [f.strip() for f in csv_header.split(',') if f != '']
	for i in range(len(fields)): 
		field_to_col_index[fields[i]] = i
	return(field_to_col_index)

def freq_str_to_dict(s):
    freq_dict = {}
    r = dict([f.split(':') for f in s.split('/')])
    if not ';' in r.values()[0]:
        for k, v in r.items(): freq_dict[k] = float(v)
    else:
        to_float_tuple = lambda tuple_str: tuple(map(lambda s: float(s.replace('(','').replace(')','')), tuple_str.split(';')))
        for k, v in r.items(): freq_dict[k] = to_float_tuple(v)
    return(freq_dict)

def classify_freq_dict(freq_dict, include_nonref=False):
    classified = {}
    for k, v in freq_dict.items():
	    if v == max(freq_dict.values()): 
		    classified['major'] = k
	    elif v == min(freq_dict.values()): 
		    classified['minor'] = k
	    elif include_nonref: 
		    classified['nonref'] = k
    return(classified)    

def minor_allele_freq(allele_freqs, just_value=True):
    if just_value:
        return(min(allele_freqs.values()))
    else:
        maf_dict = {}
        for allele, freq in allele_freqs.items():
            if freq == min(allele_freqs.values()): maf_dict[allele] = freq
        return(maf_dict)

def get_filtered_maf_file_lines(group, select_file_contents): 
	# get maf_geo_select type: region or country 
	maf_geo_type = 'region'
	to_group_name = lambda x: x
	if not group in ['all','central_africa','southeast_asia','west_africa']: 
		maf_geo_type = 'country'
		to_group_name = lambda val: dict([["ghana","Ghana"],["bangladesh","Bangladesh"],
						  ["myanmar","Myanmar"],["guinea","Guinea"],["laos","Laos"],["senegal","Senegal"],
						  ["cambodia","Cambodia"],["congo","DR of the Congo"],["gambia","The Gambia"],
						  ["vietnam","Vietnam"],["mali","Mali"],["thailand","Thailand"],["nigeria","Nigeria"],
						  ["malawi","Malawi"]])[val]
	# prepare dataframes
        select_df = pd.read_csv(StringIO.StringIO(select_file_contents))
        select_df['chrom_pos'] = select_df.apply(lambda row: (row['chrom'] + '_' + str(row['pos'])), axis=1)
        pf3k_mafs_df = pd.read_csv('static/data/pf3k_'+ maf_geo_type +'_mafs_gene_snps.csv')
        pf3k_mafs_df['chrom_pos'] = pf3k_mafs_df.apply(lambda row: (row['chrom'] + '_' + str(row['pos'])), axis=1)
        # merge 
        pf3k_select_mafs = select_df.merge(pf3k_mafs_df, on='chrom_pos', how='left')
        # add columns
        for kind in ['major','minor']:
                pf3k_select_mafs[kind] = pf3k_select_mafs.allele_freqs.apply(lambda afs: classify_freq_dict(freq_str_to_dict(afs))[kind]
                                                                             if pd.notnull(afs) else afs)
        pf3k_select_mafs['barcode_pos'] = pf3k_select_mafs.index
        pf3k_select_mafs['all'] = pf3k_select_mafs.allele_freqs.apply(lambda afs: min(freq_str_to_dict(afs).values()) if pd.notnull(afs) else afs)
        # change group field to 'maf'
        pf3k_select_mafs = pf3k_select_mafs.rename(columns={to_group_name(group): 'maf'})
        # return lines of this df, not null
        maf_file_lines = [line for line in (pf3k_select_mafs[pd.notnull(pf3k_select_mafs.maf)][['barcode_pos','major','minor','maf']]
                                            .to_csv(sep='\t', index=False).split('\n')) if line != '']
        maf_file_lines = ['#' + maf_file_lines[0]] + maf_file_lines[1:] 
        return(maf_file_lines)
