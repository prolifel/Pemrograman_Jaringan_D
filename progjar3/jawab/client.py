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

SERVER_NAME = "INS"

serverIp = "127.0.1.1"

host = "" # IP Client
clientPort = 10001 # Port Client
serverAddr = None
buffer = 1024
data = ""
filePath = os.getcwd()+ "/ClientFiles" # Path file client
saveToFile = "" # filename from server to save
COUNTER = 0 # Menghitung percobaan unduh
SENDFILE = "" # Daftar file yang ingin diunduh

# Daftar perintah
LIST = "LIST" # Request daftar file
FILE = "FILE" # Request file yang akan dikirim 
NACK = "NACK" # ACK Positif
PACK =  "PACK" # ACK Negatif
CHECK = "CHECK" # Checksum dari server

# Ambil IP dari server
host = sk.gethostbyname(sk.gethostname())

# Membuat socket server
clientSocket = None
def initSocket():
   "Inisialisasi koneksi dengan server"
   global clientSocket
   global serverAddr
   global serverIp
   serverAddr = (serverIp,10000)
   clientSocket = None # definisi ulang
   clientSocket = socket(AF_INET, SOCK_DGRAM)
   clientSocket.bind((host,clientPort))
initSocket()

# Apabila folder filePath belum ada, maka buat folder tersebut
if not os.path.exists(filePath):
   os.mkdir(filePath)

def listenForList():
   'Mengambil list daftar file dari server'
  
   global serverAddr
   clientSocket.sendto("LIST".encode("utf-8"), serverAddr)
   data, serverAddr = clientSocket.recvfrom(buffer)
   time.sleep(0.5)

   os.system('cls' if os.name == 'nt' else 'clear')
   allFiles = data.decode("utf-8").strip() # Mengubah data dalam bentuk string
   filesList = list(allFiles.split("\t"))
   time.sleep(0.5)

   print("\n\n=========== File pada Server ===========\n")
   count = 0
   for item in filesList:
      time.sleep(0.1)
      if item.strip() != "":
         count += 1
         print(f'\t{count}. {item}\n')
   if count == 0:
      print("\tTidak terdapat file pada server")
      return
   time.sleep(0.5)

   print("======================")
   print("Masukkan nama file yang ingin diunduh.\n")
   time.sleep(0.5)
   print("Contoh: './gambar.png' (tanpa petik)\n")
   sendFile = input("Nama File > ")
   global SENDFILE
   SENDFILE = sendFile # ACK nama file
   saveToFile = filePath+os.sep+sendFile.split('/')[-1]
   print(saveToFile)
   print("Melakukan request unduh pada server....")
   sendFile = "FILE "+ sendFile
   clientSocket.sendto(sendFile.encode("utf-8"), serverAddr)

   # Melakukan listen pada file
   listenForFile(saveToFile)
   return

def listenForFile(fileName):
   'Listen pada file dan mengunduh file'
   fileName = fileName.replace('/','/')
   global serverAddr
   data = None
   try:
      global clientSocket
      global serverAddr
      clientSocket.settimeout(2)
      data, serverAddr = clientSocket.recvfrom(buffer)
   except timeout:
      print("Server sedang sibuk dan timed out. Silakan coba kembali.")
      return

   response = data.decode("utf-8")
   rchecksum = ""
   # Kalau checksum yang diterima berbeda
   if response[:5] == CHECK:
      rchecksum = response[5:].strip()
      time.sleep(0.5)
   else:
      time.sleep(0.5)
      print("Respon server -", response)
      return
   
   print("Checksum diterima")

   file = None
   fileData = None
   try:
      global serverSocket
      clientSocket.settimeout(2)
      fileData, serverAddr = clientSocket.recvfrom(buffer)
      file = open(fileName, "wb+") # Membuat file
   except timeout:
      print("Server sedang sibuk dan timed out. Silakan coba kembali.")
      time.sleep(0.5)
      return
   print("Mengunduh ", fileName+"...")
   try:
      while True:
         file.write(fileData)
         clientSocket.settimeout(2)
         fileData, serverAddr = clientSocket.recvfrom(buffer)
   except timeout:
      file.close()

   # Membuat checksum untuk memeriksa integritas file
   checkSum = hashlib.md5(open(fileName, "rb").read()).hexdigest()
   if rchecksum == checkSum:
      global COUNTER
      COUNTER = 0 # Merubah counter menuju 0
      time.sleep(0.5)
      print("Berhasil mengunduh! - File berukuran ",os.path.getsize(fileName))
      pack = PACK + " " + SENDFILE
      clientSocket.sendto(pack.encode("utf-8"), serverAddr)
      time.sleep(0.5)
   else:
      print("Checksum tidak sesuai..")
      return
      os.remove(fileName)
      print("Terjadi masalah pada server. File gagal diunduh!")
      time.sleep(0.5)
      if(COUNTER < 5):
         COUNTER += 1
         print("Mencoba kembali...")
         time.sleep(0.5)
         nack = NACK + " " + SENDFILE
         clientSocket.sendto(nack.encode("utf-8"), serverAddr)
         listenForFile(fileName) # Mencoba mengunduh kembali

def menu():
   'Menu pada user'
   while True:
      time.sleep(0.5)
      print("\n=========== Masukkan Perintah ===========")
      print("Ketik 'daftar' untuk melihat daftar file pada server")
      print("Ketik 'proses' untuk melakukan image processing")
      print("Ketik 'keluar' untuk menutup aplikasi\n")
      time.sleep(0.5)
      command = input("Perintah > ")
      if command == "daftar":
         listenForList()
      elif command == "proses":
         process()
      elif command == "keluar":
         closeApp()
      else:
         print("Perintah > Tidak ada perintah")
         continue

def closeApp():
   "Menutup aplikasi"
   time.sleep(0.5)
   os.system('cls' if os.name == 'nt' else 'clear')
   print("Aplikasi akan ditutup. Menutup koneksi dengan server.")
   clientSocket.close() # Menutup socket
   sys.exit() # Keluar menuju ke sistem

def process():
   'Melakukan image processing pada server'
   global serverAddr
   try:
      clientSocket.sendto("PROCESS".encode("utf-8"), serverAddr)
   except Exception:
      print("Koneksi ke server gagal")
      clientSocket.close() # Menutup socket
      initSocket() # Membuka socket
      return
   print("Menuggu server selesai memproses gambar.")
   data, serverAddr = clientSocket.recvfrom(buffer)
   time.sleep(0.5)
   totalTime = data.decode("utf-8").strip()
   totalTime = totalTime.split("\t")
   print("Waktu image processing dengan multiprocessing adalah: ", totalTime[0], " seconds")
   print("Waktu image processing dengan multithreading adalah: ", totalTime[1], " seconds")
   print("Waktu image processing dengan multiprocessing asynchronous adalah: ", totalTime[2], " seconds")
   print("Waktu image processing dengan multithreading asynchronous adalah: ", totalTime[3], " seconds")
   return

# Menampilkan menu
menu()