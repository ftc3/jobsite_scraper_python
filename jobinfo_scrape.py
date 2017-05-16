import urllib2
import re
from bs4 import BeautifulSoup
import time
import ast
import json
import requests
import csv
# searched google for "data analyst intern"
# the first link is:
# https://www.indeed.com/q-Data-Analyst-Intern-jobs.html

# leave on for fresh data
initial = urllib2.urlopen('https://www.indeed.com/q-Data-Analyst-Intern-jobs.html').read()
#print initial
fout = open('indeedhtml.txt', 'w')
fout.write(str(initial))

initial = open('indeedhtml.txt','rU',)


# I want <span class="company">, these are sponsored listings blended in with the others. Are they on every page?
# I want job map listings most of all! This is the easy part

# for the sponsored listings
# https://www.indeed.com/cmp/ company /jobs/ job-name-fb142d6ced6df3e9  <-- this code is here data-jk="_____"
# parse 1) company name 2) job name 3) data-jk="_______"
# then build the url with urllib.openurl

# is "row result" unique -- the data-jk starts there
# one regex is ideal
initial = initial.read()
#print initial
sponsored = re.findall(r'<div\sclass="row.*?data-jk="(.*?)"', initial)
#print sponsored

# <div\sclass="row.*?data-jk="(.*?)">\n[.*\n]{3}.*"company">\n(.*)</span>


#bs = BeautifulSoup(initial, 'html.parser')
#print bs
#bs = bs.read()
#print type(bs)


# the range that I want range(10, 990, 10)

# returns list of curly bracketed jobmap observations on a page
jobmaps = re.findall('jobmap\[[0-9]\]=\s({.*})', initial)
#print jobmaps
#change list of strings to list of dictionaries
#print type(jobmaps)
pagedicts = list()
for item in jobmaps:
    item = item.replace('{', '{"')
    item = item.replace(':', '" : ')
    item = item.replace('\',', '\', \"')
    item = item.replace('\'', '"')
    #jk = item.get('jk')
    # ditem = ast.literal_eval(item)
    # print ditem
    ditem = json.loads(item)
    #print ditem
    pagedicts.append(ditem)
# finalpagedicts is the final list of dictionaries that need to be written
# do this for every position in the jobmap
finalpagedicts = list()
for pos in pagedicts:
    try:
        address = 'https://www.indeed.com/rc/clk?jk=' + pos['jk'] + '&fccid=' + pos['efccid']
        #print address
        #cookies preventing redirect from working, use requests
        r = requests.get(address)
        r = r.text
        #print type(r)
        #print r
        unpaidre = re.search("unpaid", r, re.IGNORECASE)
        if unpaidre != None:
            pos['unpaid']= 1
        else:
            pos['unpaid']= 0
        #print pos
        zipcodere = re.search(',\s[A-Z]{2}\s[0-9]{5}', r)
        if zipcodere !=None:
            pos['zip2'] = zipcodere.group()
        else:
            pos['zip2'] = None
        finalpagedicts.append(pos)
        print pos
        time.sleep(5)
    except:
        print "missed 1"
        continue

href = re.findall('<a\shref="(/jobs\?q=Data.*?)">', initial)
lasthref = href[-1]
pieceoflast = re.match('^(.*start=)[0-9]{2,}(&pp=.*)$', lasthref)
#print pieceoflast.group(1), pieceoflast.group(2)
first = pieceoflast.group(1)
last = pieceoflast.group(2)
time.sleep(1)
# do this for the first 100 pages. page 1 is done before this loop
for i in range(10, 30, 10):
    print i
    pagedicts = list()
    current = urllib2.urlopen('https://www.indeed.com' + first + str(i) + last).read()

    href = re.findall('<a\shref="(/jobs\?q=Data.*?)">', current)
    lasthref = href[-1]
    pieceoflast = re.match('^(.*start=)[0-9]{2,}(&pp=.*)$', lasthref)
    first = pieceoflast.group(1)
    last = pieceoflast.group(2)
    #print pieceoflast.group(1), i, pieceoflast.group(2)
    jobmaps = re.findall('jobmap\[[0-9]\]=\s({.*})', current)
    #print jobmaps
    time.sleep(4)
    pagedicts = list()
    for item in jobmaps:
        item = item.replace('{', '{"')
        item = item.replace(':', '" : ')
        item = item.replace('\',', '\', \"')
        item = item.replace('\'', '"')
        #trouble shooting one particular case
        item = item.replace('Summer Intern" :  Database Analyst', 'Summer Intern : Database Analyst')
        # ditem = ast.literal_eval(item)
        print "mapped", item
        ditem = json.loads(item)
        print "json success"
        pagedicts.append(ditem)
# we just created a dictionary of positions from the current page we want to go through
# this next loop goes through each position to get to the end of the list of all positions
# that are in our dictionary
    for pos in pagedicts:
        try:
            address = 'https://www.indeed.com/rc/clk?jk=' + pos['jk'] + '&fccid=' + pos['efccid']
            #print address
            # cookies preventing redirect from working, use requests
            r = requests.get(address)
            r = r.text
            #print type(r)
            # print r
            unpaidre = re.search("unpaid", r, re.IGNORECASE)
            if unpaidre != None:
                pos['unpaid'] = 1
            else:
                pos['unpaid'] = 0
            # print pos
            zipcodere = re.search(',\s[A-Z]{2}\s[0-9]{5}', r)
            if zipcodere != None:
                pos['zip2'] = zipcodere.group()
            else:
                pos['zip2'] = None
            finalpagedicts.append(pos)
            print pos
            time.sleep(5)
        except:
            print "missed 1.0"
            continue
print finalpagedicts

#csv file creation
tuplist = list()
for x in finalpagedicts:
    #j = json.loads(x)
    loc = x['loc']
    cmpesc = unicode(x['cmpesc']).encode('utf-8')
    zip = x['zip']
    city = x['city']
    rd = x['rd']
    country = x['country']
    title = x['title']
    srcid = x['srcid']
    srcname = x['srcname']
    unpaid = x['unpaid']
    num = x['num']
    cmpid = x['cmpid']
    jk = x['jk']
    zip2 = x['zip2']
    efccid = x['efccid']
    cmplnk = x['cmplnk']
    tup = (loc, cmpesc, zip, city, rd, country, title, srcid, srcname, unpaid, num, cmpid, jk, zip2, efccid, cmplnk)
    tuplist.append(tup)
print tuplist

with open('output_4_18.csv', 'w') as out:
    csv_out = csv.writer(out)
    csv_out.writerow(['Location', 'cmpesc', 'zip', 'city', 'rd', 'country', 'jobtitle', 'srcid', 'srcname', 'unpaid', 'num', 'companyid', 'jk', 'regex_zip', 'efccid', 'companylink'])
    for row in tuplist:
        csv_out.writerow(row)


