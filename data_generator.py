import random
import matplotlib.pyplot as plt    
import math
import numpy as np
import json
import collections
import argparse

class dataGenerator():

    def __init__(self,FLAGS):
        self.loadTasks(FLAGS.input_file)
        self.http_plot=[]
        self.mqtt_plot=[]
        self.ssh_plot=[]
        self.sql_plot=[]
        self.ftp_plot=[]
        self.data={}
        self.rand=FLAGS.random
        self.randData=[]
        self.initArgs(FLAGS)
        if self.rand:
            self.generateRandomData()
        self.generate()
            
    def initArgs(self,args):
        argsDict=args.__dict__
        try:
            self.http=argsDict["generate_http"]
            self.mqtt=argsDict["generate_mqtt"]
            self.ssh=argsDict["generate_ssh"]
            self.sql=argsDict["generate_sql"]
            self.ftp=argsDict["generate_ftp"]
            self.http_out=argsDict["http_output_file"]
            self.mqtt_out=argsDict["mqtt_output_file"]
            self.ssh_out=argsDict["ssh_output_file"]
            self.sql_out=argsDict["sql_output_file"]
            self.ftp_out=argsDict["ftp_output_file"]
        except Exception as e:
            print(e)
            print("Criticall error, Exiting...")
            exit(0)

    def loadTasks(self,filename):
        with open(filename,'r') as f:
            self.fulldata=json.load(f)
             
    def generate(self): #todo: rewrite this 
        self.httpTasks=[]
        self.mqttTasks=[]
        self.sshTasks=[]
        self.sqlTasks=[]
        self.ftpTasks=[]
        if self.http:
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
            self.merged=self.mergeData(self.httpTasks)
            self.sort(self.merged)
            self.save(self.http_out)
        if self.mqtt:
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
            self.merged=self.mergeData(self.mqttTasks)
            self.sort(self.merged)
            self.save(self.mqtt_out)
        if self.ssh:
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
            self.merged=self.mergeData(self.sshTasks)
            self.sort(self.merged)
            self.save(self.ssh_out)
        if self.sql:
            self.sqOff=0
            for d in self.fulldata["sql_tasks"]:
                self.data=d
                self.result=self.generateProbabilityDenistyFunction()
                self.mappedY=self.mapRequestsPerSecound(self.result[1],d["tasks"])
                self.printNumOfReq()
                self.mappedX=self.mapValues(self.result[0],d["time"])
                self.sql_plot.append((self.mappedX,self.mappedY,(d["host"],d["port"])))
                self.generateSQLdata(self.mappedX,self.mappedY)
                self.sqlTasks.append(self.dictSQ)
                self.sqOff+=1
            self.merged=self.mergeData(self.sqlTasks)
            self.sort(self.merged)
            self.save(self.sql_out)
        if self.ftp:
            self.fOff=0
            for d in self.fulldata["ftp_tasks"]:
                self.data=d
                self.result=self.generateProbabilityDenistyFunction()
                self.mappedY=self.mapRequestsPerSecound(self.result[1],d["tasks"])
                self.printNumOfReq()
                self.mappedX=self.mapValues(self.result[0],d["time"])
                self.ftp_plot.append((self.mappedX,self.mappedY,d["host"]))
                self.generateFTPdata(self.mappedX,self.mappedY)
                self.ftpTasks.append(self.dictF)
                self.fOff+=1
            self.merged=self.mergeData(self.ftpTasks)
            self.sort(self.merged)
            self.save(self.ftp_out)
    def getTasks(self):
        return self.httpTasks,self.mqttTasks,self.sshTasks,self.sqlTasks,self.ftpTasks
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
    def generateSQLdata(self,x,y):
        self.dictSQ={}
        for i in range(len(x)):
            self.dictSQ[x[i]+0.001*self.sqOff]={"numberOfTasks":y[i],"host":self.data["host"],"port":self.data["port"],"username":self.data["user"],"password":self.data["password"],"query":self.data["query"]}
    def generateFTPdata(self,x,y):
        self.dictF={}
        for i in range(len(x)):
            self.dictF[x[i]+0.001*self.fOff]={"numberOfTasks":y[i],"host":self.data["host"],"username":self.data["user"],"password":self.data["password"]}
    
    def mergeData(self,data): 
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
        return self.http_plot,self.mqtt_plot,self.ssh_plot,self.sql_plot,self.ftp_plot
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

def show_one_plot(data,size):
    if size:
        fig,axs = plt.subplots(size,1,sharex=True,sharey=True)
        i=0
        if size==1:
            axs.plot(data[0][0],data[0][1])
            axs.set_title(data[0][2],fontsize=5)
        else: 
            for d in data:
                axs[i].plot(d[0],d[1])
                axs[i].set_title(d[2],fontsize=5)
                i+=1
    
def show_plots(data):
    sizes=[]
    count=0
    for d in data:
        size=0
        for _ in d: size+=1
        sizes.append(size)
        count+=size
    if not count: 
        print("Nothing to show on plot")
        return
    for i,d in enumerate(data):
        show_one_plot(d,sizes[i])
    plt.show()

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input-file',type=str,help="JSON input file with requests")
    parser.add_argument('-gh','--generate-http',action='store_true',help="Generate http requests")
    parser.add_argument('-gm','--generate-mqtt',action='store_true',help="Generate mqtt requests")
    parser.add_argument('-gs','--generate-ssh',action='store_true',help="Generate ssh requests")
    parser.add_argument('-gsq','--generate-sql',action='store_true',help="Generate sql requests")
    parser.add_argument('-gf','--generate-ftp',action='store_true',help="Generate ftp requests")
    parser.add_argument('-oh','--http-output-file',type=str,default="http_out.json",help="JSON output file with http requests")
    parser.add_argument('-om','--mqtt-output-file',type=str,default="mqtt_out.json",help="JSON output file with mqtt requests")
    parser.add_argument('-os','--ssh-output-file',type=str,default="ssh_out.json",help="JSON output file with ssh requests")
    parser.add_argument('-osq','--sql-output-file',type=str,default="sql_out.json",help="JSON output file with sql requests")
    parser.add_argument('-of','--ftp-output-file',type=str,default="ftp_out.json",help="JSON output file with ftp requests")
    parser.add_argument('-p','--plot',action='store_true',help="Show plots")
    parser.add_argument('-r','--random',type=int,default=0,help="Randomize requests output by given number (-r 5 (%%))")

    FLAGS,unparsed=parser.parse_known_args()
    if not FLAGS.input_file:
        print("You must enter input file path (-i), Exiting")
        exit()
    if not FLAGS.generate_http and not FLAGS.generate_mqtt and not FLAGS.generate_ssh and not FLAGS.generate_sql and not FLAGS.generate_ftp:
        print("Nothing to generate, use -gh or/and -gm -gs -gsq -gf, Exiting...")
        exit()
    
    d=dataGenerator(FLAGS)
    
    if FLAGS.plot:
        show_plots(d.getPlotData())

