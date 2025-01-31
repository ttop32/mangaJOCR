from folder_manager import FolderManager
from download_manager import DownloaderManager
from text_segmentation import TextSegmenation
from text_detection import TextDetection
from text_ocr import TextOcr
from text_translate import TextTranslator
from text_draw import TextDraw
from ini_handler import IniHandler

import os
import pickle
from tqdm import tqdm
import time
import threading

class MangaTranslator():
    def __init__(self, url,settingValueDict):
        self.url=url
        print(settingValueDict)
        self.textSegmentation=TextSegmenation()
        self.textDetection=TextDetection(settingValueDict["ContourSize"])
        self.textOcr=TextOcr(settingValueDict["OCR"])
        self.textTranslator=TextTranslator(settingValueDict["Translator"],settingValueDict["Language"])
        self.textDraw=TextDraw(settingValueDict["FontStyle"],settingValueDict["FontSize"])
        self.folder=FolderManager()
        self.downloader=DownloaderManager()
        
        
        self.customTqdm=tqdm
        
    def processTranslation(self,):
        ###folder init and download
        if os.path.isdir(self.url):
            downloadFileList,mangaName=self.downloader.getLocalDirFileList(self.url)
        else:
            self.folder.removeDir([self.folder.downloadPath])
            downloadFileList,mangaName=self.downloader.downloadUrl(self.url)
            #downloadFileList,mangaName=self.downloader.getDownloadedFilePathList()
        
        if mangaName=="":
            print("download fail")
            return -1
        
        
        
        oriFileList=self.folder.intitFolderEnv(downloadFileList,mangaName)
        self.sendInfo(mangaName,oriFileList[0],len(oriFileList))
        self.threadCounter=0
        self.lock = threading.Lock()
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock3 = threading.Lock()
        self.lock4 = threading.Lock()
        self.lock5 = threading.Lock()
        #forloop
        #for fileName in tqdm(oriFileList): 
        #    self.processTranslationTask(fileName)
        
        #thread start
        tList=[]
        for fileName in oriFileList:
          t = threading.Thread(target=self.processTranslationTask, args=(fileName,), daemon=True).start()
          tList+=[t]
        print("progess")
        #thread progress
        for i in self.customTqdm(range(len(oriFileList))):
          while self.threadCounter<=i:
            time.sleep(0.5)
        
        
        ###save_file
        self.folder.saveFileAndRemove(mangaName)
        return 1
        
        
        
    def processTranslationTask(self,fileName):

        ###segmentation
        self.lock1.acquire()
        self.textSegmentation.segmentPage(fileName,self.folder.inpaintedFolder,self.folder.textOnlyFolder)
        self.lock1.release()
        

        ###text_detection
        textBoxList=self.textDetection.textDetect(fileName,self.folder.textOnlyFolder)
        
        
        ###text_ocr
        self.lock3.acquire()
        textList=self.textOcr.getTextFromImg(fileName,textBoxList,self.folder.textOnlyFolder)
        self.lock3.release()


        ###text_translation
        self.lock4.acquire()
        textList_trans=self.textTranslator.translate(textList)
        self.lock4.release()
        
        
        ###text_draw
        self.textDraw.drawTextToImage(fileName,textBoxList,textList_trans,self.folder.inpaintedFolder,self.folder.transalatedFolder)
        
        
        #count finish
        self.lock.acquire()
        self.threadCounter+=1
        self.lock.release()



if __name__ == "__main__":
    iniHandler=IniHandler()
    setting=iniHandler.getCurrentSetting()
    setting["Translator"]="google"
    setting["OCR"]="windowocr"
    url=""
    mangaTranslator=MangaTranslator(url,setting)
    mangaTranslator.processTranslation()
        


