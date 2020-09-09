import mysql.connector
import threading
import time as t
from queue import Queue
import json
import argparse

class SQLPublisher():

    def __init__(self,filename,threads=10):
        self.taskNumber=0
        self.loadDataFromFile(filename)
        self.startingTime=t.time()
        self.setupWorkers(threads)
    
    def loadDataFromFile(self,filename):
        with open(filename) as f:
            self.data=json.load(f)
    def setupWorkers(self,numOfWorkers):
        self.queue = Queue(numOfWorkers)
        for _ in range(numOfWorkers):
            thread = threading.Thread(target = self.connect)
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

    def connect(self):
        while True:
            try:
                data=self.queue.get()           
                task=self.taskNumber
                self.taskNumber+=1
                currTime=t.time()
                mydb = mysql.connector.connect(
                host=data["host"],
                user= data["username"],
                password=data["password"],
                port=data["port"]
                )
                if data["query"]:
                    mycursor = mydb.cursor()
                    mycursor.execute(data["query"])
                delay=(t.time()-currTime)*1000 
                print("Task: ",task," Time elapsed: %.3f"%(t.time()-self.startingTime),"s Delay: %.2f"%delay,"ms")
                self.queue.task_done()
            except Exception as e:
                print("Something went wrong! ",e)   


if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input-file',type=str,help="JSON input file with generated sql requests")
    parser.add_argument('-t','--threads',type=int,default=10,help="Number of threads,default:10")

    FLAGS,unparsed=parser.parse_known_args()
    if not FLAGS.input_file:
        print("You must enter input file path (-i), Exiting")
        exit()
    print(FLAGS.threads)

    m=SQLPublisher(FLAGS.input_file,FLAGS.threads)
    while True:
        pass