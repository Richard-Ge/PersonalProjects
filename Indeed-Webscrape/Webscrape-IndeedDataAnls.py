########## Start using python3 <filename> instead of python <filename>!

	###### TODO: use Django to put this on my website!
		## have one window for console outputs (e.g. progress, 3/15 scraped), 
		## one for summary output, one for job words
		## have inputs for user, way to quit/stop running (on exit?)

		## Find a way to verify results? print page text to 
		## different document, compare the two? 

		## TEST: max character limit for indeed jobs?
		## Periodically check, & save new jobs so they won't disappear!
		## Otherwise, there will be anti-recency bias, and more urgently
		## filled jobs will not show up. Job keys are perfect for a 
		## SQL database, as well as employer lists/foreign keys!
		  ## will jobs that have a key be updated, while keeping the key?
		   ## I can test this myself by creating my own listing
		   ## good opportunity to do ALTER table WHERE jk="abc123"
		   ## >>also test the character limit for job listings!
		  ## Try using an API (RESTful?) to connect Python and HTML
		  ## maybe use that sharable code website from /g/ to host Python?
		## calculate upload date & time from the age!

import time
import random
startTime = time.time()

def parseNum(inputStr):
		# !!!TODO: Create fcn. to strip ","'s from # of ratings^^^!!!
	if("," in inputStr): 
		# if there are commas, split them out and recombine
		splitString = inputStr.split(",")
		resultStr = "".join(splitString)
	else:
		# if there aren't any, just return it
		resultStr = inputStr
	return resultStr

def pixelWidth(inputStr):
		# TODO: create fcn. to find specific pixel width 
			# (measures from ": " to "px", and take whatever is in between)
	resultStr = ""
	for char in inputStr:
		if (char>='0' and char<='9') or char=='.':
			resultStr = resultStr + str(char)
		elif char=="p":
			break
	return resultStr


print("TOP of output ===========")   # why does it need parentheses now?
import requests
import bs4
import re

queries = ["data analyst intern", "data analyst"]  # update flags, certain TSVs; based on query (" intern", first two = datasci, second two = analysts...)
for query in queries:
	querySplit = query.split(" ")
	plusQuery = "+".join(querySplit)
	pages = 6
	recent_bool = True 			# TODO: read input
	if recent_bool==True:
		sort_method = "&sort=date"  # recency
	else: 
		sort_method = ""  # relevance (default)

	# scrape (n?) pages of search results for listing ID's
	## but only append if its a new key
	results = []
	for searchIndex in range(0, pages*10, 10):
		oneURL = "https://www.indeed.com/jobs?q="+plusQuery+"&l=United+States"+sort_method+"&start="+str(searchIndex)
		results.append(requests.get(oneURL))
		print("===One search")
	# the search results are contained in a "td" with ID = "resultsCol"
	print("Time after requests: "+str(time.time()-startTime))  # DEBUG

	justjobs = []
	temp = None
	soup_jobs = None  # to find ages of external listings
	for eachResult in results:
		print("===One result")
		soup_jobs = bs4.BeautifulSoup(eachResult.text, "lxml")  # this is for IDs
		# print(soup_jobs)  # way too much output!!!
		justjobs.extend(soup_jobs.find_all(attrs={"data-jk":True}))  # re.compile("data-jk")
	
	# Now, each div element has a data-jk. Get data-jk from each one!
	## MOVED: Make sure not to get old job keys: 
	with open("IndeedAnalysts.tsv", "r") as file:
		text = file.readlines()
		print()  #DEBUG
	currJKs = []
	for eachLine in text[1:]:
		currJKs.append(eachLine[:16])
	currJKstr = str(currJKs)
	print(str(len(text))+" JKs currently stored: ..."+currJKstr[len(currJKstr)-119:]) #DEBUG, 80 width - 26 chars

	jobIDs = []
	# Manual (string.find()) method (WORKING)
	for eachJob in justjobs: 
		startindex = str(eachJob).find("data-jk")
		temp0 = str(eachJob)[startindex+9:startindex+25]
		if (temp0 not in currJKs):
			jobIDs.append(temp0)

	IDs = " "
	for jobx in jobIDs:
		IDs = IDs + jobx + ", "
	print("\n"+str(len(jobIDs))+" *NEW* JobIDs for "+query+" found:"+IDs[:-2])

	# 2: put IDs into URLs, & scrape all of them for keywords
	jobListings = []
	jobDescs = []
	# DEBUG
	# jobPage = requests.get("https://www.indeed.com/viewjob?jk="+jobIDs[0])
	# print(str(bs4.BeautifulSoup(jobPage.text, "lxml")))
	count = 1
	for IDstr in jobIDs:  
		# for each job ()
		jobTemp = []
		jobTemp.append(str(IDstr)) ## 0
		print("This ID: "+str(IDstr)+", pause 1sec"); time.sleep(1)
		jobPage = requests.get("https://www.indeed.com/viewjob?jk="+IDstr)
		pageSoup = bs4.BeautifulSoup(jobPage.text, "lxml")

		# GET TITLE
			# Job title, full tag: <h1 class="icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title">Looker Data Analyst (Fully Remote)</h1>
			# now we clean it so only the job title is in position 0
			# the first index is fixed at 76, second one varies based on where "<" starts
			# so we substring for [1:], and .find("<")
		clutteredTitle = str(pageSoup.select('.icl-u-xs-mb--xs'))
		# print("String: "+"".join(jobTemp))  # DEBUG
		# print(clutteredTitle)  # DEBUG
		titleEnd = clutteredTitle[76:].find("<")
		#print(clutteredTitle[76:76+titleEnd])  # DEBUG
		
		####### TODO: redo these (no more hyphen in the page?)
		# GET A COMPANY'S NAME, RATING, NUM. OF REVIEWS, LOCATION
			# ^^ this one might not come out so easily, 4 more tags in between
			# Company line: div tag w/class=" jobsearch-CompanyInfoWithoutHeaderImage
			# ==== Sometimes it's a link, sometimes there are reviews, etc.
			# There are too many tags to search through. Instead, search
			# for instances of ">text<", and ignore instances of "><".
			# Save the substrings of ">text<", but ignore substrings 
			# containing the word "review".
			# We can also split based on "><", and search for "<" & ">" appearing
			# in one single block (the blocks on the ends won't have both)
		# GET COMPANY NAME, LOCATION
		fullCompany = ""
		fullLocation = ""
		fullDetails = ""
		halfwayBoolean = False
		clutteredCompany = str(pageSoup.select(".jobsearch-CompanyInfoWithoutHeaderImage"))
			# Split based on "><", and then find ">"
		clutteredCompanyTags = clutteredCompany.split("><")  # list of HTML blocks; one has 2 blocks
		locationIndex = -1
		for block in clutteredCompanyTags:
			if("<" in block and ">" in block):  # if ">text<" has been found. accounts for ending
					# if the text between "><" is "-" (filtering for "-" to get location after!)
				index1 = block.find(">")
				index2 = block.find("<")
				halfwayBoolean = True if block[index1+1] == "-" else halfwayBoolean  # otherwise, no change
				if(halfwayBoolean == True):
					fullLocation = fullLocation + (block[index1+1:index2]) + " "
				else: 
					fullCompany = fullCompany + (block[index1+1:index2]) + " "
		# GET # OF RATINGS, AND ACTUAL RATING (if applicable)	
			# split fullCompany, see if size >2. if true, test isnum() 
			# on penultimate element. if true, parse it as an int and 
			# append to jobTemp
		fullCompany = fullCompany[:-1]
		companyLineSplit = fullCompany.split(" ")
		# print("Review line word count: "+str(len(companyLineSplit)))  # DEBUG
		companyReviews = "No Reviews"
		companyRating = "No Rating"
		hasReviews = False
		if("review" in fullCompany):
			hasReviews = True
			# Get the number of reviews (penultimate word in company name)
			numReviewsTemp = companyLineSplit[-2]
			# print("Reviews before cleaning: "+companyLineSplit[-2])  # DEBUG
			companyReviews = str(parseNum(numReviewsTemp))
			# print("Reviews after cleaning: "+numReviewsTemp)  # DEBUG

			# Now we can get rid of the "n reviews" part
			lineArray = fullCompany.split(" ")  # split it into indiv. words
			lineArray = lineArray[:-2]  # subarray of everything except last 2 ("n reviews")
			fullCompany = " ".join(lineArray)
			
			# Get the company's rating
			starsFilledIndex = clutteredCompany.find("width:")
				# this may break if a job has another image in the CompanyInfoWithoutHeaderImage tag
			starsTemp = float(pixelWidth(clutteredCompany[starsFilledIndex+6:]))
			# print("Stars' size: "+starsTemp)  # DEBUG
			companyRating = starsTemp/60  # divide starsFilled pixels by 60 (full width) to get companyRating
		
		## ALTERNATIVE METHOD: COMPANY DETAILS
		jobHeaderSel = pageSoup.select(".jobsearch-JobInfoHeader-subtitle")
		if str(jobHeaderSel) == "[]":
			print("Special case: webpage is different")
			with open("IndeedAnalysts.tsv", "a") as file:
				file.write(IDstr+"\t\t\t"+time.asctime(time.gmtime())+"\t"+query+"\t\n")
			count += 1
			continue
		jobHeaderText = ">"+str(jobHeaderSel[0])+"<"
		jobHeaderSplit = jobHeaderText.split("><")
		# print("========\nJob Header Split: "+str(jobHeaderSplit)+"\n========")
		jobDetails = ""
		for aTag in jobHeaderSplit:
			if(">" in aTag):
				infoStart = aTag.find(">") + 1
				infoEnd = aTag.find("<")
				jobDetails += "|"+aTag[infoStart:infoEnd]
		print(str(count)+"/"+str(len(jobIDs))+" Job Details: "+jobDetails+"\n========")
		# Finding company rating is still working, so we don't redo that

		# GET AGE OF POSTING
			# also add separate "weight" to more recent jobs?
		# look for "jobsearch-JobMetadataFooter"
			# then look for "days ago", "hours ago", or "just now"
		jobAge = None
		jobFooter = str(pageSoup.select(".jobsearch-JobMetadataFooter"))  # print(jobFooter)  # DEBUG
		agoIndex = jobFooter.find(" ago")  
		justIndex = jobFooter.find("Just posted")
		todayIndex = jobFooter.find("Today")  
		# print("Age index: "+str(agoIndex))  # DEBUG
		# print("Just posted index: "+str(justIndex))  # DEBUG
		# print("Today index: "+str(todayIndex))  # DEBUG
		if(agoIndex != -1 and justIndex==-1 and todayIndex==-1):
			ageTemp = jobFooter[agoIndex-9:agoIndex]
			# print("Age temp: "+ageTemp)  # DEBUG
			dayStart = ageTemp.find(">")
			jobAge = ageTemp[dayStart+1:]
			# print("Job age: "+jobAge)  # DEBUG
		elif(justIndex != -1 and agoIndex==-1 and todayIndex==-1):
			jobAge = "Just posted"
		elif(todayIndex != -1 and justIndex==-1 and agoIndex==-1):
			jobAge = "Today"
		if(agoIndex==-1 and justIndex==-1 and todayIndex==-1):  # If there's no index (external listing, no page!)
			print("External Listing: "+IDstr)  # DEBUG
			jobAge = "External: WIP!"  # DEBUG
				# we will need to search the orig. results for this IDstr, 
				# and get the associated posting date
				###### UNNEEDED! Indeed does its own webscrape of company sites, 
				###### external listings will show with "original job" link!
		if(jobAge != None and agoIndex==-1 and justIndex==-1 and todayIndex==-1):  
			# if it isn't "Just Posted" or external listing
			print("Something happened... "+IDstr)  # DEBUG


		# GET JOB SALARY (TODO)  # often contained in the text itself, hard to extract
		#DEBUG jobTemp.extend(pageSoup.select("""Salary? """))
			# ^^ could be worth trying? only 1 tag in between, and I can search for "$"
		#DEBUG jobTemp.extend(pageSoup.select("""Page text: div tag w/id="jobDescriptionText"""))
			# ^^ text contained in multiple div/ul tags inside of this

		# GET JOB TEXT (for qualifications)
		# Job Description: <STARTS WITH VERB!!!> Duties, Responsibilities, Tasks, Functions, "work with", " to ",
		# Qualifications: Minimum, Skill, Competencies, "required", "preferred", "degree", "ability"
		page_string = pageSoup.get_text("\n")
		page_elements = (page_string.split("\n"))
		 
		#### TEMP: just put the whole page text in

		jobTextTemp = IDstr+" at "+jobDetails+". Desc.: "+"`".join(page_elements)+"\n"  # orig. fullCompany
		jobDescs.append(jobTextTemp)
		
		jobTemp.append(clutteredTitle[77:76+titleEnd])  ## 1  #77 takes out the ">"

		jobTemp.append(jobAge)  ## 2
		jobTemp.append(time.asctime(time.gmtime()))  ## 3

		# jobTemp.append(fullSalary)
		
		# jobTemp.append(fullCompany)  ## Temp. disabled

		# jobTemp.append(fullLocation[2:-1])  ## Temp. disabled
		jobTemp.append(jobDetails)  ## 4

		jobTemp.append(companyReviews)  ## 5

		jobTemp.append(str(companyRating) if str(companyRating)[:2] == "No"  ## 6
				else (str(companyRating*100)[:2]+"%"))
			# also add separate "weight" to higher/more rated companies?
		# print("===================")
		# print(jobTemp)  # DEBUG
		jobListings.append(jobTemp)  ## 7
		count = count + 1
	print("------------------------------")
	print("Job listings for: "+query)
	print("JobIndex, JobKey, JobTitle, TimePosted, TimeScraped, Company, Location, Reviews, Rating")
	for prIndex in range(0, len(jobListings)):
		print(str(prIndex+1)+"	"+"	".join(jobListings[prIndex]))
		# print(str(listing[:-1]))  # everything but qualifs  # temp. disabled
		# for item in listing[-1]:  # temporarily disabled
			# print(str(item))  # print qualifications on separate lines
	print("------------------------------")
	# print("Job Listings: "+str(jobListings))  # DEBUG
	# print("Type: "+str(type(jobListings[0])))  # DEBUG: type = list (each job listing)
	# print("Type: "+str(type(jobListings[0][0])))  # DEBUG: type = string (each job listing's job title)

	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	# print("===========ALL JOB DESCRIPTIONS: \n"+str(jobDescs))

	# Update .csv file with the new listings!                  https://stackoverflow.com/questions/4706499/how-do-you-append-to-a-file
	## READ stored listings, to look for overlap
		### moved to top, to save bandwidth
	## Now APPEND listings that aren't already there
	with open("IndeedAnalysts.tsv", "a") as file:
		for tempI in range(len(jobListings)):
			if(jobListings[tempI][0] not in currJKs):
				# print("adding JK: "+jobListings[tempI][0])
				tempDesc = jobDescs[tempI]
				tempDescSplit = tempDesc.split("\n")
				tempDescFormatted = "`".join(tempDescSplit)
				file.write(jobListings[tempI][0]+"\t"+jobListings[tempI][1]+"\t"+jobListings[tempI][2]+"\t"+jobListings[tempI][3]+"\t"+jobListings[tempI][4]+"\t"+query+"\t"+tempDescFormatted+"\n")
	print("Waiting 3 secs..."); time.sleep(3)

"""
We still need: whether/when it's removed. 
	- try scraping old jobs, or doing internet protocol stuff to see when it was modified?
"""








endTime = time.time()
totalRuntime = endTime - startTime
print("BOTTOM of output ========")
print("Time needed: "+str(totalRuntime)[:6]+" secs")
print("Waiting 80-140 secs..."); time.sleep(random.randint(80,140))
