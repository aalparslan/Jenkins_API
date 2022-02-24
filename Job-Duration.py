from distutils.command.build import build
import re
from unittest import removeResult
from html5lib import serialize
import jenkins
import matplotlib.pyplot as plt
import matplotlib
import time
import sys,getopt
import numpy as np
from datetime import date, datetime

class DurationMetrics:
    username = ''
    password = ''
    server = None
    buildDurations = []
    buildTimeStamps = []
    totalNumberOfBuilds = 0.0
    totalDuration = 0.0

    def __init__(self, username, password):
        self.username = username
        self.password = password

    
    def calculateAverageDuration(self):
        averageDuration = (self.totalDuration / self.totalNumberOfBuilds)
        print(f'Average Build Duration {averageDuration}')
        

    def connetToJenkins(self):
        self.server = jenkins.Jenkins('http://localhost:8080', username= self.username, password= self.password)
        user = self.server.get_whoami()
        version = self.server.get_version()
        print(f'Hello from Jenkins {user["fullName"]} {version}')

    def getjobDuration(self):
        jenkinsJobs = self.server.get_all_jobs()
        myJob =  self.server.get_job_info('UpworkJob', 0, True)
        myJobBuilds = myJob.get('builds')
        for build in myJobBuilds:
            buildNumber = build.get('number')
            buildInfo = self.server.get_build_info('UpworkJob', buildNumber)
            buildTimeStamp = buildInfo.get('timestamp')
            buildDuration = buildInfo.get('duration')/1000
            self.buildDurations.append(buildDuration)
            self.buildTimeStamps.append(buildTimeStamp)
            self.totalDuration += buildDuration
            self.totalNumberOfBuilds += 1.0

    def plotJobDuration(self):
        #TODO: plot job durations
        dateTimeObjs = self.converTimeStamps()
        dates = matplotlib.dates.date2num(dateTimeObjs)
        npArray = self.runningMean()
        plt.plot_date(dates[:-9], npArray, '-')
        plt.xlabel('Time of Execution')
        plt.ylabel('Build Duration (Seconds)')
        plt.title('Build Durations Over Time')
        plt.gcf().autofmt_xdate()
        plt.show()


    def converTimeStamps(self):
        dates = []
        for timeStamp in self.buildTimeStamps:
            dateTimeObj = datetime.fromtimestamp((timeStamp / 1000))
            dates.append(dateTimeObj)
        return dates

    def runningMean(self):
        npArr = np.convolve(self.buildDurations, np.ones((10,))/10, mode='valid')
        return npArr



def main(argv):
    username = ''
    password = ''

    try:
        opts, args = getopt.getopt(argv, "hu:p:", ["username=", "password="])
    except getopt.GetoptError:
        print
        'python Job-Duration-Metrics.py -u <username> -p <password>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print
            'python Job-Duration-Metrics.py -u <username> -p <password>'
            sys.exit()
        elif opt == '-u':
            username = arg
        elif opt == '-p':
            password = arg

    durationMetrics = DurationMetrics(username, password)
    durationMetrics.connetToJenkins()
    durationMetrics.getjobDuration()
    durationMetrics.calculateAverageDuration()
    durationMetrics.plotJobDuration()


if __name__ == "__main__":
    main(sys.argv[1:])
