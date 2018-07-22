'''
Created on Jul 20, 2018

@author: Vishruth
'''
import os
import random
from shutil import copyfile
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from builtins import staticmethod

class Video(object):
    def __init__(self, description):
        '''
        Constructor
        '''
        self.clip = None
        self.description = description
    
    @staticmethod
    def ingest_video(file_path):
        try:
            copyfile(file_path, "..\\cache\\"+os.path.basename(file_path))
            # Add file_path and file_id to DB
        except OSError as e:
            print(e.errno)
            print(os.getcwd())
            print(e.filename)
            print(e.strerror)
    
    def add_segment(self, video_segment):
        if not self.clip:
            self.clip = video_segment.get_videoclip()
        else:
            self.clip = concatenate_videoclips([self.clip, video_segment.get_videoclip()])
    
    def write_videoclip_to_file(self):
        try:
            directory = "..\\output\\"
            if not os.path.exists(directory):
                os.makedirs(directory)
            print("here")
            os.remove("..\\output\\%s.mp4" % self.description)
        except OSError:
            pass
        print("Writing to file: ..\\output\\%s.mp4" % self.description)
        self.clip.write_videofile("..\\output\\%s.mp4" % self.description)

class VideoSegment(object):
    '''
    classdocs
    '''
    def __init__(self, video_id, start_time, end_time):
        '''
        Constructor
        '''
        self.clip = VideoFileClip("..\\cache\\"+video_id+".mp4").subclip(start_time, end_time)
        self.left, self.right, self.top, self.bottom = 0, 0, 0, 0
        self.duration = end_time - start_time
        VideoSegment.colors = {
            'red': [255,0,0],
            'green': [0,255,0],
            'blue': [0,0,255]
            }
    
    @staticmethod
    def draw_rectangle(frame, left, right, top, bottom, color):
        """Draw a colored rectangle"""
        width = len(frame[0])-1
        height = len(frame)-1
        left_abs = int(left*width)
        right_abs = int(right*width)
        top_abs = int(top*height)
        bottom_abs = int(bottom*height)
        frame[top_abs, left_abs: right_abs] = color
        frame[bottom_abs, left_abs: right_abs] = color
        frame[top_abs: bottom_abs, left_abs] = color
        frame[top_abs: bottom_abs, right_abs] = color
        
        return frame
    
    def annotate_videoclip(self, left, right, top, bottom, text):
        drawing_color, drawing_color_rgb = random.choice(list(VideoSegment.colors.items()))
        textclip = TextClip(" "+text,fontsize=16,color=drawing_color).set_position((0.1,0.2), relative=True).set_duration(self.duration)
        self.clip = CompositeVideoClip([self.clip, textclip]).fl_image(
            lambda image: VideoSegment.draw_rectangle(image, left, right, top, bottom, drawing_color_rgb))
        return self.clip
    
    def get_videoclip(self):
        return self.clip