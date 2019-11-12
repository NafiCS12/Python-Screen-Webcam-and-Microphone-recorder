import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os

import PIL.Image
from PIL import ImageTk
from PIL import Image
from PIL import ImageGrab
import numpy as np


class VideoRecorder():
    
    
    # Video class based on openCV 
    def __init__(self):
        
        self.open = True
        self.device_index = 0
        self.fps = 5.0              
        self.frameSize = (1366,768) 
        self.video_filename = "temp_video52.avi"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_out = cv2.VideoWriter(self.video_filename, cv2.VideoWriter_fourcc(*'XVID'), self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()
    
    # Video starts being recorded 
    def record(self):
        
        counter = 1
        timer_start = time.time()
        
        timer_current = 0
        
        def rescale_frame(frame, percent=75):
            width = int(frame.shape[1] * percent/ 100)
            height = int(frame.shape[0] * percent/ 100)
            dim = (width, height)
            return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


        
        while(self.open==True):
            ret, video_frame = self.video_cap.read()
            if (ret==True):


                img = ImageGrab.grab()
                frameWebCam = rescale_frame(video_frame, percent=50)
                img_np = np.array(img)
                frameScreen = cv2.cvtColor(img_np,cv2.COLOR_BGR2RGB)
                #frameScreen = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

                self.video_out.write(frameScreen)

                cv2.imshow("frame",frameWebCam) #Displays an image in the specified window.

                                        
                   #print str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current)
                self.frame_counts += 1
                   #counter += 1
                   #timer_current = time.time() - timer_start
                
                # time.sleep(0.16)
           

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
                            
                # 0.16 delay -> 6 fps
                # 
                

    # Finishes the video recording therefore the thread too
    def stop(self):
        
        if self.open==True:
            
            self.open=False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()
            
        else: 
            pass


    # Launches the video recording function using a thread          
    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()





class AudioRecorder():
    

    # Audio class based on pyAudio and Wave
    def __init__(self):
        
        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio52.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []


    # Audio starts being recorded
    def record(self):
        
        self.stream.start_stream()
        while(self.open == True):
            data = self.stream.read(self.frames_per_buffer) 
            self.audio_frames.append(data)
            if self.open==False:
                break
        
            
    # Finishes the audio recording therefore the thread too    
    def stop(self):
       
        if self.open==True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
               
            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()
        
        pass
    
    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


    


def start_AVrecording(filename):
                
    global video_thread
    global audio_thread
    
    video_thread = VideoRecorder()
    audio_thread = AudioRecorder()

    audio_thread.start()
    video_thread.start()

    return filename




def start_video_recording(filename):
                
    global video_thread
    
    video_thread = VideoRecorder()
    video_thread.start()

    return filename
    

def start_audio_recording(filename):
                
    global audio_thread
    
    audio_thread = AudioRecorder()
    audio_thread.start()

    return filename




def stop_AVrecording(filename):
    
    audio_thread.stop() 
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print ( "total frames " + str(frame_counts) )
    print ( "elapsed time " + str(elapsed_time) )
    print ( "recorded fps " + str(recorded_fps) )
    video_thread.stop() 

    print ( '\n check audio and video files first' )


    # Makes sure the threads have finished
    while threading.active_count() > 1:
        time.sleep(1)

    cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio52.wav -i temp_video52.avi -pix_fmt yuv420p " + filename + ".avi"
    subprocess.call(cmd, shell=True)

    print (' Merging audio and video signal ended  ')



#Required and wanted processing of final files
def file_manager(filename):

    local_path = os.getcwd()

    if os.path.exists(str(local_path) + "/temp_audio52.wav"):
        os.remove(str(local_path) + "/temp_audio52.wav")
    
    if os.path.exists(str(local_path) + "/temp_video52.avi"):
        os.remove(str(local_path) + "/temp_video52.avi")

    if os.path.exists(str(local_path) + "/temp_video2.avi"):
        os.remove(str(local_path) + "/temp_video2.avi")

    if os.path.exists(str(local_path) + "/" + filename + ".avi"):
        os.remove(str(local_path) + "/" + filename + ".avi")
    
    

    
if __name__== "__main__":
    
    filename = "demo"   
    file_manager(filename)
    
    start_AVrecording(filename)  
    
    time.sleep(10)
    
    stop_AVrecording(filename)
    print ("Done")



##
