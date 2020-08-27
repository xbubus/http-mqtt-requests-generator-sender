import paho.mqtt.client as mqtt
import threading
import time as t
from queue import Queue
import json
import random
import argparse
import string
class MQTTPublisher():

    def __init__(self,filename,threads=10):
        self.taskNumber=0
        self.loadDataFromFile(filename)
        self.startingTime=t.time()
        self.setupWorkers(threads)
    
    def loadDataFromFile(self,filename):
        with open(filename) as f:
            self.data=json.load(f)
        
    def getRandomString(self,length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str
    def setupWorkers(self,numOfWorkers):
        self.queue = Queue(numOfWorkers)
        for _ in range(numOfWorkers):
            thread = threading.Thread(target = self.publish)
            thread.daemon = True
            thread.start()
        print("Workers added!")
        self.setupAddingThread()

    def setupAddingThread(self):
        thread = threading.Thread(target = self.addTasks)
        thread.daemon = True
        thread.start()

    def addTasks(self):
        for key,value in self.data.items():
            try:
                while float(key)>=t.time()-self.startingTime:
                    pass
                req=0
                for _ in range(value["numberOfTasks"]):
                    self.queue.put(value)
                    req+=1
                if req>0:
                    print("Added ",req,"to queue")
            except:
                pass
        self.queue.join()

        print("Finished!")
        print("Requests: ",self.taskNumber,"time: ",t.time()-self.startingTime)
        print("Ctrl-C to exit")

    def publish(self):
        client=mqtt.Client(self.getRandomString(5))
        while True:
            try:
                data=self.queue.get()           
                task=self.taskNumber
                self.taskNumber+=1
                client.username_pw_set(data["username"], data["password"])
                client.connect(data["url"],data["port"],3600)
               #print(data["msg"])
                client.publish(data["topic"],payload=data["msg"])             
                print("Task: ",task," Time elapsed: %.3f"%(t.time()-self.startingTime))
                self.queue.task_done()
            except Exception as e:
                print("Something went wrong! ",e)   


if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input-file',type=str,help="JSON input file with generated mqtt requests")
    parser.add_argument('-t','--threads',type=int,default=10,help="Number of threads,default:10")

    FLAGS,unparsed=parser.parse_known_args()
    if not FLAGS.input_file:
        print("You must enter input file path (-i), Exiting")
        exit()
    print(FLAGS.threads)

    m=MQTTPublisher(FLAGS.input_file,FLAGS.threads)
    while True:
        pass