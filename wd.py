#!/usr/bin/env python

import threading, Queue
import argparse
import urllib, re, urlparse, os, sys
from bs4 import BeautifulSoup

q = Queue.Queue()
dictionary = dict()
global_depth = 0

def outsource_check_url(full_url, url):
    if full_url.split("/")[2] == url.split("/")[2]:
        return True
    else:
        return False

def is_url(string):
    check = string.split("/")
    if check[0] == "http:":
        return True
    else:
        return False

def work_thread():
    while True:
        item = q.get()
        print "Downloaded next files:", item[1]
        try:
            urllib.urlretrieve(item[0], item[1])
        except:
            print "Warning!!! Some problems with:", item[0]
            continue            
        q.task_done()

def download_next(url, depth, thread_numbers, dest):
    global global_depth
    global dictionary
    if depth > 0:
        soup = BeautifulSoup(urllib.urlopen(url))
        for i in soup.findAll('img'):
            full_url = urlparse.urljoin(url, i['src'])
            folder = full_url.split('/')[3:-1]
            f = str()
            for each in folder:
                f = f + each + "/"
            folder = f
            f_name = os.path.join(dest, i['src'])
            dictionary[full_url] = f_name            
            if not os.path.exists(folder) and folder != '':
                os.makedirs(folder)
            
        for i in soup.findAll('a', attrs={'href': re.compile('(?i)(htm|html)$')}):
            full_url = urlparse.urljoin(url, i['href'])
            if outsource_check_url(full_url, url) != True:
                continue
            folder = full_url.split('/')[3:-1]
            f = str()
            for each in folder:
                f = f + each + "/"
            folder = f
            if is_url(i['href']):
                i['href'] = i['href'].split('/')[3:]
                it = str()
                for each in i['href']:
                    it = it + "/" + each
                i['href'] = it[1:]
            f_name = os.path.join(dest, i['href'])
            dictionary[full_url] = f_name
            if not os.path.exists(folder) and folder != '':
                os.makedirs(folder)
            download_next(full_url, depth - 1, thread_numbers, folder)
            
        if global_depth == depth + 1:
            for each in range(thread_numbers):
                thread = threading.Thread(target = work_thread)
                thread.daemon = True
                thread.start()
            for key, value in dictionary.iteritems():
                arglist = list()
                arglist.append(key)
                arglist.append(value)
                q.put(arglist)
            q.join()
        
def download_html(url, depth, thread, dest):
    f_name = str(url).split(".")
    urllib.urlretrieve(url, dest + f_name[1] + ".html")
    global global_depth 
    global_depth = depth
    if depth > 1:
        download_next(url, depth - 1, thread, dest)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("URL", type = str, help = "Name of website")
    parser.add_argument("-d", dest = "depth_download", help = "Depth download of website")
    parser.add_argument("-t", dest = "thread", help = "Number of threads")
    parser.add_argument("-o", dest = "folder_name", help = "The directory in which the website will be downloaded")
    args = parser.parse_args()

    depth = 3
    thread = 5
    d_name = ""
    try:
        if args.depth_download != None:
            depth = int(args.depth_download)
        if args.thread != None:
            thread = int(args.thread)
    except:
        print "Bad arguments"
        sys.exit()
    try:
        if args.folder_name != None:
            d_name = args.folder_name    
    except:
        print "Directory doesn't exist"
        sys.exit()
    print "Proccessing...."
    download_html(args.URL, depth, thread, d_name)    
    print "All done"
    
if __name__ == '__main__':
    status = main()