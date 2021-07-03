from selenium import webdriver
import time
from selenium.webdriver.firefox.options import Options
import os
import random
import json
import threading
from os import path
from requests import get
import tqdm
from html.parser import HTMLParser
import re
from datetime import datetime
from vpnswitch import *

class HTMLFilter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data

import os, sys, subprocess, json, argparse, signal
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import random
from datetime import datetime




class OBJ:
    def __init__(self,url,worker_count,user_agents,inputfile,outputfile,vpn,reset):
        self.user_agents = user_agents
        self.url = url
        self.worker_count = worker_count
        self.input_file = inputfile
        self.output_file = outputfile
        self.vpn = vpn
        self.reset = reset

    def randagent(self):
        return random.choice(self.user_agents)

    def search(self,job,id,reset_time=60):
        count = 0
        while True:
            time.sleep(random.random())
            try:
                options = Options()
                options.add_argument('--headless')
                print("Worker",id,"INIT")
                profile = webdriver.FirefoxProfile()
                profile.set_preference("general.useragent.override", self.randagent())
                driver = webdriver.Firefox(options=options, firefox_profile=profile)
                driver.set_window_size(random.randint(500,1000), random.randint(500,1000))
                driver.set_page_load_timeout(15)

                print("Worker",id,"Agent:",driver.execute_script("return navigator.userAgent"))
                time.sleep(random.random()*5)
                query_url = self.url.format(job)
                print("Worker",id,"Query",query_url)
                driver.get(query_url)
                raw_source = driver.page_source
                driver.quit()
                del driver
                print("Worker",id,"Response:")
                print(datetime.now().time().strftime("%H:%M:%S"))
                f = HTMLFilter()
                f.feed(raw_source)
                print(f.text)
                processed = f.text
                print("Worker",id,"RECV",len(raw_source))
                return processed

            except KeyboardInterrupt:
                exit()
            except Exception as e:
                count +=1
                if count>3:
                    return -1,-1
                print("WOKR:",id,'ERR',str(e))
                try:
                    driver.quit()
                    del driver
                except:
                    pass
                time.sleep(reset_time)
                continue

    def worker(self,id_job,wid,output):
            print(f"{wid} worker booted")
            for i in range(len(id_job)):
                uname = id_job[i]
                result = self.search(uname,wid)

                print("YOU MAY WANT TO PROCESS RESULT HERE")
                assert 0 == 1

                des = open(self.output_file,"a")
                des.write("{}\n".format(result))
                des.close()
                print("Worker",wid,"Job", i,'/',len(id_job))
            print(f"{wid} worker ended")


    def start(self):

        allid = []
        todo = []
        done = []
        prefix = []

        print("Loading file")

        csvfile = open(self.input_file,'r')
        lines = csvfile.readlines()
        for line in lines:
            try:
                allid.append(line.strip())
            except:
                pass
        print("Data loaded,", len(allid),"found")
        csvfile.close()

        try:
            csvfile = open(self.output_file)
        except:
            csvfile = open(self.output_file,'w')
            csvfile.close()
            csvfile = open(self.output_file)

        lines = csvfile.readlines()
        for line in lines:
            try:
                row = line.split(",")
                done.append(row[1].strip())
            except:
                pass
        print("Data loaded,", len(done),"done")
        csvfile.close()

        print("Load task todo")
        for i in tqdm.tqdm(range(len(allid))):
            if allid[i] in done:
                done.remove(allid[i])
            else:
                todo.append(allid[i])

        print(len(todo),'job todo')
        todo_jobs = []
        for i in range(self.worker_count):
            todo_jobs.append([])
        for i in range(len(todo)):
            j = i%self.worker_count
            todo_jobs[j].append(todo[i])

        threading.Thread(target=vpnsel, args=(self.vpn,self.reset)).start()

        for i in range(self.worker_count):
            print(i,"worker booting")
            threading.Thread(target=self.worker, args=(todo_jobs[i], i, self.output_file)).start()
            time.sleep(0.1)
        
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Some tool to query website, automatically switch vpn')
    parser.add_argument('--config', metavar='config_file', type=str, required=True,
                        help='path to configure file.')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.loads(f.read())
        obj =  OBJ(config['url'],config['worker_count'],config['user_agents'],config['input_file'],
                    config['output_file'],config['vpn_service'],config['vpn_refresh'])

        obj.start()
