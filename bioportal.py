"""
  Hacky implementation of clients to invoke Bioportal APIs.
"""
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

is_debug = False

"""
  Builds a URL parameter, including the URL-encoding of its value.
"""
def url_param ( key, value ):
	return key + "=" + quote ( value )

"""
  The same as url_param, but prepend a '&' separator.
"""
def url_param_append ( key, value ):
	return "&" + url_param ( key, value )

"""
  Builds a URL from a dictionary of parameters.
"""
def url_build ( baseurl, **params ):
	url = baseurl
	for key in params:
		url += url_param_append ( key, params [ key ] )
	return url

"""
	Simple helper to get the URL content
"""
def url_get_json ( url ):
	if is_debug: print ( "url_get_json: " + url )
	jdoc = urlopen ( url ).read()
	jdoc = json.loads( jdoc )
	return jdoc


"""
	The BioPortal client.

	Instances must be inititalised with an API key, which is then reused as necessary.
"""
class BioPortalClient:
	def __init__ ( self, apikey ):
		self.apikey = apikey

	# The API base URL, including the apikey
	def _bp_baseurl ( self, api_path ):
		return BIOPORTAL_BASE_URL + api_path + "?" + url_param ( "apikey", self.apikey )

	"""
		The text annotation service.

		This returns the plain json
	"""
	def annotator ( self, text, **other_params ):
		other_params [ "text" ] = text
		url = self._bp_baseurl ( "/annotator" )
		url = url_build ( url, **other_params )
		jterms = url_get_json ( url )
		return jterms

	"""
		The text annotation service.

		Returns the a list term descriptors, which are also cutoff based on the corresponding parameter.
		The annotar should return terms in order of significance, so the cutoff should retain the most relevant ones.

		if get_uris is set, returns only the term URIs (instead of complete dictionaries with label, synonym, definition).
	"""
	def annotator_terms ( self, text, cutoff = None, only_uris = False, **other_params ):
		jterms = self.annotator ( text, **other_params )
		# Strangely, there are dupes, let's filter
		visited = set (); new_terms = []
		for term in jterms:
			uri = term [ "annotatedClass" ] [ "@id" ]
			if uri in visited: continue
			new_term = { "uri": term [ "annotatedClass" ] [ "@id" ] }
			new_term [ "self" ] = term [ "annotatedClass" ] [ "links" ] [ "self" ]
			new_terms.append ( new_term )
			visited.add ( uri )
		if cutoff and len ( new_terms ) > cutoff:
			new_terms = new_terms [ 0: cutoff ]
		if only_uris:
			new_terms = [ term [ "uri" ] for term in new_terms ]
			return new_terms
		# Else, let's resolve only those that were retained
		for new_term in new_terms:
			durl = new_term [ "self" ]
			durl += "?" + url_param ( "apikey", self.apikey )
			dj = url_get_json ( durl )
			new_term [ "label" ] = dj [ "prefLabel" ]
			new_term [ "synonyms" ] = dj [ "synonym" ]
			defv = dj [ "definition" ]
			defv = defv [ 0 ] if len ( defv ) > 0 else "" # TODO: why is it string?
			new_term [ "definition" ] = defv
		return new_terms
		

def test ():
	if __name__ != '__main__': return
	# TODO: this is what their UI uses: 8b5b7825-538d-40e0-9e9e-5ab9274a9aeb
	if len ( sys.argv ) < 2: return
	apikey = sys.argv [ 1 ]
	# This is Jupyter
	if apikey == "-f":
		if len ( sys.argv ) < 3: return
		else: apikey = sys.argv [ 2 ]
	
	global is_debug; is_debug = True
	bp = BioPortalClient ( apikey )
	#terms = bp.annotator_terms ( "Melanoma is a malignant tumor usually affecting the skin", cutoff = 3, ontologies = "MESH,SNOMED,ICD10" )
	terms = bp.annotator_terms ( "Melanoma is a malignant tumor usually affecting the skin", 5 )
	terms = terms [ 0: 9 ]
	print ( terms )

test()