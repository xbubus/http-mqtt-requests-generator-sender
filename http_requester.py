
import requests
import threading
import time as t
from queue import Queue
import json
import argparse
class Requester():

    def __init__(self,filename,threads=40):
        self.loadDataFromFile(filename)      
        self.taskNumber=0
        self.startingTime=t.time()
        self.setupWorkers(threads)
        
    def loadDataFromFile(self,filename):
        with open(filename) as f:
            self.data=json.load(f)
            #print(self.data)    

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
                for i in range(value["numberOfTasks"]):
                    self.queue.put(value)
                    req+=1
                if req>0:
                    print("Added ",req,"to queue")
            except Exception as e:
                print(e)
        self.queue.join()
        print("Finished!")
        print("Requests: ",self.taskNumber,"time: ",t.time()-self.startingTime)
        print("Ctrl-C to exit")

    def connect(self):
        while True:
            try:
                taskData = self.queue.get()           
                task=self.taskNumber
                self.taskNumber+=1
                currTime=t.time() 
                if taskData["method"]=="GET": 
                    r=requests.get(taskData["url"],headers=taskData["headers"])
                    delay=(t.time()-currTime)*1000               
                    print("Task: ",task," Status Code: ",r.status_code," Time elapsed: %.3f"%(t.time()-self.startingTime), "s Delay: %.2f"%delay,"ms")
                    self.queue.task_done() 
                elif taskData["method"]=="POST": 
                    r=requests.post(taskData["url"],headers=taskData["headers"],data=taskData["body"])
                    delay=(t.time()-currTime)*1000               
                    print("Task: ",task," Status Code: ",r.status_code," Time elapsed: %.3f"%(t.time()-self.startingTime), "s Delay: %.2f"%delay,"ms")
                    self.queue.task_done()
                elif taskData["method"]=="DELETE":
                    r=requests.delete(taskData["url"],headers=taskData["headers"],data=taskData["body"])
                    delay=(t.time()-currTime)*1000               
                    print("Task: ",task," Status Code: ",r.status_code," Time elapsed: %.3f"%(t.time()-self.startingTime), "s Delay: %.2f"%delay,"ms")
                    self.queue.task_done()
                else:
                    print("ERROR: Unsuported method type : ",taskData["method"])
                    self.queue.task_done()
                
            except Exception as e:
                print("Something went wrong! ",e)

    def setupWorkers(self,numOfWorkers):
        self.queue = Queue(numOfWorkers)
        for _ in range(numOfWorkers):
            thread = threading.Thread(target = self.connect)
            thread.daemon = True
            thread.start()
        print("Workers added!")
        self.setupAddingThread()

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input-file',type=str,help="JSON input file with generated requests")
    parser.add_argument('-t','--threads',type=int,default=40,help="Number of threads,default:40")

    FLAGS,unparsed=parser.parse_known_args()
    if not FLAGS.input_file:
        print("You must enter input file path (-i), Exiting")
        exit()

    r=Requester(FLAGS.input_file,FLAGS.threads)
    while True:
        pass