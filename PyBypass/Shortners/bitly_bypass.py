import requests 

"""
https?://(bit\.ly/)\S+
https://bit.ly/3gco4QU
"""

def bitly_bypass(bitly_url: str) -> str:
	return requests.get(bitly_url).url
	
	
