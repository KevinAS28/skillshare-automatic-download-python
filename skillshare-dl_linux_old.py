import os
import time
import json
import urllib
import requests
from pathlib import Path, PureWindowsPath
from selenium import webdriver, common
from browsermobproxy import Server
from threading import Thread
import traceback
import sys

max_course_download = 3 #maximum course download in a time.
download_to = "/media/kevin/3AE1A2A77B72C361/skillshare"
absolute_path = os.path.dirname(os.path.abspath(__file__))

#Open a Chrome windows controlled by selenium
def initializeChrome():
	global driver
	global server
	global proxy
	dict={'port':8090}

	server = Server(path="./binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy", options=dict)
	server.start()
	proxy = server.create_proxy()
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
	chrome_options.add_argument("--ignore-certificate-errors")

	driver = webdriver.Chrome(str(Path("./binaries/chromedriver").absolute()), options = chrome_options)
	print('initialized Chrome window!')

'''
Navigate to the login page.
Sometimes it throws you back to the homepage for teachers
without even logging you in. That's what the alternative_login function is for
'''
def login(username, password):
	# print('Attempting to log in...')
	# driver.get('https://skillshare.com/login')
	# email_field = driver.find_element_by_name('LoginForm[email]')
	# email_field.send_keys(username)
	# password_field = driver.find_element_by_name('LoginForm[password]')
	# password_field.send_keys(password)
	# remember_me_checkbox = driver.find_element_by_css_selector('#login-form-remember-me')
	# remember_me_checkbox.click()
	# submit_login_button = driver.find_element_by_xpath('//*[@id="page-wrapper"]/div[1]/div/form/form/input[1]')
	# #submit_login_button = driver.find_element_by_css_selector('#page-wrapper > div.center-page > div > form > form > input.button.large.full-width.btn-login-submit.initialized')
	# submit_login_button.click()
	# time.sleep(2)
	input("Already login?")
	driver.get('https://skillshare.com/home')
	currentUrl = driver.current_url
	print("Current URL: " + currentUrl)
	
	if currentUrl != 'https://www.skillshare.com/home':
		print("Current URL is {}\nand NOT {}!\nTrying to log in again...".format(currentUrl, 'https://skillshare.come/home'))
		alternative_login(username, password)

def alternative_login(username, password):
	driver.get('https://skillshare.com')
	sign_in_homepage_button = driver.find_element_by_css_selector('#site-content > div.site-header.transparent.js-site-header-container > div.site-header-nav.site-header-nav-right > div.nav-items.js-nav-items-transparent > div:nth-child(3) > a')
	sign_in_homepage_button.click()
	email_field = driver.find_element_by_name('LoginForm[email]')
	email_field.send_keys(username)
	password_field = driver.find_element_by_name('LoginForm[password]')
	password_field.send_keys(password)
	remember_me_checkbox = driver.find_element_by_css_selector('#login-form-remember-me')
	remember_me_checkbox.click()
	submit_login_button = driver.find_element_by_css_selector('#abstract-popup-view > div > div.signup-login-column > div.login-wrapper > div.login-form-wrapper.form-wrapper > form > input.button.large.full-width.btn-login-submit')
	submit_login_button.click()

def get_number_of_videos():
	all_videos = driver.find_element_by_xpath('//*[@id="video-region"]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/ul/li/ul')
	videos = all_videos.find_elements_by_tag_name("li")
	number_of_videos = len(videos)
	titles_list = []
	loop_index = 0
	for item in videos:
		titles_list.append(item)
		#video-region > div > div.video-player-container.js-cd-video-player-container > div.video-player > div.video-and-playlist.video-player-layout.js-video-and-playlist-container > div.video-playlist-module.js-video-playlist-module > div > div.unit-list-wrapper > ul > li > ul > li.session-item.first > div > div.section.information > p
		text = item.find_element_by_css_selector('div > div.section.information > p')
		text = text.text
		print("Title: " + text)
		titles_list[loop_index] = text
		loop_index += 1
	return number_of_videos, titles_list

def downloadAllVideosJson(accept_value, videos_list, titles_list):
	with open('skillshare_links.txt', 'r') as file: 
		links = [link.rstrip('\n') for link in file]
		# print(links)
		# print(len(links))

	videos_list_json = []

	for index in range(len(links)):
		videos_list_json.append(index)
		#print("K:" + links[index])
		r = requests.get(
			links[index],
			headers={'Host': 'edge.api.brightcove.com',
			'Connection':'keep-alive',
			'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
			'Sec-Fetch-Mode':'cors',
			'Accept': accept_value,
			'Origin':'https://www.skillshare.com',
			'Sec-Fetch-Site':'cross-site',
			'Accept-Encoding':'gzip, deflate, br',
			'Accept-Language':'en-US,en;q=0.9'
			},
		)
		videos_list_json[index] = r.content

	return videos_list_json

def getCourseTitle():
	course_title_field = driver.find_element_by_css_selector('#video-region > div > div.video-player-container.js-cd-video-player-container > div.video-player-layout.title-container > div > div > h1')	
	course_title = course_title_field.text
	return course_title

def getVideoLinksAndTitle(videos_list_json):
	video_links = []
	video_titles = []
	#print(videos_list_json)
	for index in range(len(videos_list_json)):
		video_links.append(index)
		video_titles.append(index)
		video_json = json.loads(videos_list_json[index])
		video_links[index] = video_json['sources'][7]['src']
		#print(video_links[index])
		video_titles[index] = video_json['name']
		#print(video_titles[index])

	return video_links, video_titles

def write_links_to_file():
	command_videos_string = 'cat skillshare.log | grep -o -E "https://edge.api.brightcove.com/playback/v1/accounts/[01234567890]{1,}/videos/[0123456789]{1,}" | uniq | uniq > skillshare_links.txt'
	os.system(command_videos_string)
	command_accept_value_string = 'cat skillshare.log | grep -o -E "application/json;pk=[0123456789ABCDEFGHIJKLMNOPQRSTUVWXZYabcdefghijklmnopqrstuvwxyz-]{1,}" | uniq > skillshare_accept.txt'
	os.system(command_accept_value_string)

def get_accept_value():
	with open("skillshare_accept.txt", "r") as file:
		accept_value = file.read()
	return accept_value.strip()

def downloadVideosWithTitles(video_links, video_titles):
	for index in range(len(video_links)):
		url = video_links[index]
		filename = str(index+1) + " - " + repairFilename(video_titles[index]) + ".mp4"
		# urllib.request.urlretrieve(url, filename)
		not_succeed = True
		while not_succeed:
			try:
				print('Downloading {} ...'.format(filename))
				urllib.request.urlretrieve(url, filename)
				not_succeed = False
			
			except Exception as e:
				if (os.path.isfile(filename) == True):
					os.remove(filename)				
				print("Error while downloading {} : ".format(filename))
				traceback.print_exc()
				print('Trying in 5 seconds')
				time.sleep(5)
				print('Trying again...')


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
	os.chdir(download_to)
	course_title = repairFilename(course_title)
	if "/" in course_title:
		course_title.replace("/","-")
	if not os.path.exists(course_title):
		os.makedirs(course_title)
		os.chdir(course_title)
	else:
		os.chdir(course_title)

def cleanUp():
	to_cleanup = ["bmp.log", "server.log", "skillshare_accept.txt", "skillshare_links.txt", "skillshare_accept.txt", "skillshare.log", "done_downloaded"]
	for file in to_cleanup:
	    if os.path.isfile(file) == True:
	        os.remove(file)

def asChild(course_title, videos_list, title_lists):
	pass


def main():
	cleanUp()
	# if len(sys.argv)!=1:
	# 	json_data = sys.argv[1]
	

	home_url = "https://www.skillshare.com/home/"
	initializeChrome()
	# username = input("Please enter your E-Mail: ")
	# password = input("Please enter your password: ")
	# login(username, password)
	# logged_in_status = input("Are you logged in and on the homepage? [y/Y/n/N]: ")
	# if logged_in_status == 'y' or 'Y':
	# 	print("Logged in!")
	# else:
	# 	print("Not logged in!")
	# 	exit()

	print("Loading...")
	time.sleep(3)
	driver.get('https://skillshare.com/login')
	input("Please login, then go to the class you want to download. Press any key after you done: ")
	#driver.get(home_url)
	allpid = []
	allurl = []

	link_list = False
	index_link = 0
	with open("link_list.txt", "r+") as read_link_list:
		link_list_raw = read_link_list.read()
		if link_list_raw!="":
			link_list = [i.replace(' ', '') for i in link_list_raw.split('\n')]


	while True:
		if len([i for i in allpid if i!=None])==max_course_download:
			#wait them for finish first, then continue again
			print("Reached max class download in a time ({}). waiting them to finish first...".format(max_course_download))
			while True:
				if len([i for i in allpid if i!=None])!=max_course_download:
					break
				time.sleep(3)
			print("download class in progress: {}. continue!".format(max_course_download))

		if link_list:
			if (link_list[index_link][0]=="#"):
				print('link {} has been commented. skipping....'.format(link_list[index_link]))
				index_link+=1
				continue
			print("Link from link_list.txt: {}".format(link_list[index_link]))
			driver.get(link_list[index_link])
			index_link+=1

		if not link_list:
			print("Go to the page of the course you want to download and press a key when you're done.")
			input("Waiting for a key to be pressed... ")
			print("You pressed it!")
			print("Current URL: " + driver.current_url)

		if driver.current_url in allurl:
			print("I already work for that now... please choose another link....")
			continue

		allurl.append(driver.current_url)
		proxy.new_har("skillshare", options={'captureHeaders': True})
		driver.refresh()
		try:
			course_title = getCourseTitle()
			videos_list = []
			not_succeed = True
			while not_succeed:
				try:
					number_of_videos, titles_list = get_number_of_videos()
					not_succeed = False
				except Exception as e:
					print("Failed fetch number of videos. trying in 5 seconds...")
					time.sleep(5)
			
			for index in range(number_of_videos):
				videos_list.append(index)
				videos_list[index] = index
				index += 1
				print(index)
				video_selector_xpath = '//*[@id="video-region"]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/ul/li/ul/li[' + str(index) + ']'
				print("{} ({})".format(course_title, index))
				video_selector = driver.find_element_by_xpath(video_selector_xpath)
				video_selector.click()
				time.sleep(2)

			with open("skillshare.log", "w+") as log_file:
				log_file.write(json.dumps(proxy.har, indent=4, sort_keys=True))

			newpid = os.fork()
			allpid.append(newpid)
			if newpid==0:
				#print(videos_list)
				write_links_to_file()
				accept_value = get_accept_value()
				videos_list_json = downloadAllVideosJson(accept_value, videos_list, titles_list)
				video_links, titles_list = getVideoLinksAndTitle(videos_list_json)
				makeDirectoryForCourse(course_title)
				downloadVideosWithTitles(video_links, titles_list)
				
				with open(os.path.join(absolute_path, "done_downloaded"), "a+") as done_file:
					done_file.write(link_list[index_link]+'\n')

			else:
				#print("Press any key to continue...")
				def waitThatChild():
					childIndex = len(allpid)-1
					os.waitpid(allpid[childIndex], 0)
					allpid[childIndex] = None

				Thread(target=waitThatChild, args=[]).start()
				
				time.sleep(2)
				if not link_list:
					if input("Still want to download any class? [y/Y/N/n]").lower()=="n":
						break
				
				print("Lets Go More!!!")
				driver.get(home_url)


		except common.exceptions.NoSuchElementException:
			print("Looks like not in class link. skipping...")

	print("Okay. waiting for another task done...")
	for pid in allpid:
		if not pid==None:
			continue
		os.waitpid(pid, 0)
	print("All task done! Quiting...")
	return 0		
	
	server.stop()
	driver.quit()
	
		

if __name__ == '__main__':
    main()