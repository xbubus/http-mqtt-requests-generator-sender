import random
import matplotlib.pyplot as plt    
import math
import numpy as np
import json
import collections
import argparse

class dataGenerator():

    def __init__(self,filename,http_out,mqtt_out,ssh_out,http=False,mqtt=False,ssh=False,rand=0):
        self.loadTasks(filename)
        self.http_plot=[]
        self.mqtt_plot=[]
        self.ssh_plot=[]
        self.data={}
        self.rand=rand
        self.randData=[]
        if rand:
            self.generateRandomData()
        if http:
            self.generate(http=True)
            self.merged=self.mergeData(self.getTasks()[0])
            self.sort(self.merged)
            self.save(http_out)
        if mqtt:
            self.generate(mqtt=True)
            self.merged=self.mergeData(self.getTasks()[1])
            self.sort(self.merged)
            self.save(mqtt_out)
        if ssh:
            self.generate(ssh=True)
            self.merged=self.mergeData(self.getTasks()[2])
            self.sort(self.merged)
            self.save(ssh_out)
    def loadTasks(self,filename):
        with open(filename,'r') as f:
            self.fulldata=json.load(f)
             
    def generate(self,http=False,mqtt=False,ssh=False):
        self.httpTasks=[]
        self.mqttTasks=[]
        self.sshTasks=[]
        if http:
            self.rOff=0
            for d in self.fulldata["http_tasks"]:
                self.data=d
                self.result=self.generateProbabilityDenistyFunction()
                self.mappedY=self.mapRequestsPerSecound(self.result[1],d["tasks"])
                self.printNumOfReq()
                self.mappedX=self.mapValues(self.result[0],d["time"])
                self.http_plot.append((self.mappedX,self.mappedY,(d["url"],d["method"])))
                self.generateRequestsData(self.mappedX,self.mappedY)
                self.httpTasks.append(self.dictR)
                self.rOff+=1

        if mqtt:
            self.mOff=0
            for d in self.fulldata["mqtt_tasks"]:
                self.data=d
                self.result=self.generateProbabilityDenistyFunction()
                self.mappedY=self.mapRequestsPerSecound(self.result[1],d["tasks"])
                self.printNumOfReq()
                self.mappedX=self.mapValues(self.result[0],d["time"])
                self.mqtt_plot.append((self.mappedX,self.mappedY,(d["url"],d["topic"])))
                self.generateMQTTdata(self.mappedX,self.mappedY)
                self.mqttTasks.append(self.dictM)
                self.mOff+=1
        if ssh:
            self.sOff=0
            for d in self.fulldata["ssh_tasks"]:
                self.data=d
                self.result=self.generateProbabilityDenistyFunction()
                self.mappedY=self.mapRequestsPerSecound(self.result[1],d["tasks"])
                self.printNumOfReq()
                self.mappedX=self.mapValues(self.result[0],d["time"])
                self.ssh_plot.append((self.mappedX,self.mappedY,(d["host"],d["port"])))
                self.generateSSHdata(self.mappedX,self.mappedY)
                self.sshTasks.append(self.dictS)
                self.sOff+=1

    def getTasks(self):
        return self.httpTasks,self.mqttTasks,self.sshTasks
    def printNumOfReq(self):
        sum=0
        for v in self.mappedY:
            sum+=v
        print("Request generated: ",sum)

    def gauss(self,x):
       # print(self.data["mi"])
        return 1/(self.data['sigma']*math.sqrt(2*math.pi))*math.exp((-pow((x-self.data['mi']),2))/(2*pow(self.data['sigma'],2)))

    def generateProbabilityDenistyFunction(self):
        yAxis=[]
        xAxis=[]
        resolution =0.1
        if  self.data['sigma']!=0:
            resolution =self.data['sigma']/100.
        resolution=19/self.data["time"]*40000/self.data["tasks"]
        for i in np.arange(-10,10,resolution):  
            yAxis.append(self.gauss(i))
            xAxis.append(i)
        #print(xAxis)
        return xAxis,yAxis

    def mapValue(self,val,in_min,in_max,out_min,out_max):
        return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def mapValues(self,values,max_value,min_value=0):
        sortedValues=sorted(values)
        return [self.mapValue(val,sortedValues[0],sortedValues[-1],min_value,max_value) for val in values]

    def mapRequestsPerSecound(self,values,requestNumber):
        sum=0
        for val in values:
            sum+=val
        if self.rand:
            return [round(val*requestNumber/sum * (1+random.choice(self.randData)/100.)) for val in values] 
        return [round(val*requestNumber/sum ) for val in values]

    def generateRequestsData(self,x,y):
        self.dictR={}
        for i in range(len(x)):
            self.dictR[x[i]+0.001*self.rOff]={"numberOfTasks":y[i],"url":self.data["url"],"method":self.data["method"],"headers":self.data["headers"],"body":self.data["body"]} # timestamp offset, requests/secound
        #print(self.dictR)
    def generateMQTTdata(self,x,y):
        self.dictM={}
        for i in range(len(x)):
            self.dictM[x[i]+0.001*self.mOff]={"numberOfTasks":y[i],"url":self.data["url"],"topic":self.data["topic"],"port":self.data["port"],"msg":self.data["msg"],"username":self.data["username"],"password":self.data["password"]}
    def generateSSHdata(self,x,y):
        self.dictS={}
        for i in range(len(x)):
            self.dictS[x[i]+0.001*self.sOff]={"numberOfTasks":y[i],"host":self.data["host"],"port":self.data["port"],"username":self.data["username"],"password":self.data["password"]}
    def mergeData(self,data): #http
        merged={}
        for d in data:
            merged={**merged,**d}
        return merged
    def sort(self,data):
        self.sortedDict=collections.OrderedDict(sorted(data.items()))
    def save(self,filename):
        with open(filename, 'w') as outfile:
            json.dump(self.sortedDict, outfile)
        print("Generated and saved to: ",filename)
    def getPlotData(self):
        return self.http_plot,self.mqtt_plot,self.ssh_plot
    def generateRandomData(self):
        self.data['sigma']=8
        self.data['mi']=self.rand
        yAxis=[]
        xAxis=[]
        resolution=0.1
        for i in np.arange(-100,100,resolution):  
            yAxis.append(self.gauss(i))
            xAxis.append(i)
        for i in range(len(xAxis)):
            for _ in np.arange(0.00001,yAxis[i],0.001):
                 self.randData.append(xAxis[i])
        print(self.randData)
def show_plots(data):
    http=data[0]
    mqtt=data[1]
    ssh=data[2]
    httpSize=0
    mqttSize=0
    sshSize=0
    for _ in http:  httpSize+=1
    for _ in mqtt: mqttSize+=1
    for _ in ssh: sshSize+=1
    if not httpSize and not mqttSize and not sshSize: 
        print("Nothing to show on plot")
        return
    if httpSize:
        fig1,axs = plt.subplots(httpSize,1,sharex=True,sharey=True)
        i=0
        for d in http:
            axs[i].plot(d[0],d[1])
            s=0
            axs[i].set_title(d[2],fontsize=5)
            i+=1
    if mqttSize:
        fig2,axs = plt.subplots(mqttSize,1,sharex=True,sharey=True)
        i=0
        for d in mqtt:
            axs[i].plot(d[0],d[1])
            s=0
            axs[i].set_title(d[2],fontsize=5)
            i+=1
    if sshSize:
        fig3,axs = plt.subplots(sshSize,1,sharex=True,sharey=True)
        i=0
        for d in ssh:
            axs[i].plot(d[0],d[1])
            s=0
            axs[i].set_title(d[2],fontsize=5)
            i+=1
    plt.show()

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input-file',type=str,help="JSON input file with requests")
    parser.add_argument('-gh','--generate-http',action='store_true',help="Generate http requests")
    parser.add_argument('-gm','--generate-mqtt',action='store_true',help="Generate mqtt requests")
    parser.add_argument('-gs','--generate-ssh',action='store_true',help="Generate ssh requests")
    parser.add_argument('-oh','--http-output-file',type=str,default="http_out.json",help="JSON output file with http requests")
    parser.add_argument('-om','--mqtt-output-file',type=str,default="mqtt_out.json",help="JSON output file with mqtt requests")
    parser.add_argument('-os','--ssh-output-file',type=str,default="ssh_out.json",help="JSON output file with ssh requests")
    parser.add_argument('-p','--plot',action='store_true',help="Show plots")
    parser.add_argument('-r','--random',type=int,default=0,help="Randomize requests output by given number (-r 5 (%%))")

    FLAGS,unparsed=parser.parse_known_args()
    if not FLAGS.input_file:
        print("You must enter input file path (-i), Exiting")
        exit()
    if not FLAGS.generate_http and not FLAGS.generate_mqtt and not FLAGS.generate_ssh:
        print("Nothing to generate, use -gh or/and -gm -gs, Exiting...")
        exit()
    
    d=dataGenerator(FLAGS.input_file,FLAGS.http_output_file,FLAGS.mqtt_output_file,FLAGS.ssh_output_file,FLAGS.generate_http,FLAGS.generate_mqtt,FLAGS.generate_ssh,FLAGS.random)
    
    if FLAGS.plot:
        show_plots(d.getPlotData())

