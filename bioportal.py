import platform
majorv = platform.python_version()
majorv = int ( majorv [ 0 ] )
if majorv > 2:
  from urllib.parse import quote
  from urllib.request import urlopen
else:
  from urllib2 import quote
  from urllib2 import urlopen

import json
import sys


BIOPORTAL_BASE_URL = "http://data.bioontology.org"

def url_param ( key, value ):
	return key + "=" + quote ( value )

def url_param_append ( key, value ):
	return "&" + url_param ( key, value )

def url_build ( baseurl, **params ):
	url = baseurl
	for key in params:
		url += url_param_append ( key, params [ key ] )
	return url

class BioPortalClient:
	def __init__ ( self, apikey ):
		self.apikey = apikey

	def _bp_baseurl ( self, api_path ):
		return BIOPORTAL_BASE_URL + api_path + "?" + url_param ( "apikey", self.apikey )

	def annotator ( self, text, **other_params ):
		other_params [ "text" ] = text
		url = self._bp_baseurl ( "/annotator" )
		url = url_build ( url, **other_params )
		print ( url )
		jterms = urlopen ( url ).read()
		jterms = json.loads( jterms )
		return jterms

	def annotator_terms ( self, text, **other_params ):
		jterms = self.annotator ( text, **other_params )
		terms = [ term [ "annotatedClass" ] [ "@id" ] for term in jterms ]
		return terms

if __name__ == '__main__DISABLED':
	# TODO: this is what their UI uses: 8b5b7825-538d-40e0-9e9e-5ab9274a9aeb
	if len ( sys.argv ) < 2:
		 raise TypeError ( "A Bioportal API key is needed to test this module (as command line argument)" )
	bp = BioPortalClient ( sys.argv [ 1 ] )
  #terms = bp.annotator_terms ( "Melanoma is a malignant tumor usually affecting the skin", ontologies = "MESH" )
	terms = bp.annotator_terms ( "Melanoma is a malignant tumor usually affecting the skin" )
	terms = terms [ 0: 9 ]
	print ( terms )