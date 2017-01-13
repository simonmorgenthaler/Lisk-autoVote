#!/usr/bin/python

####################################################################################################################
# File name: autoVote.py                                                                                           #
# Author: cc001                                                                                                    #
# Last modified: 2016-12-10                                                                                        #
#                                                                                                                  #
# This is a script to vote automatically for Lisk delegates.                                                       #
# The accounts you want to vote for must be added to text files, defined in the file config.yml.                   #
# Put every delegatename, accountnumber, or publickey on its own line                                              #
#                                                                                                                  #
# Installation: make sure to have installed the modules time, httplib, socket, json, requests, os, yaml, getpass   #
# Example: For the in Ubuntu this is done with 'sudo apt-get install python-httplib2 python-requests python-yaml'  #
# You have to modify the file config.yaml to adapt it for your needs. See the instructions in config.yml           #
#                                                                                                                  #
# Usage: make sure this script is executable with 'chmod +x autoVote.py'                                           #
# Start the script with no parameters: './autoVote.py' to use the default config                                   #
# Or add the desired config section: './autoVote.py cc001'                                                         #
#                                                                                                                  #
# If you like and use this script, please vote for 'cc001' as Delegate on test- and mainnet, Thanks!               #
####################################################################################################################

import time
import httplib
import socket
import json, requests
import os
import sys
import yaml
import getpass

numberOfVotesPerTransaction = 33;

def getMyVotes():
    myVotes = []
    query = config['node'] + "/api/accounts/delegates/?address=" + config['myAddress']
    answer = getAnswer(query)
    if 'delegates' in answer:
        delegates = answer['delegates']
        for delegate in delegates:
            myVotes.append(delegate['publicKey'])
    return myVotes

def getVotingPublicKeysFromFile():    
    votingFileName = config['votingFilename']
    with open(votingFileName) as filename:
        votes = filename.read().splitlines()
    votes = filter(None, votes) # remove empty lines/entries
    votes = filter(lambda l: not l.startswith('#'), votes) #remove comments
    
    return getPublicKeys(votes)
    

def getPublicKeys(votes):
    publicKeys = []
    notFoundVotes = []
    if votes:
        template = "{0:22}|{1:22}|{2:<7}|{3:22}|{4:35}"
        print "\nFound:"
        print template.format("Vote", "Username", "Rank", "Adress", "PublicKey") # header
        print "-------------------------------------------------------------------------------------------------------------------------------------"
      
        for vote in votes:
            found = False
            for delegate in allDelegates:
                if delegate['username'] == vote or delegate['address'] == vote or delegate['publicKey'] == vote:
                    print template.format(vote, delegate['username'], delegate['rate'], delegate['address'], delegate['publicKey'])
                    publicKeys.append(delegate['publicKey'])
                    found = True
                    break
            if not found:
                notFoundVotes.append(vote)
        
        if notFoundVotes:    
            print "\nNot found:"
            print "----------"
            for notFound in notFoundVotes:
                print notFound
        print "\n"
        
    return publicKeys

def getDelegateName(publicKey):
    for delegate in allDelegates:
        if delegate['publicKey'] == publicKey:
            return delegate['username']

def generateVotingList():    
    currentVotesPublicKeys = getMyVotes()
    votingPublicKeysPos = getVotingPublicKeysFromFile()
    
    if len(currentVotesPublicKeys) > 0:
        print ""
        print "Voting already for these " + str(len(currentVotesPublicKeys)) + " delegates:"
        print "--------------------------------------"
        votedNames = []
        for entry in currentVotesPublicKeys:
            votedNames.append(getDelegateName(entry))
        print ", ".join(votedNames)
        
    finalVotesListPos = list(set(votingPublicKeysPos) - set(currentVotesPublicKeys))
    if len(finalVotesListPos) > 0:
        print "" 
        print "Adding the following votes:"
        print "---------------------------"
        for entry in finalVotesListPos:
            print getDelegateName(entry)
    
    finalVotesListNeg = list(set(currentVotesPublicKeys) - set(votingPublicKeysPos)) 
    if len(finalVotesListNeg) > 0:
        print ""
        print "Removing the following votes:"
        print "-----------------------------"
        for entry in finalVotesListNeg:
            print getDelegateName(entry)
    
    if len(finalVotesListPos) == 0 and len(finalVotesListNeg) == 0:
        print ""
        print "The votes are already correct, doing nothing"
    
    print "\n"
    return ['+' + votePos for votePos in finalVotesListPos] + ['-' + voteNeg for voteNeg in finalVotesListNeg]

def sendVotings(payload):
    url = config['node'] + "/api/accounts/delegates"
    try:
        response = requests.put(url=url, data=payload)
        answer = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        answer = []
    return answer

def getVotingPubKeys():
    publicKeys = []
    votesList = generateVotingList()
    
    print "Final list", votesList
    
    for votingname in votesList:
        prefix = votingname[0]
        name = votingname[1:]
        if prefix != '+' and prefix != '-':
            prefix = '+'
            name = votingname        
        publicKey = getPublicKey(name)
        if publicKey:
            publicKeys.append(str(prefix + publicKey))
        else:
            print "PublicKey for '" + name + "' not found"
    
    return publicKeys

def getAnswer(query):  
    answer = ""
    try:
        response = requests.get(url=query, timeout=3)
        answer = json.loads(response.text)
    except requests.exceptions.SSLError as e:
        print "SSLError", e.message
        print "Exiting..."
        exit(1)
    except requests.exceptions.RequestException as e:
        print "Error:", e.message
        print "Exiting..."
        exit(1)
    except ValueError, e:
        print "Not allowed"
        print "Exiting..."
        exit(1)
        
    return answer
    
def getAllDelegates():
    allDelegates = []
    limit = 100
    offset = 0
    totalCount = -1
    while totalCount == -1 or len(allDelegates) < totalCount:
        apiCall = "/api/delegates?limit=" + str(limit) + "&offset=" + str(offset) + "&orderBy=rate"
        query = config['node'] + apiCall
        answer = getAnswer(query)
        if 'delegates' in answer:
            allDelegates.extend(answer['delegates'])
            if totalCount == -1:
                totalCount = answer['totalCount']
            offset = offset + limit
        else:
            break
    return allDelegates
    
def help():
    print "You need to append the desired config section"
    print "Example:", sys.argv[0], "cc001"

def readConfig():
    global config
    with open("config.yml", 'r') as ymlfile:
        configuration = yaml.load(ymlfile)

    if len(sys.argv) == 1:
        configsection = "default"
        
    elif len(sys.argv) == 2:
        configsection = sys.argv[1]
    else:
        help
        exit(0)

    if not configsection in configuration:
        print "Unknown config section in config.yml:", configsection
        exit(0)

    config = configuration[configsection]

    if config['node'] == "REPLACE_ME" or config['mySecret'] == "REPLACE_ME" or ('mySecondSecret' in config and config['mySecondSecret'] == "REPLACE_ME") or config['myAddress'] == "REPLACE_ME" or config['myPublicKey'] == "REPLACE_ME" or config['votingFilename'] == "REPLACE_ME":
        print "Please read the instructions at the top of this file and adapt the configuration in config.yml accordingly"
        exit (0)

    config['node'] = config['node'].rstrip('/') # Remove trailing slashes

def testSecret():
    if not config['mySecret']:
        config['mySecret'] = getpass.getpass('Passphrase (needed for voting): ')

def testSecondSecret():
    if 'mySecondSecret' in config:
        if not config['mySecondSecret']:
            config['mySecondSecret'] = getpass.getpass('Second Passphrase (needed for voting): ')

def checkConfirmation():
    answer = raw_input("Execute the voting? [y/n]: ").lower()
    execute = False
    if answer == 'y' or answer == 'yes':
        execute = True
    return execute

        
readConfig()
allDelegates = getAllDelegates()
finalVotingList = generateVotingList()

if finalVotingList:
    if checkConfirmation():
      print
      delegatesLength = len(finalVotingList)

      start = 0;    
      if delegatesLength > numberOfVotesPerTransaction:
          print "Splitting " + str(len(finalVotingList)) + " votes into chunks of " + str(numberOfVotesPerTransaction)

      testSecret()
      testSecondSecret()
      
      while start < delegatesLength:
          shortDelegates = finalVotingList[start:start+numberOfVotesPerTransaction]

          payload = {
              "delegates[]": shortDelegates,
              "publicKey": config['myPublicKey'],
              "secret": config['mySecret']
          }
          if 'mySecondSecret' in config:
              payload['secondSecret'] = config['mySecondSecret']

          answer = sendVotings(payload)
          if answer and 'success' in answer and answer['success']:
              print "Voted successfully for " + str(len(shortDelegates)) + " delegates:"
              print "-------------------------------------------"
              for delegate in shortDelegates:
                  prefix = delegate[0]
                  publickey = delegate[1:]
                  print prefix + getDelegateName(publickey)
          else:
              print "Error:", answer['error']
          start = start + numberOfVotesPerTransaction
          print ""
    else:
        print ""
        print "Aborted. Doing nothing\n"
        
else:
    print "Doing nothing\n"

exit(0)
