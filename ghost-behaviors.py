#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 10:40:19 2020

@author: dankerkove
"""

import requests
import json
import time

class Location:
    def __init__(self, locId, auth):
        self.locId = locId
        self.auth = auth
        self.bList = []
        self.rList = []
        self.gBList = []
        self.gRList = []
        self.locInit()
        
    def locInit(self):
        #dm url + params
        oldOffset = 0
        locParam = '?locationId=' + locId
        dmUrl = 'https://api.smartthings.com/behaviors'
        dmUrl = dmUrl+locParam
        
        #ocf url + params
        locParam = '?gid=' + locId
        ocfUrl = 'https://ruleproxy-na04-useast2.api.smartthings.com/rules'
        ocfUrl = ocfUrl+locParam
        
        dmRespBehaviors = httpReq(dmUrl)
        behaviorParse(dmRespBehaviors, oldOffset, self.bList)

        ocfRespRules = httpReq(ocfUrl)
        ocfParse(ocfRespRules, self.rList)
        
     
    def listBehaviors(self):
        print(len(self.bList))
        for b in self.bList:
           print(b.bName)
           
    
    def getGhosts(self, delBehaviors, delRules):
        self.findGhosts()
        countB = 0
        for gb in self.gBList:
            for b in self.bList:
                if b.bName == gb:
                    print("Found Ghost Behavior: ", b.bName, " - " , b.bId)
                    if delBehaviors == True:
                        print("Deleting ", b.bName, " - " , b.bId)
                        delBehaviorReq(self.locId, b.bId)
                    countB+=1
        print("total ghost behaviors = ", countB, "\n")
        countR = 0
        for gr in self.gRList:
            for r in self.rList:
                if r.rName == gr:
                    print("Found Ghost Rule: ", r.rName, " - ", r.rId)
                    if delRules == True:
                      print("Deleting ", r.rName, " - ", r.rId)
                      delRuleReq(self.locId, r.rId)
                    countR+=1
        print("total ghost rules = ", countR)

        


    def findGhosts(self):
        strBList = []
        strRList = []
        for b in self.bList:
            strBList.append(b.bName)
        for r in self.rList:
            strRList.append(r.rName)
        self.gBList = list(set(strBList) - set(strRList))
        self.gRList = list(set(strRList) - set(strBList))
        # print(self.gBList)
        # print(self.gRList)
        return self.gBList, self.gRList

    
        
    def listRules(self):
        for r in self.rList:
            print(r.rName)
    
    

    def forceDelete(self, name):
      delName = name
      for b in self.bList:
        if b.bName == delName:
          print("deleting: " + b.bName, b.bId)
          delReq(self.locId, b.bId)
    
    
class Behavior:
    def __init__(self, bName, bId, bStatus):
        self.bName = bName
        self.bId = bId
        self.bStatus = bStatus


class Rule:
    def __init__(self, rName, rId):
        self.rName = rName
        self.rId = rId
        
        
class Ghost:
    def __init__(self, gName):
        self.gName = gName        
        


def delBehaviorReq(locId, bId):
    url = 'https://api.smartthings.com/behaviors/' + bId + '?locationId=' + locId
    headers={'Content-Type':'application/json',
             'Authorization': 'Bearer {}'.format(auth)} 
    req = requests.delete(url = url,headers = headers)
    print(req.status_code)
    return

def delRuleReq(locId, bId):
    url = 'https://ruleproxy-na04-useast2.api.smartthings.com/rules/' + rId + '?gid=' + locId
    headers={'Content-Type':'application/json',
             'Authorization': 'Bearer {}'.format(auth)} 
    req = requests.delete(url = url,headers = headers)
    print(req.status_code)
    return


def httpReq(url):
    headers={'Content-Type':'application/json',
             'Authorization': 'Bearer {}'.format(auth)} 
    req = requests.get(url = url,headers = headers)
#    print(req.status_code)
    jsonResp = json.dumps(req.json(), indent = 4)
    jsonDict = json.loads(jsonResp)
#    print(jsonResp)
#    print(jsonDict)
    return jsonDict

  
def behaviorParse(jsonDict, oldOffset, bList):
    for elem in jsonDict['items']:
        try:
            bName = elem['name']
        except KeyError:
            bName = "UNKOWN"
        bId = elem['id']
        try:
            bStatus = elem['status']
        except KeyError:
            bStatus = "UNKOWN"
        newBehavior = Behavior(bName, bId, bStatus)
        bList.append(newBehavior)
    try:    
        nextPageLink = (jsonDict['_links']['next']['href'])
        offsetIndex = nextPageLink.find("&offset=")
        offsetStart = offsetIndex +len("&offset=")
        offset = int(nextPageLink[offsetStart:offsetStart +3])
        if offset > oldOffset:
            behaviorNextPage(nextPageLink, offset, bList)
    except KeyError:
        pass

def behaviorNextPage(url, offset, bList):
    headers={'Content-Type':'application/json',
         'Authorization': 'Bearer {}'.format(auth)} 
    req = requests.get(url = url,headers = headers)
    jsonResp = json.dumps(req.json(), indent = 4)
    jsonDict = json.loads(jsonResp)
#    print(jsonResp)
    behaviorParse(jsonDict, offset, bList)


def ocfParse(jsonDict, rList):
    for elem in jsonDict:
        rName = (elem['n'])
        rId = elem['id']
        newRule = Rule(rName, rId)
        rList.append(newRule)
    return 



#user location id and auth token
locId = ''
auth = ''

thisLocation = Location(locId, auth)

# thisLocation.listRules()
# thisLocation.listBehaviors()
thisLocation.getGhosts(delBehaviors=False, delRules=False)
# thisLocation.forceDelete(name="ButtonAutomation1554848473396")
