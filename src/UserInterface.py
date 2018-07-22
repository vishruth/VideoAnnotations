#!/usr/local/bin/python2.7
# encoding: utf-8
from src.Database import Database
from src.Video import VideoSegment, Video
import os
import random
from pprint import pprint

NUM_ARGS_PER_CSV_LINE = 8

colors = {
        'red': [255,0,0],
        'green': [0,255,0],
        'blue': [0,0,255]
        }

def menu():
    '''
    Prints the menu and returns the user's choice.
    '''
    while True:
        print("Enter the number corresponding to the desired option:")
        print("[1] Ingest video")
        print("[2] List videos")
        print("[3] Search by objects")
        print("[4] Search by time")
        print("[5] Clear database")
        print("[6] Exit")
        
        try:
            choice = int(input("Make your selection: "))
            if choice < 1 or choice > 6:
                raise ValueError
            else:
                break
        except ValueError:
            print("That was not a valid option.")

    return choice

def main():
    selector = {
        1: ingest_video,
        2: list_videos,
        3: search_by_objects,
        4: search_by_time,
        5: clear_database,
        6: quit_program
    }
    
    while True:
        choice = menu()
        choice_func = selector.get(choice, lambda: "Invalid choice")
        choice_func()
        input("Press Enter to continue...")
        
def ingest_video():
    '''
    Takes in a path to a video and its corresponding annotation file.
    Stores the relevant annotation info in the database.
    '''
    while True:
        try:
            video_path = input("Enter the path to the video to be ingested: ")
            if not os.path.exists(video_path):
                raise ValueError
            else:
                print("Ingesting video...")
                Video.ingest_video(video_path)
                annotation_path = os.path.splitext(video_path)[0] + ".csv"
                if not os.path.exists(annotation_path):
                    raise ValueError
                else:
                    with open(annotation_path) as file:
                        print("Parsing annotation file...")
                        for line in file:
                            args = line.strip().split(',')
                            if len(args) == NUM_ARGS_PER_CSV_LINE:
                                video_name = os.path.basename(video_path)
                                video_id = os.path.splitext(video_name)[0]
                                timestamp_ms, class_name, object_id, object_presence, xmin, xmax, ymin, ymax =\
                                int(args[0]), args[1], args[2], args[3], args[4], args[5], args[6], args[7] 
                                Database.add_document_to_db(video_id, timestamp_ms, class_name, object_id, object_presence, xmin, xmax, ymin, ymax)
                            else:
                                print("Line %s was invalid" % line)
                                raise ValueError
                    break
        except ValueError:
            print("That was not a valid option.")

def list_videos():
    '''
    Prints the names of all videos that have previously been ingested into the system.
    '''
    # List all unique video_id values from the database.
    all_videos = Database.list_all_video_ids()
    if not all_videos:
        print("No videos ingested so far.")
    else:
        print("%d videos were found:" % len(all_videos))
        for video_id in all_videos:
            print(video_id)
    
def search_by_objects():
    '''
    Compiles all video segments for a given object.
    Allows the user to choose to see the raw compilation or the annotated version.
    '''
    print("Searching by objects")
    while True:
        try:
            videos_dict = {}
            previous_annotation_text = ""
            class_name = input("Object to search for: ")
            all_segments = Database.get_all_segments_for_object(class_name)
            if all_segments:
                output_video = Video("Search_%s" % class_name)
                for segment in all_segments:
                    video_id = segment["video_id"]
                    start_time = int(segment["timestamp_ms"])/1000 # in seconds.
                    end_time = start_time + 1
                    if (video_id, start_time, end_time) in videos_dict.keys():
                        video_segment = videos_dict[(video_id, start_time, end_time)]
                    else:
                        video_segment = VideoSegment(video_id, start_time, end_time)
                        videos_dict[(video_id, start_time, end_time)] = video_segment
                    
                    left, right, top, bottom = float(segment["xmin"]), float(segment["xmax"]), float(segment["ymin"]), float(segment["ymax"])
                    annotation_text = segment["class_name"] + segment["object_id"]
                    
                    # If the object is not the same as before, choose a new annotation color at random.
                    if annotation_text != previous_annotation_text:
                        previous_annotation_text = annotation_text
                        color, color_rgb = random.choice(list(colors.items()))
                    
                    video_segment.annotate_videoclip(left, right, top, bottom, annotation_text, color, color_rgb)
                    output_video.add_segment(video_segment)
                output_video.write_videoclip_to_file()
                break
            else:
                raise ValueError
                
        except ValueError as e:
            print("That was not a valid option.")
            print(e)

    quit_program()
    
def search_by_time():
    '''
    Returns a video segment for a given video ID and time range.
    Allows the user to choose to see the raw video or the annotated version.
    '''
    print("Searching a video by time")
    while True:
        try:
            video_id = input("Video ID to search for: ")
            if video_id not in Database.list_all_video_ids():
                raise ValueError
            else:
                start_time = input("Start time in ms: ")
                start_time = int(start_time)/1000 # In seconds
                end_time = input("End time in ms: ")
                end_time = int(end_time)/1000 # In seconds
                output_video = Video("Search_%s_%d-%d" % (video_id, start_time, end_time))
                previous_annotation_text = ""
                video_segment = VideoSegment(video_id, start_time, end_time)
                all_segments = Database.get_all_segments_by_time(video_id, start_time, end_time)
                if all_segments:
                    for segment in all_segments:
                        pprint(segment)
                        left, right, top, bottom = float(segment["xmin"]), float(segment["xmax"]), float(segment["ymin"]), float(segment["ymax"])
                        annotation_text = segment["class_name"] + segment["object_id"]
                        
                        # If the object is not the same as before, choose a new annotation color at random.
                        if annotation_text != previous_annotation_text:
                            previous_annotation_text = annotation_text
                            color, color_rgb = random.choice(list(colors.items()))
                        
                        relative_start_time = int(segment["timestamp_ms"])/1000 - start_time
                        video_segment.annotate_videoclip_at_time(relative_start_time, left, right, top, bottom, annotation_text, color, color_rgb)
                        
                    output_video.add_segment(video_segment)
                    output_video.write_videoclip_to_file()
                    break
                else:
                    raise ValueError
            
        except ValueError as e:
                print("That was not a valid option.")
                print(e)
        
    quit_program()

def clear_database():
    '''
    Drops the collection for all annotations.
    '''
    if Database.clear_all_documents_from_db():
        print("Successfully cleared the database")
    else:
        print("Failed to clear the database")

def quit_program():
    print("Quitting gracefully")
    quit()

if __name__ == '__main__':
    main()