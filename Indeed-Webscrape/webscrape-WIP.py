import time
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


print("TOP of output ===========")
import requests
import bs4
import re

query = "data analyst intern"  # TODO: read input
querySplit = query.split(" ")
plusQuery = "+".join(querySplit)
pages = 1					# TODO: read input
recent_bool = True 			# TODO: read input
if recent_bool==True:
	sort_method = "&sort=date"  # recency
else: 
	sort_method = ""  # relevance (default)

# scrape (5?) pages of search results for listing ID's
	# remove non-relevant positions (only needed if sorted by date?)
	# // "mosaic-zone-afterTenthJobResult" has no ID so it should be fine
results = []
# Create a loop to do a bunch of these at once! range(0, 80, 10)?
for searchIndex in range(0, pages*10, 10):
	oneURL = "https://www.indeed.com/jobs?q="+plusQuery+"&l=United+States"+sort_method+"&start="+str(searchIndex)
	results.append(requests.get(oneURL))
# the search results are contained in a "td" with ID = "resultsCol"
print("Time after requests: "+str(time.time()-startTime))  # DEBUG

justjobs = []
temp = None
soup_jobs = None  # to find ages of external listings
for eachResult in results:
	soup_jobs = bs4.BeautifulSoup(eachResult.text, "lxml")  # this is for IDs
	# print(soup_jobs)  # way too much output!!!
	justjobs.extend(soup_jobs.find_all(attrs={"data-jk":True}))  # re.compile("data-jk")
# each "card" is a div object
	# each has the class "jobsearch-SerpJobCard unifiedRow row result clickcard"
	# as well as an "ID" (unused?) and a second ID tag "data-jk"
	# "data-jk" seems to be the actual IDs used in each listing's URL
		# 2.5: also store job name and age of posting
# print(len(justjobs))  # 75, so 15 from each page!
# print(justjobs[0])  #M: was it always working? did changing to extend() fix it?

# Now, each div element has a data-jk. Get data-jk from each one!
jobIDs = []
"""
# More BeautifulSoup method (NOT WORKING)
print(type(justjobs[0]))
# print(justjobs[0])
for eachJob in justjobs:
	# print(eachJob.find("data-jk"))
	jobIDs.append(eachJob.find("data-jk"))
print("Length: " + str(len(jobIDs)))
print("Example JobID: " + str(jobIDs[1]))
"""
"""
# Manual (index) method (NOT WORKING)
# print(justjobs[5])  # DEBUG
#M: used isdigit() instead of isalnum()
for eachJob in justjobs: 
	if(str(eachJob)[115].isalnum() and str(eachJob)[115:117] != "id="):
		jobIDs.append(str(eachJob)[115:131])
	elif(str(eachJob)[66:82].isalnum() and False): # False for debug
		# print("\n"+str(eachJob)[115:117])  # DEBUG
		jobIDs.append(str(eachJob)[66:82])
	else: 
		print(str(eachJob))
		jobIDs.append(str(eachJob)[66:82])  # DEBUG
"""

# Manual (string.find()) method (WORKING)
for eachJob in justjobs: 
	startindex = str(eachJob).find("data-jk")
	jobIDs.append(str(eachJob)[startindex+9:startindex+25])

# DEBUG

IDs = " "
for jobx in jobIDs:
	IDs = IDs + jobx + ", "
print("\n"+str(len(jobIDs))+" JobIDs for "+query+" found:"+IDs[:-2])


# 2: put IDs into URLs, & scrape all of them for keywords
jobListings = []
jobDescs = []
# DEBUG
# jobPage = requests.get("https://www.indeed.com/viewjob?jk="+jobIDs[0])
# print(str(bs4.BeautifulSoup(jobPage.text, "lxml")))
for IDstr in jobIDs:  
	# for each job
	jobTemp = []
	jobTemp.append(str(IDstr))
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
	# print(clutteredTitle[76:76+titleEnd])  # DEBUG
	
	
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

	# GET JOB TEXT FOR QUALIFICATIONS, TASKS, VALUES <?>
	'''find a pattern that distinguishes actual requirements from 
	"who you are", "values", other stuff. maybe look in the previous paragraph?
	>>Try using machine learning here!'''
	# Job Description: <STARTS WITH VERB!!!> Duties, Responsibilities, Tasks, Functions, "work with", " to ",
	# Qualifications: Minimum, Skill, Competencies, "required", "preferred", "degree", "ability"
	# Company Values: Belie-, Value, anything w/"divers-"?
		# >>consider making the array of lines a set
	page_string = pageSoup.get_text("\n")
	# print("Page String of soup: \n"+page_string)  # DEBUG
	# print("Page String get_text: \n"+page_string)  # DEBUG
	page_elements = (page_string.split("\n"))
	reportJob = page_elements.index("Report job")  # index of "Report Job" line, i.e. end of page
	# print(page_elements)  # DEBUG
	pageTextOnly = []  # just text, no \n's
	for elementindex in range(50, len(page_elements[0:reportJob])):
		# test for keywords? or count SQL/AWS, etc.?
		if (len(page_elements[elementindex]) > 1):
			pageTextOnly.append(page_elements[elementindex])
	reviewBoolean = False
	# Now get rid of extra beginning, when reviews present
	if(hasReviews == True): 
		# print("DEBUG: This listing has reviews")  # DEBUG
		# only start page text after second "n reviews"
		for lineNumber in range(0, len(pageTextOnly)):  # look for first "review"
			if reviewBoolean == True:  # start looking for next one
				for nextLineNumber in range(lineNumber, len(pageTextOnly)):
					if " review" in pageTextOnly[nextLineNumber]:
						pageTextOnly = pageTextOnly[nextLineNumber+2:]  # trim off front
						break  # M: forgot this, miscalculated indices (loop iterates again when bool. flips)
				break
			if " review" in pageTextOnly[lineNumber]:  # look for first one
				reviewBoolean = True
	# Trim extra stuff
	  # at the end
	if pageTextOnly[-2]=="original job" and "If you require alternative methods of application" in pageTextOnly[-1]:
		# print("TRIMMED: "+pageTextOnly[-5])  # DEBUG
		pageTextOnly = pageTextOnly[:-6]  # both
	elif pageTextOnly[-1]=="original job":
		# print("TRIMMED: "+pageTextOnly[-4])  # DEBUG
		pageTextOnly = pageTextOnly[:-5]  # "original job" only
	elif pageTextOnly[-2]!="original job" and "If you require alternative methods of application" in pageTextOnly[-1]:
		pageTextOnly = pageTextOnly[:-2]  # "If you require" only
	  # at the beginning
	if(pageTextOnly[0] == "Find Jobs"): 
		print("TRIMMED2: "+pageTextOnly[4]+" "+pageTextOnly[5])
		pageTextOnly = pageTextOnly[6:]  
	
	# print(IDstr+" at "+fullCompany+": ")  # DEBUG
	# for trimIndx in range(0, len(pageTextOnly)):  # DEBUG (took out string casting?)
	# 	# these indices will be different from previous ones (\n's removed)
	# 	print(pageTextOnly[trimIndx])
	jobTextTemp = IDstr+" at "+fullCompany+": \n"+"\n".join(pageTextOnly)+"\n"
	jobDescs.append(jobTextTemp)
	print("")
	"""
	#### vvv temporarily disabled
	# vvv this method may break if there are lists in other lists... consider creating a stack to count <ul>'s (+1) and </ul>'s (-1) (=1 or 0, never 2)
	# vvv also doesn't work on job listings without <ul>'s, e.g. jk = a31451fe54f92742
	body_string = str(pageSoup.select(".jobsearch-jobDescriptionText"))
	ul_matchStarts = re.finditer("<ul>", body_string)
	ul_matchEnds = re.finditer("</ul>", body_string)
	ul_matchIndexes = []
	for startMatch, endMatch in zip(ul_matchStarts, ul_matchEnds):
		ul_matchIndexes.append((startMatch.end(), endMatch.start()))
	# print("<ul> locations: " + str(ul_matchIndexes))  # DEBUG
	oneUL = []
	for start_ul,end_ul in ul_matchIndexes:
		# print(IDstr+": ul Body For "+fullCompany+": ---\n" + body_string[start_ul:end_ul])  # DEBUG
		oneUL = body_string[start_ul:end_ul]
		oneUL = oneUL[4:-5]  # to get rid of tags at the beginning, end
	oneUL = "".join(oneUL)
	listofLIs = []
	liSplit = oneUL.split("><")   ;print("DEBUG: "+str(liSplit))  # DEBUG  
	joinStr = "".join(liSplit)	# ;print("===Removed ><'s: "+joinStr)  # DEBUG  # now we have big tags
	liSplit2 = re.split(">|<", joinStr)  # ;print("Raw: "+str(liSplit2))  # DEBUG
	for liOrTag in liSplit2: 
		# print("LI or Tag: "+liOrTag)  # DEBUG
		if (len(liOrTag) > 0) and (liOrTag[0] == "\n"):  # the "\n" string itself becomes a newline character, not a \\ literal
			liTagNew = liOrTag[1:]
			# print("starts with \\! New: "+liTagNew)  # DEBUG
		else:
			liTagNew = liOrTag
		if (len(liTagNew) > 0) and (liTagNew != "\\n") and (liTagNew != "li") and (liTagNew != "lii"):
			# filters out garbage tags
			listofLIs.append(liTagNew)
	print(IDstr+": LI's For "+fullCompany+": " + str(listofLIs))  # DEBUG
	#### ^^^ temporarily disabled
	"""
	jobTemp.append(clutteredTitle[77:76+titleEnd])  #77 takes out the ">"

	jobTemp.append(jobAge)

	# jobTemp.append(fullSalary)
	
	jobTemp.append(fullCompany)  

	jobTemp.append(fullLocation[2:-1])

	jobTemp.append(companyReviews)

	jobTemp.append(str(companyRating) if str(companyRating)[:2] == "No" 
			else (str(companyRating*100)[:2]+"%"))
		# also add separate "weight" to higher/more rated companies?
	# print("===================")
	# print(jobTemp)  # DEBUG
	jobListings.append(jobTemp)

print("------------------------------")
print("Job listings for: "+query)
print("Job order      Job Key      Job title      Time posted      Company      Location      Reviews      Rating")
for prIndex in range(0, len(jobListings)):
	print(str(prIndex+1)+"	"+"	".join(jobListings[prIndex]))
	# print(str(listing[:-1]))  # everything but qualifs  # temp. disabled
	# for item in listing[-1]:  # temporarily disabled
		# print(str(item))  # print qualifications on separate lines
print("------------------------------")
for descIndex in range(0, len(jobDescs)):
	print(jobDescs[descIndex])
	print("====================")
# print("Job Listings: "+str(jobListings))  # DEBUG
# print("Type: "+str(type(jobListings[0])))  # DEBUG: type = list (each job listing)
# print("Type: "+str(type(jobListings[0][0])))  # DEBUG: type = string (each job listing's job title)
# DEBUG
"""
jobPage = requests.get("https://www.indeed.com/viewjob?jk="+jobIDs[0])
pageSoup = bs4.BeautifulSoup(jobPage.text, "lxml")
print(type(pageSoup))  
print(str(pageSoup.select('.icl-u-xs-mb--xs')))
"""

"""
There could be multiple arrays/one main array with subarrays 
that extend job titles and other elements in the top bar. 
We need: Job title, company, salary?, job description.

Look for SQL or AWS separately, to count how many of each?
"""

# 3: DATA: keep track of how many times a predetermined word appears








endTime = time.time()
totalRuntime = endTime - startTime
print("BOTTOM of output ========")
print("Time needed: "+str(totalRuntime)[:6]+" secs")
