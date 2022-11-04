import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


"""
Appdrive Domain: appdrive.info

Appdrive Look Alike Domain: "driveapp.in", "drivehub.in" , "gdflix.pro", "drivesharer.in", "drivebit.in", "drivelinks.in", "driveace.in", "drivepro.in", "gdflix.top"


Note:- Each Domain require login email and password. You have to login all website separately to bypass that website link
( Tip use same email to login all website and go to  dashboard and create same password of all domain )


Parameters: 
appdrive_email and appdrive_password params should be of website not GOOGLE ACCOUNT
drive_id = team drive ID (optional) (for MyDrive, keep this field empty)
folder_id =  drive folder ID (optional)


Note: Some appdrive links don't need authorization ( email, password) like :( ex:  https://appdrive.info/file/m6p1PbFF49aqb4MOHrz1 ) , whereas some need authorization ( ex: https://appdrive.info/file/78owWyzsKPRuU5QB2VyG)

Regex: 
https?://(appdrive|driveapp|drivehub|gdflix|drivesharer|drivebit|drivelinks|driveace|drivepro)\.(info|in|pro|top)\/file/\S+

Domains Examples:
https://appdrive.info/file/78owWyzsKPRuU5QB2VyG
https://gdflix.top/file/8orswDGb6i
https://gdflix.pro/file/24pEEKH1Vp


appdrive_bypass("https://appdrive.info/file/m6p1PbFF49aqb4MOHrz1", email="xyz@gmail.com", password="appdrive", drive_id="your_td_drive_id", folder_id="folder_id_of_that_td")


"""


def account_login(client, url, appdrive_email, appdrive_password):
    data = {
        'email': email,
        'password': password
    }
    client.post(f'https://{urlparse(url).netloc}/login', data=data)



def update_account(client, url, shared_drive_id, folder_id):
    data = {
        'root_drive': shared_drive_id,
        'folder': folder_id
    }
    client.post(f'https://{urlparse(url).netloc}/account', data=data)
    
    
def gen_payload(data, boundary=f'{"-"*6}_'):
    data_string = ''
    
    for item in data:
        data_string += f'{boundary}\r\n'
        data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
        
    data_string += f'{boundary}--\r\n'
    return data_string



def appdrive_lookalike(client, drive_link):
    try:
        response = client.get(drive_link).text
        soup = BeautifulSoup(response, "html.parser")
        return soup.find(class_="btn").get("href")
    except: return drive_link

			
def appdrive_bypass(url: str, appdrive_email=None, appdrive_password=None, drive_id=None,  folder_id=None) -> str:

    client = requests.Session()
    client.headers.update({
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    })
    update_account(client, url, drive_id, folder_id)
    
    url = client.get(url).url 
    response = client.get(url)   
    try:
    	key = re.findall('"key",\s+"(.*?)"', response.text)[0]
    	soup = BeautifulSoup(response.text,  "html.parser")
    	ddl_btn = soup.find(id="drc")	    	    	
    except:
    	return "Something went wrong. Could not generate GDrive URL for your Given Link"
    
    headers = { "Content-Type": f"multipart/form-data; boundary={'-'*4}_"} 
    data = { 'type': 1,  'key': key, 'action': 'original'}
    
    if ddl_btn != None:  data['action'] = 'direct'
    else : account_login(client, url, appdrive_email, appdrive_password)
    	 
  
        
    while data['type'] <= 3:
        try:  response = client.post(url, data=gen_payload(data), headers=headers).json() ;  break 
        except: data['type'] += 1   
 
        
    if 'url' in response:
    	drive_link = response["url"]
    	if urlparse(url).netloc in ("driveapp.in", "drivehub.in" , "gdflix.pro", "drivesharer.in", "drivebit.in", "drivelinks.in", "driveace.in", "drivepro.in", "gdflix.top"): return appdrive_lookalike(client,  drive_link)
    	else : return drive_link 
    		     	 	
    elif  'error' in response and response['error']: return response['message']
    else: return "Something went wrong. Could not generate GDrive URL for your Given Link"
    




