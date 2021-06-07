# JALANIN INI
# apk add --no-cache gcc python3-dev jpeg-dev zlib-dev
# apk add --no-cache --virtual .build-deps build-base linux-headers
# pip install Pillow

import socket as sk
from socket import *
import os
import sys
import hashlib
import time
import datetime
import concurrent.futures
import threading
import multiprocessing as mp
from PIL import Image, ImageFilter



os.system('cls' if os.name == 'nt' else 'clear')

# Variabel UDP
host = "" # 
serverPort = 10000 
clientPort = 10001 
buffer = 1024 
data = "" # Data dari client
filePath = os.getcwd()+ "/img" # Path gambar
logDict = {} # Dict untuk log

# Command aplikasi
LIST = "LIST" # Request daftar file
FILE = "FILE" # Request file yang akan dikirim 
NACK = "NACK" # ACK Negatif
PACK =  "PACK" # ACK Positif
CHECK = "CHECK" # Mengirimkan checksum ke client
PROCESS = "PROCESS" # process imageFilter

# mencari IP server
host = sk.gethostbyname(sk.gethostname())

# Membuat folder apabila kosong
if not os.path.exists(filePath):
    os.mkdir(filePath) 

# Binding ke port
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((host,serverPort))

clientAddr = (host,clientPort)

def listen():
    'Server menunggu client dan menerima koneksi'

    try:
        data,clientAddr = serverSocket.recvfrom(buffer)
    except ConnectionResetError:
        print("Koneksi dengan client hilang")
        listen()
    print("Terhubung dengan client - ip:", clientAddr[0], " pada port ", clientAddr[1])
    data = data.decode("utf-8").strip()
    if data == LIST:
        sendList()
        listen()
    elif data == PROCESS:
        process()
        listen()
    elif data[:4] == FILE:
        data = data[5:].strip()
        sendFile(filePath + "/"+data)
        listen()
    elif data[:4] == NACK:
        print("File tidak diterima oleh client")
        currentTime = datetime.datetime.now()
        # Mencatat pada log
        putToLog(currentTime.strftime("%Y-%m-%d %H:%M"), clientAddr, data[4:].strip(),"FAILED")

        # Mengirimkan data kembali ke client
        print("Mengirimkan kembali data ke client")
        sendFile(data[4:].strip())
        listen()
    elif data[:4] == PACK:
        print("File telah diterima oleh client")
        currentTime = datetime.datetime.now()
        # Mencatat pada log
        putToLog(currentTime.strftime("%Y-%m-%d %H:%M"), clientAddr, data[4:].strip(),"SUCCESS")
        listen()
    else:
        # Perintah tidak ada yang sesuai
        listen() 
    return

def sendList():
    'Mengirimkan daftar file kepada server'
    filesList = [] # Daftar file pada server
    
    for root, dirs, files in os.walk(filePath):
        for file in files:
            relPath = os.path.relpath(root, filePath)
            filesList.append(os.path.join(relPath,file))
            
    allFiles = ""
    # Mengubah list menjadi string
    for item in filesList:
        allFiles += item + "\t"

    # Mengirimkan string tersebut kepada client
    serverSocket.sendto(allFiles.encode("utf-8"), clientAddr)
    print("Daftar file berhasil dikirimkan")
    return

def sendFile(fileName):
    'Mengirim file kembali kepada client'
    
    # Membaca dan memeriksa file dalam bentuk bytes
    if not os.path.exists(fileName):
        print("File yang direquest salah")
        serverSocket.sendto("File salah.".encode("utf-8"), clientAddr)
        return
    checkSum = hashlib.md5(open(fileName,"rb").read()).hexdigest()
    time.sleep(0.5)

    file = open(fileName, "rb")

    # Mengirim checksum ke client
    checkSum = CHECK + " " + checkSum
    serverSocket.sendto(checkSum.encode("utf-8"), clientAddr)

    print("Checksum telah terkirim ke - ip: ", clientAddr[0], " dan port ", clientAddr[1])

    fileSize = int(os.path.getsize(fileName))
    count = int(fileSize/buffer)+1

    print("Mengirim: ", fileName)
    time.sleep(0.5)
    while(count != 0) :
        fileData = file.read(buffer)
        serverSocket.sendto(fileData, clientAddr)
        time.sleep(0.02)
        count -= 1
    print("File telah terkirim")

    file.close() 
    time.sleep(0.5)

def putToLog(curDTime, cAddr, fName, message):
    "Menyimpan log pada server"
    tempList = [cAddr,fName, message]
    logDict[curDTime] = tempList 
    print(logDict)

def getImage():
    "Menyimpan daftar gambar pada list"
    filesList = []
    for root, dirs, files in os.walk(filePath):
        if(root is filePath):
            for file in files:
                filesList.append(os.path.join(filePath,file))
    return filesList

def process_image(process, img_name):
    "Proses blur gambar"
    size = (100, 100)
    path, file_name = os.path.split(img_name)
    img = Image.open(img_name)

    # Filter gambar dengan gaussian blur
    img = img.filter(ImageFilter.GaussianBlur(15))

    img.thumbnail(size)
    img.save(f"img/{process}/proses-{file_name}")
    print(f'{file_name} telah difilter')

def helperMultiprocessing(x):
    return process_image("multiprocessing", x)

def helperMultiprocessingAsync(x):
    return process_image("multiprocessing-async", x)

def helperMultithreading(x):
    return process_image("multithreading", x)

def helperMultithreadingAsync(x):
    return process_image("multithreading-async", x)

def multiprocessingAsync():
    "Image processing dengan multiprocessing asynchronous"

    if not os.path.exists(os.path.join(filePath,"multiprocessing-async")):
        os.mkdir(os.path.join(filePath,"multiprocessing-async")) 

    listImage = getImage()
    t1 = time.perf_counter()
    # multiprocessing async
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(helperMultiprocessingAsync, listImage)
    t2 = time.perf_counter()

    total_time = t2-t1
    return total_time

def multiprocessing():
    "Image processing dengan multiprocessing"

    if not os.path.exists(os.path.join(filePath,"multiprocessing")):
        os.mkdir(os.path.join(filePath,"multiprocessing")) 
    
    listImage = getImage()
    t1 = time.perf_counter()
    
    listProcess = []
    # multiprocessing 
    for i in listImage:
        p = mp.Process(target=helperMultiprocessing, args=(i,))
        p.start()
        listProcess.append(p)
    
    for process in listProcess:
        process.join()

    t2 = time.perf_counter()

    total_time = t2-t1
    return total_time

def multithreadingAsync():
    "Image processing dengan multithreading asynchronous"

    if not os.path.exists(os.path.join(filePath,"multithreading-async")):
        os.mkdir(os.path.join(filePath,"multithreading-async")) 

    listImage = getImage()
    t1 = time.perf_counter()
    # multithreading async
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(helperMultithreadingAsync, listImage)
    t2 = time.perf_counter()

    total_time = t2-t1
    return total_time

def multithreading():
    "Image processing dengan multithreading"

    if not os.path.exists(os.path.join(filePath,"multithreading")):
        os.mkdir(os.path.join(filePath,"multithreading")) 

    listImage = getImage()
    t1 = time.perf_counter()
    
    listThread = []

    # multithreading
    for i in listImage:
        t = threading.Thread(target=helperMultithreading, args=(i,))
        t.start()
        listThread.append(t)
            
    for thread in listThread:
        thread.join()

    t2 = time.perf_counter()

    total_time = t2-t1
    return total_time
    
def process():
    "Menghitung waktu proses filter"

    time_multiprocess = multiprocessing()
    time_multiprocess_async = multiprocessingAsync()
    time_multithread = multithreading()
    time_multithread_async = multithreadingAsync()

    print(f"Waktu multiprocessing: {time_multiprocess}")
    print(f"Waktu multithreading: {time_multithread}")
    print(f"Waktu multiprocessing asynchronous: {time_multiprocess_async}")
    print(f"Waktu multithreading asynchronous: {time_multithread_async}")

    total = str(time_multiprocess) + "\t" + str(time_multithread) + "\t" + str(time_multiprocess_async) + "\t" + str(time_multithread_async)
    
    print("Mengirimkan waktu proses ke - ip: ",clientAddr[0], " pada port ", clientAddr[1])
    serverSocket.sendto(str(total).encode("utf-8"), clientAddr)
    return

# Menjalankan server
listen()