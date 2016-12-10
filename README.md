# Lisk-autoVote
Script to vote automatically from text files with delegate names, addresses and/or public keys.

## Installation
Make sure to have installed the imported python modules time, httplib, socket, json, requests, os, yaml.
For example in Ubuntu this is done with 'sudo apt-get install python-httplib2 python-requests python-yaml'. If you start the script with missing modules it will tell you which modules you have to install.
Read also the header in autoVote.py, but you don't have to modify autoVote.py. All you have to adapt is config.yml.

## Configuration
You have to modify the file config.yml to adapt it for your needs. See the instructions in config.yml. The script won't run if you don't adapt the mentioned constants.
Add the delegates you want to vote for to the file you configured in config.yml (Default is votes.txt). You can entere the delegate name, its address or its publickey. Put every delegate on a new line (see votes.txt as example)
You can add multiple configuration secions, to vote from different accounts, with different delegate files.

## Usage
Make sure this script is executable with 'chmod +x autoVote.py'
If you start the script with no parameters: './autoVote.py' it uses the default config section in config.yml.
If you want to run a different config secion, you can add it as an argument.
Example: './autoVote.py cc001'

If you like this script, please vote for my delegate 'cc001' on test- and mainnet, Thanks!
