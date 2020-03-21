import urllib
import sys
import json
import os
import traceback
import time
import requests

json_file_name = sys.argv[1]
absolute_path = os.path.dirname(os.path.abspath(__file__))
download_directory = '/media/kevin/3AE1A2A77B72C361/skillshare_downloads'

with open(os.path.join(absolute_path, json_file_name), 'r+') as json_file:
    json_data = json.loads(json_file.read())



def repairFilename(filename):
    '''
    Filenames are problematic, Windows, Linux and macOS don't
    allow certain characters. This (mess) fixes that. Basically 
    every other character, no matter how obscure, is seemingly
    supported though.
    '''

    if u"/" in filename:
        filename = filename.replace(u"/", u"-")
    if u"\\" in filename:
        filename = filename.replace(u"\\", u"-")
    if u"|" in filename:
        filename = filename.replace(u"|", u"-")
    if u":" in filename:
        filename = filename.replace(u":", u"-")
    if u"?" in filename:
        filename = filename.replace(u"?", u"-")
    if u"<" in filename:
        filename = filename.replace(u"<", u"-")
    if u">" in filename:
        filename = filename.replace(u">", u"-")
    if u'"' in filename:
        filename = filename.replace(u'"', u"-")
    if u"*" in filename:
        filename = filename.replace(u"*", u"-")
    if u"..." in filename:
        filename = filename.replace(u"...", u"---")

    return filename



def makeDirectoryForCourse(course_title):
	os.chdir(download_directory)
	course_title = repairFilename(course_title)
	if "/" in course_title:
		course_title.replace("/","-")
	if not os.path.exists(course_title):
		os.makedirs(course_title)
		os.chdir(course_title)
	else:
		os.chdir(course_title)


makeDirectoryForCourse(json_data['course_title'])
print('Downloading Course: ' + json_data['course_title'])
video_links = json_data['video_links']
video_titles = json_data['title_lists']

for index in range(len(video_links)):
    filename = repairFilename(video_titles[index]) + ".mp4"
    not_succeed = True
    while not_succeed:
        print('Downloading {} ...'.format(filename))
        try:
            urllib.request.urlretrieve(video_links[index], str(index) + " - " + filename)
            not_succeed = False
        except Exception as error:
            print('Error while downloading {} . trying again 5 seconds...'.format(filename))
            traceback.print_exc()
            time.sleep(5)
            
with open('done', 'w+') as msgs:
    msgs.write('Enjoy...')
# os.remove(json_file_name)