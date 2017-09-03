import git
import csv
import re
import datetime
import time
import requests
from github import Github


class aProject:
    def __init__(self, org, repo, projectName):
        self.org = org
        self.repo = repo
        self.projectName = projectName


def openRepo(repoName):
    return git.Repo(repoName)

def getOriginalLines(openedRepo):
    lines = openedRepo.git.stat

def computeTime(someCommit):
    time.asctime(time.gmtime(someCommit.committed_date))
    return time.strftime("%a, %d %b %Y %H:%M", time.gmtime(someCommit.committed_date))

def getAgeOfCode(openedRepo):
    firstCommit = openedRepo.commit('master')
    newestCommit = openedRepo.head.commit
    firstTime = computeTime(firstCommit)
    newestTime = computeTime(newestCommit)
    print (firstTime)
    print (newestTime)

def getReleaseAuthors(openedRepo):
    logInfo = openedRepo.git.log("--all", "-i")
    if ( len(logInfo) == 0):
        return []
    else:
        print logInfo
        developers = re.findall('(?<=Author: )([a-zA-Z ]+)', logInfo)
        for dev in developers:
            print (dev)

def getFurtherPulls(gitKey, organization, gitRepo):
    git = Github(gitKey)
    org = git.get_organization(organization)
    repo = org.get_repo(gitRepo)
    count = 0
    for pull in repo.get_pulls('all'):
        count = count + 1
        #print "TITLE:",pull.title
    print ("total pulls:",count)
    return count

def getTotalCommits(gitKey, organization, gitRepo):
    count = 0
    git = Github(gitKey)
    org = git.get_organization(organization)
    repo = org.get_repo(gitRepo)
    commitList = repo.get_commits()
    for commit in commitList:
        count = count + 1
    return count


def isMirror(gitKey, organization, gitRepo):
    git = Github(gitKey)
    org = git.get_organization(organization)
    repo = org.get_repo(gitRepo)
    description = repo.description
    print "description:",description
    a = re.search('mirror', description, re.IGNORECASE)
    if a != None:
        return 1
    else:
        mirrorUrl = repo.mirror_url
        print "mirror URL: ", mirrorUrl
        if (mirrorUrl != ""):
            return 1
        else:
            return 0


def getRecentCommits(gitKey, organization, gitRepo):
    count = 0
    git = Github(gitKey)
    org = git.get_organization(organization)
    repo = org.get_repo(gitRepo)
    d = datetime.datetime.now() - datetime.timedelta(days=30)
    commitList = repo.get_commits(since=d)
    for commit in commitList:
        count = count + 1
    return count

def earliestCommitYoungerThan(gitKey, organization, gitRepo, months):
    count = 0
    git = Github(gitKey)
    org = git.get_organization(organization)
    repo = org.get_repo(gitRepo)
    d = datetime.datetime.now() - datetime.timedelta(days=30*months)
    commitList = repo.get_commits(since=d)
    for commit in commitList:
        count = count + 1
    if (count != 0):
        return 1
    else:
        return 0

def getStressInfo(csvFileName, typeOfInfo, PROJECT_NAME):
    count = 0
    place = 0
    lastCommitPlace = 0
    authorPlace = 0
    commitCountPlace = 0
    with open(csvFileName) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            columns = row
            for item in columns:
                if (item == "projectName"):
                    place = count
                if (item == "lastCommit"):
                    lastCommitPlace = count
                if (item == "numberAuthors"):
                    authorPlace = count
                if (item == "commitCount"):
                    commitCountPlace = count
                count = count + 1

            break
        for row in readCSV:
            if row[place] == PROJECT_NAME:
                print "woo hoo!"
                print "last commit:", row[lastCommitPlace]
                lastCommit = row[lastCommitPlace]
                print "number of authors:", row[authorPlace]
                authors = row[authorPlace]
                print "commit count:", row[commitCountPlace]
                commitCount = row[commitCountPlace]
                print "id:",row[0]
    if (typeOfInfo == "lastCommit"):
        return lastCommit
    elif (typeOfInfo == "numberAuthors"):
        return authors
    elif (typeOfInfo == "commitCount"):
        return commitCount
    else:
        print "input did not match options."
        return 0

def getUnnamedCommits(gitKey, org, gitRepo):
    git = Github(gitKey)
    org = git.get_organization(org)
    repo = org.get_repo(gitRepo)
    listOfAuthors = []
    commitCount = 0
    unnamedCommits = 0
    for commit in repo.get_commits():
        comAuthor = commit.author
        if comAuthor is None:
            unnamedCommits = unnamedCommits + 1
        else:
            loginName = comAuthor.login
            if loginName not in listOfAuthors:
                listOfAuthors.append(loginName)
        commitCount = commitCount + 1
    print "number of unnamedCommits:",unnamedCommits
    return unnamedCommits


def generateList(GIT_KEY, project):
    GIT_ORG = project.org
    GIT_REPO = project.repo
    PROJECT_NAME = project.projectName
    totalCommits = getTotalCommits(GIT_KEY, GIT_ORG, GIT_REPO)
    recentCommits = getRecentCommits(GIT_KEY, GIT_ORG, GIT_REPO)
    mostRecentCommit = earliestCommitYoungerThan(GIT_KEY, GIT_ORG, GIT_REPO, 2)
    numAuthors = getStressInfo("STRESSmetrics.csv", "numberAuthors", PROJECT_NAME)
    mirror = isMirror(GIT_KEY, GIT_ORG, GIT_REPO)
    unnamedCommits = getUnnamedCommits(GIT_KEY, GIT_ORG, GIT_REPO)
    percentUnnamed = ((unnamedCommits)/ float(totalCommits)) * 100
    pullRequests = getFurtherPulls(GIT_KEY, GIT_ORG, GIT_REPO)
    metricsList = [PROJECT_NAME, totalCommits, recentCommits, mostRecentCommit,
                   numAuthors, mirror, unnamedCommits,
                   percentUnnamed, pullRequests]
    return metricsList

def writeToCSV(metricsList):
    with open("TikaMetrics.csv", 'wb') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        perilsNames = ['',
                       'peril 2',
                       'peril 2 & 3',
                       'peril 3',
                       'peril 5',
                       'peril 6',
                       'peril 10',
                       'peril 10',
                       'peril 7']
        metricsNames = ['Project Name',
                        '# Total Commits',
                        '# Total commits within month',
                        'Newest Commit <1 month old',
                        '# of authors',
                        'Whether project is a mirror',
                        '# non-user Commits',
                        '% non-user Commits',
                        '# of Pull Requests']

        wr.writerow(perilsNames)
        wr.writerow(metricsNames)
        for item in metricsList:
            wr.writerow(item)

def main():
    gitKey = "2d4389a1baa643f581fcc8b90a6187d18f0d3394"
    projectList = []
    tika = aProject("apache", "tika", "Apache Tika")
    accumulo = aProject("apache", "accumulo", "Apache Accumulo")
    projectList.append(generateList(gitKey, tika))
    projectList.append(generateList(gitKey, accumulo))
    writeToCSV(projectList)

if __name__ == "__main__":
    main()



