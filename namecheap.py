#!/usr/bin/env python3
import requests 
import xmltodict
import sys
import time
import os
import logging
import argparse
import yaml
import urllib.request
from dotenv import load_dotenv
load_dotenv()

sample_yaml_records = """
---
-
  HostName: '@'
  RecordType: 'A'
  Address: '10.1.1.1'
  MXPref: '10'
  TTL: '60'
-
  HostName: test1
  RecordType: 'A'
  Address: '10.1.1.1.2'
  MXPref: '10'
  TTL: '60'
-
  HostName: 'test2'
  RecordType: 'A'
  Address: '10.1.1.3'
  MXPref: '10'
  TTL: '60'
"""


class NameCheap(object):
  def __init__(self, apiUser,apiKey,subDomain,topDomain):
    self.url = ("https://api.namecheap.com/xml.response")
    self.header = {
        "Content-Type": "application/x-www-form-urlencoded"
        } 
    self.data_template = {
        "ApiUser"  : apiUser,
        "UserName" : apiUser,
        "ApiKey"   : apiKey,
        "Command"  : "",
        "ClientIp" : "127.0.0.1",
        "SLD"      : subDomain,
        "TLD"      : topDomain
    }


  def get_records(self, verbose=False):
    records = []
    data = self.data_template.copy()
    data["Command"] = "namecheap.domains.dns.getHosts"

    response = requests.post(self.url, headers=self.header, data = data) 
    nc = xmltodict.parse(response.content)
    if nc["ApiResponse"]["Errors"]:
        sys.exit('Post to namecheap failed!')
    else:
        cmdResponse = nc["ApiResponse"]["CommandResponse"]["DomainDNSGetHostsResult"]
        domain      = cmdResponse["@Domain"]
        emailType   = cmdResponse["@EmailType"]
        hosts       = cmdResponse["host"]
        for host in hosts:
            record = {
                "HostName"   : host["@Name"],
                "RecordType" : host["@Type"],
                "Address"    : host["@Address"],
                "MXPref"     : host["@MXPref"],
                "TTL"        : host["@TTL"]
            }
            if verbose: print(record)
            records.append(record)
    return records


  def check_records(self,records):
    nc_records = self.get_records()
    for record in records:
      match = next(  (nc_record for nc_record in nc_records if nc_record["HostName"] == record["HostName"])  , None)
      if not match:
        return False
    for nc_record in nc_records:
      match = next(  (record for record in records if nc_record["HostName"] == record["HostName"])  , None)
      if not match:
        return False
    return True


  def add_record(self,record):
    records = self.get_records()
    url = ("https://api.namecheap.com/xml.response")
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
        } 

    records.append(record)

    newdata = self.data_template.copy()
    newdata["Command"] = "namecheap.domains.dns.setHosts"

    for i in range(len(records)):
        newdata["HostName"+str(i+1)]   = records[i]["HostName"]
        newdata["RecordType"+str(i+1)] = records[i]["RecordType"]
        newdata["Address"+str(i+1)]    = records[i]["Address"]
        newdata["MXPref"+str(i+1)]     = int(records[i]["MXPref"])
        newdata["TTL"+str(i+1)]        = records[i]["TTL"]

    

    response = requests.post(url, headers=header, data = newdata)
    return response


  def add_record_certbot(self, domain, validation):
    host_length = len(domain) - len( "." + self.data_template["SLD"] + "." + self.data_template["TLD"] )  
    hostname = domain[:host_length] 
    if host_length < 2:
      hostname = "_acme-challenge"
    else:
      hostname = "_acme-challenge." + hostname if hostname != "*" else "_acme-challenge"
    print(f"Adding Certbot verification: {hostname} - {validation} ")

    record = {
      "HostName": hostname,
      "RecordType": "TXT",
      "Address": validation,
      "MXPref": "10",
      "TTL":  "60"
    }
    self.add_record(record)


  def delete_record_certbot(self, domain, validation):
    host_length = len(domain) - len( "." + self.data_template["SLD"] + "." + self.data_template["TLD"] )
    hostname = domain[:host_length] 
    if host_length < 2:
      hostname = "_acme-challenge"
    else:
      hostname = "_acme-challenge." + hostname if hostname != "*" else "_acme-challenge"
    print(f"Deleting Certbot verification: {hostname} - {validation} ")


    record ={
      "HostName": hostname,
      "RecordType": "TXT",
      "Address": validation,
      "MXPref": "10",
      "TTL":  "60"
    }
    self.delete_record(record)


  def delete_record(self,record):
    records = self.get_records()

    newdata = self.data_template.copy()
    newdata["Command"] = "namecheap.domains.dns.setHosts"

    for i in range(len(records)):

        match = records[i]["HostName"] == record["HostName"] and records[i]["RecordType"] == record["RecordType"] 
        if match:
          pass
        else:
          newdata["HostName"+str(i+1)]   = records[i]["HostName"]
          newdata["RecordType"+str(i+1)] = records[i]["RecordType"]
          newdata["Address"+str(i+1)]    = records[i]["Address"]
          newdata["MXPref"+str(i+1)]     = int(records[i]["MXPref"])
          newdata["TTL"+str(i+1)]        = records[i]["TTL"]
    
    response = requests.post(self.url, headers=self.header, data = newdata) 
    return response


  def overwrite(self,records):

    newdata = self.data_template.copy()
    newdata["Command"] = "namecheap.domains.dns.setHosts"

    for i in range(len(records)):

        newdata["HostName"+str(i+1)]   = records[i]["HostName"]
        newdata["RecordType"+str(i+1)] = records[i]["RecordType"]
        newdata["Address"+str(i+1)]    = records[i]["Address"]
        newdata["MXPref"+str(i+1)]     = int(records[i]["MXPref"])
        newdata["TTL"+str(i+1)]        = records[i]["TTL"]
    
    response = requests.post(self.url, headers=self.header, data = newdata) 
    return response


if __name__ == "__main__":
  
  # logging.basicConfig(level=logging.WARN, format='%(asctime)s UTC %(levelname)s %(module)s(%(funcName)s) [%(process)d-%(thread)d-%(threadName)s]: %(message)s')
  logging.basicConfig(level=logging.INFO, format='%(asctime)s UTC %(levelname)s %(module)s %(message)s')
  parser = argparse.ArgumentParser(description='Optional app description')
  parser.add_argument('--add',      action='store_true', help='Add TXT auth record from certbot to Namecheap DNS records')
  parser.add_argument('--delete',   action='store_true', help='Delete TXT auth record from certbot to Namecheap DNS records')
  parser.add_argument('--upload',     action='store'     , help='Upload records YAML file to Namecheap')

  args = parser.parse_args()

  apiUser     = os.getenv('NAMECHEAP_USER', None)
  apiKey      = os.getenv('NAMECHEAP_APIKEY', None)
  subDomain   = os.getenv('NAMECHEAP_SUBDOMAIN', None)
  topDomain   = os.getenv('NAMECHEAP_TOPDOMAIN', None)
  cert_domain = os.getenv('CERTBOT_DOMAIN', None )
  cert_valid  = os.getenv('CERTBOT_VALIDATION', None)
  file        = os.path.join( os.getcwd() , "records/records.yaml" )

  if ( apiUser and apiKey and subDomain and topDomain ):
    if (args.add or args.delete) and not ( cert_valid and cert_domain ) :
      logging.error(f"One or more certbot environment variables are missing:")
      logging.error(f"CERTBOT_DOMAIN: {cert_domain}")
      logging.error(f"CERTBOT_VALIDATION: {cert_valid}")  
      sys.exit(1)    
  else:
    logging.error(f"One or more namecheap environment variables are missing:")
    logging.error(f"NAMECHEAP_USER: {apiUser}")
    logging.error(f"NAMECHEAP_APIKEY: {apiKey}")
    logging.error(f"NAMECHEAP_SUBDOMAIN: {subDomain}")
    logging.error(f"NAMECHEAP_TOPDOMAIN: {topDomain}")
    sys.exit(1)


  nc = NameCheap( subDomain=subDomain, topDomain=topDomain, apiUser=apiUser, apiKey=apiKey)

  if args.add :
    print("ACME CHALLANGE",cert_domain,cert_valid)
    nc.add_record_certbot(cert_domain,cert_valid)
    time.sleep(60)

  elif args.delete:
    nc.delete_record_certbot(cert_domain,cert_valid)

  elif args.upload:
    file = args.upload
    logging.info(f"Overwriting records from {file}:")
    records = []
    if os.path.exists(file):
      with open(file, "r") as stream:
          try:
              records = yaml.safe_load(stream)
          except yaml.YAMLError as exc:
              print(exc)
              sys.exit("Error reading yaml records file!")
    else:
      logging.error(f"Yaml records file '{file}' does not exists!")
      sys.exit(1)
    try:
      ip = urllib.request.urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip()
    except:
      logging.error(f"unable to determine own IP from checkip.amazonaws.com!")
      sys.exit(1)  
    if records and len(records):
      for record in records:
        if not "Address" in record:
          record["Address"] = ip
      nc.overwrite(records)
      nc.get_records(True)
    else:
      logging.error(f"No records in yaml file '{file}'!")
      sys.exit(1)      
  else:
    records = nc.get_records()
    yaml_string = "---\n" + yaml.dump( records, default_flow_style=False )
    print ( yaml_string )
