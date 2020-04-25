import os
import time
import json
import urllib
import requests
from pathlib import Path, PureWindowsPath
from selenium import webdriver
from browsermobproxy import Server
import json
from threading import Thread
import traceback
import re

home_url = 'https://skillshare.com/home'
login_url = 'https://skillshare.com/login'
absolute_path = os.path.dirname(os.path.abspath(__file__))
max_download_in_time = 3
download_directory = '/media/kevin/3AE1A2A77B72C361/skillshare_downloads'

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
	webdriver_path = str(Path("./binaries/chromedriver81").absolute())
	print(webdriver_path)
	driver = webdriver.Chrome(executable_path=webdriver_path, options = chrome_options)
	print('initialized Chrome window!')

'''
Navigate to the login page.
Sometimes it throws you back to the homepage for teachers
without even logging you in. That's what the alternative_login function is for
'''
def login(username, password):
	print('Attempting to log in...')
	email_field = driver.find_element_by_name('LoginForm[email]')
	email_field.send_keys(username)
	password_field = driver.find_element_by_name('LoginForm[password]')
	password_field.send_keys(password)
	remember_me_checkbox = driver.find_element_by_css_selector('#login-form-remember-me')
	remember_me_checkbox.click()
	submit_login_button = driver.find_element_by_xpath('//*[@id="page-wrapper"]/div[1]/div/form/form/input[1]')
	#submit_login_button = driver.find_element_by_css_selector('#page-wrapper > div.center-page > div > form > form > input.button.large.full-width.btn-login-submit.initialized')
	submit_login_button.click()
	time.sleep(2)
	driver.get(home_url)
	currentUrl = driver.current_url
	print("Current URL: " + currentUrl)
	
	if currentUrl != 'https://www.skillshare.com/home':
		print("Current URL is {}\nand NOT {}!\nTrying to log in again...".format(currentUrl, 'https://skillshare.com/home'))
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
		print(links)
		print(len(links))

	videos_list_json = []

	for index in range(len(links)):
		videos_list_json.append(index)
		# print("K:" + links[index])
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
	print(videos_list_json)
	for index in range(len(videos_list_json)):
		video_links.append(index)
		video_titles.append(index)
		video_json = json.loads(videos_list_json[index])
		video_links[index] = video_json['sources'][7]['src']
		# print(video_links[index])
		video_titles[index] = video_json['name']
		# print(video_titles[index])

	return video_links, video_titles

def write_links_to_file():
	skillshare_log = os.path.join(absolute_path, 'skillshare.log')
	skillshare_links = os.path.join(absolute_path, 'skillshare_links.txt')
	skillshare_accept = os.path.join(absolute_path, 'skillshare_accept.txt')
	command_videos_string = 'cat %s | grep -o -E "https://edge.api.brightcove.com/playback/v1/accounts/[01234567890]{1,}/videos/[0123456789]{1,}" | uniq | uniq > %s'%(skillshare_log, skillshare_links)
	os.system(command_videos_string)
	command_accept_value_string = 'cat %s | grep -o -E "application/json;pk=[0123456789ABCDEFGHIJKLMNOPQRSTUVWXZYabcdefghijklmnopqrstuvwxyz-]{1,}" | uniq > %s'%(skillshare_log, skillshare_accept)
	os.system(command_accept_value_string)

def get_accept_value():
	with open("skillshare_accept.txt", "r") as file:
		accept_value = file.read()
	return accept_value.strip()

def downloadVideosWithTitles(video_links, video_titles):
	for index in range(len(video_links)):
		urllib.request.urlretrieve(video_links[index], str(index) + " - " + repairFilename(video_titles[index]) + ".mp4")

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

def cleanUp():
    to_cleanup = ['bmp.log', 'server.log', 'skillshare_accept.txt', "skillshare_links.txt", "skillshare.log"]
    for cache in to_cleanup:
        if os.path.isfile(cache):
            os.remove(cache)

def countLivePid(pid_list):
	return len([i for i in pid_list if i!=None])

def main():
	print('Loading...')
	initializeChrome()
	gmail_or_facebook = True if input('Are you using gmail / facebook login in skillshare? [y / n]: ').lower()=='y' else False
	driver.get(login_url)
    
	if gmail_or_facebook:
		input('Please login with your gmail / facebook and press any key... ')
	
	else:
		username = input("Please enter your E-Mail: ")
		password = input("Please enter your password: ")
		login(username, password)
		logged_in_status = input("Are you logged in and on the homepage? [y/Y/n/N]: ")
		if logged_in_status == 'y' or 'Y':
		    print("Logged in!")
		else:
		    input('Please login manually and press any key here... ')

    
	print('Assuming that you already login')

	link_list = []
	using_link_list = False
    
	#check download_list_link
	with open('to_download_link_list.txt', 'r+') as link_list_file:
		link_list = link_list_file.read().replace(' ', '').split('\n')
		for link in link_list:
			if (not re.match(r'^\s*$', link)):
				using_link_list = True
				break
	
	if using_link_list:
		all_pid = []

		for link_index in range(len(link_list)):	
			os.chdir(absolute_path)

			link = link_list[link_index]
   
			if countLivePid(all_pid)==max_download_in_time:
				print('Reached maximum course download in a time ({} downloads). Waiting them to finish first...'.format(max_download_in_time))
				while countLivePid(all_pid)==max_download_in_time:
					
					#make sure the login session not timeout
					driver.get(home_url)
					driver.refresh()
					time.sleep(30)

				print('Lets go more!\n\n')

			not_succeed = True
			while not_succeed:
				try:
					print('Processing: ' + link)
					driver.get(link)
					proxy.new_har("skillshare", options={'captureHeaders': True})
					driver.refresh()
					course_title = getCourseTitle()
					videos_list = []
					number_of_videos, titles_list = get_number_of_videos()
					# print('number_of_videos: ' + str(number_of_videos))
					# print('titles_list: ' + str(titles_list))
					for index in range(number_of_videos):
						videos_list.append(index)
						videos_list[index] = index
						index += 1
						# print(index)
						video_selector_xpath = '//*[@id="video-region"]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/ul/li/ul/li[' + str(index) + ']'
						# print(video_selector_xpath)
						video_selector = driver.find_element_by_xpath(video_selector_xpath)
						video_selector.click()
						time.sleep(2)			

					with open("skillshare.log", "w+") as log_file:
						log_file.write(json.dumps(proxy.har, indent=4, sort_keys=True))

					write_links_to_file()
					accept_value = get_accept_value()
					videos_list_json = downloadAllVideosJson(accept_value, videos_list, titles_list)
					# print('accept value: ' + str(accept_value))
					# print('videos_list: ' + str(videos_list))
					# print('titles_list: ' + str(titles_list))
					# print(videos_list_json)
					video_links, titles_list = getVideoLinksAndTitle(videos_list_json)
					
					not_succeed = False
				except Exception as error:
					print("Error while trying to processing course "+link)
					print("Error: " + str(error))
					traceback.print_exc()
					print("Trying again in 10 seconds... ")
					time.sleep(10)
     
			new_pid = os.fork()
			all_pid.append(new_pid)
   
			if (new_pid==0):
				json_file = json.dumps({'course_title': course_title, 'video_links': video_links, 'title_lists': titles_list})
				json_file_name = 'temp{}.json'.format(link_index)
				
				with open(os.path.join(absolute_path, json_file_name), "w+") as json_temp:
					json_temp.write(str(json_file))

				child_command = 'konsole -e "python3 {child_script} {json_file_name}"'.format(child_script=os.path.join(absolute_path, 'skillshare-dl_linux_child.py'),json_file_name=os.path.join(absolute_path, json_file_name))
				print('running '+child_command)
				os.system(child_command)
				
				exit(0)

			else:
				def waitThatChild(index):
					os.waitpid(all_pid[index], 0)
					all_pid[index] = None
				
				Thread(target=waitThatChild, args=[link_index]).start()

		print("Now wait them all to finish :)")
		while True:
			if countLivePid(all_pid)==0:
				break
			time.sleep(5)
			

		server.stop()
		driver.quit()
		# cleanUp()
		print("EVERYTHING DONE! ENJOY")
  
  
	else:
		print("Go to the page of the course you want to download and press a key when you're done.")
		input("Waiting for a key to be pressed... ")
		print("You pressed it!")
		print("Current URL: " + driver.current_url)
		proxy.new_har("skillshare", options={'captureHeaders': True})
		driver.refresh()
		course_title = getCourseTitle()
		videos_list = []
		number_of_videos, titles_list = get_number_of_videos()
		for index in range(number_of_videos):
			videos_list.append(index)
			videos_list[index] = index
			index += 1
			print(index)
			video_selector_xpath = '//*[@id="video-region"]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/ul/li/ul/li[' + str(index) + ']'
			print(video_selector_xpath)
			video_selector = driver.find_element_by_xpath(video_selector_xpath)
			video_selector.click()
			time.sleep(2)

		with open("skillshare.log", "w+") as log_file:
			log_file.write(json.dumps(proxy.har, indent=4, sort_keys=True))

		server.stop()
		driver.quit()
		print(videos_list)
		write_links_to_file()
		accept_value = get_accept_value()
		videos_list_json = downloadAllVideosJson(accept_value, videos_list, titles_list)
		#video_links, video_titles = getVideoLinksAndTitle(videos_list_json)
		video_links, titles_list = getVideoLinksAndTitle(videos_list_json)
		#downloadVideosWithTitles(video_links, video_titles)
		makeDirectoryForCourse(course_title)
		downloadVideosWithTitles(video_links, titles_list)
		cleanUp()

if __name__ == '__main__':
    main()