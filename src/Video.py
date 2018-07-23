'''
Created on Jul 20, 2018

@author: Vishruth
'''
import os
from shutil import copyfile
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips    

def close_clip(clip):
    if not clip or not isinstance(clip, VideoFileClip):
        return
    try:
        if clip.reader != None:
            clip.reader.close()
        del clip.reader
        if clip.audio != None:
                clip.audio.reader.close_proc()
                del clip.audio
        del clip
    except Exception as e:
        print(e)

class Video(object):
    def __init__(self, description):
        '''
        Constructor
        '''
        self.clip = None
        self.description = description
    
    def __del__(self):
        '''
        Destructor
        '''
        close_clip(self.clip)
    
    @staticmethod
    def ingest_video(file_path):
        try:
            # Copy file to the cache directory (one level above current)
            destination_path = os.path.join("..", "cache", os.path.basename(file_path))
            copyfile(file_path, destination_path)
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
        if not self.clip:
            print("Clip empty, video not written")
            return
        try:
            directory = os.path.join("..", "output")
            if not os.path.exists(directory):
                os.makedirs(directory)
            output_filename = "%s.mp4" % self.description
            os.remove(os.path.join("..", "output", output_filename))
        except OSError:
            pass
        try:
            output_filename = "%s.mp4" % self.description
            output_filepath = os.path.join("..", "output", output_filename)
            print("Writing to file: %s" % output_filepath)
            self.clip.write_videofile(output_filepath)
        except OSError as e:
            print(e.errno)
            print(os.getcwd())
            print(e.filename)
            print(e.strerror)
            print("Error writing to file")

class VideoSegment(object):
    '''
    classdocs
    '''
    def __init__(self, video_id, start_time, end_time):
        '''
        Constructor
        '''
        video_path = os.path.join("..", "cache", "%s.mp4" % video_id)
        self.clip = None
        self.clip = VideoFileClip(video_path).subclip(start_time, end_time)
        self.left, self.right, self.top, self.bottom = 0, 0, 0, 0
        self.duration = end_time - start_time
    
    def __del__(self):
        '''
        Destructor
        '''
        close_clip(self.clip)
    
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
    
    def annotate_videoclip(self, left, right, top, bottom, text, color, color_rgb):
        textclip = TextClip(" "+text,fontsize=16,color=color).set_position((left, top), relative=True).set_duration(self.duration)
        old_clip = self.clip
        self.clip = CompositeVideoClip([self.clip, textclip]).fl_image(
            lambda image: VideoSegment.draw_rectangle(image, left, right, top, bottom, color_rgb))
        close_clip(old_clip)
        return self.clip
    
    def annotate_videoclip_at_time(self, timestamp, left, right, top, bottom, text, color, color_rgb):
        if timestamp+1 < self.clip.duration:
            textclip = TextClip(" "+text,fontsize=16,color=color).set_position((left, top), relative=True).set_duration(1).set_start(0)
            old_clip = self.clip
            clip_so_far = self.clip.subclip(0, timestamp)
            clip_to_annotate = self.clip.subclip(timestamp, timestamp+1)
            clip_after = self.clip.subclip(timestamp+1, self.clip.duration)
            annotated_clip = CompositeVideoClip([clip_to_annotate, textclip]).fl_image(
                lambda image: VideoSegment.draw_rectangle(image, left, right, top, bottom, color_rgb))
            self.clip = concatenate_videoclips([clip_so_far, clip_to_annotate, clip_after])
            close_clip(clip_so_far)
            close_clip(clip_to_annotate)
            close_clip(clip_after)
            close_clip(annotated_clip)
            close_clip(old_clip)
        return self.clip
    
    def get_videoclip(self):
        return self.clip