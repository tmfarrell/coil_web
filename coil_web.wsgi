#!/usr/bin/python                      
                                                                            
import sys
#import logging                                                                                                    
#logging.basicConfig(level=logging.DEBUG,                                                                          
#                    format='%(asctime)s %(levelname)s %(message)s',                                               
#                    filename='/var/www/coil_web/wsgi.log',                                                        
#                    filemode='w')                                                                                 
sys.path.insert(0, "/var/www/coil_web/")
from coil_web import app as application