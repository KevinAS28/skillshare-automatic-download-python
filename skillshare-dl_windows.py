import os
import time
import json
import urllib
import requests
from pathlib import Path, PureWindowsPath
from selenium import webdriver
from browsermobproxy import Server

#Open a Chrome windows controlled by selenium
def initializeChrome():
	global driver
	global server
	global proxy
	dict={'port':8090}
	path_to_bmp = Path("./binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy").absolute()
	path_on_windows = str(PureWindowsPath(path_to_bmp))
	server = Server(path=path_on_windows, options=dict)
	#server = Server(path="binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy", options=dict)
	server.start()
	proxy = server.create_proxy()
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
	username_windows = os.getenv('username')
	user_data_path = Path('C:/Users/' + str(username_windows) + '/AppData/Local/Google/Chrome/User Data')
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--disable-extensions")
	chrome_options.add_argument("--ignore-certificate-errors")
	chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
	chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
	chrome_options.add_argument(f'--user-data-dir={user_data_path}')
	path_to_chromedriver = str(Path("./binaries/chromedriver.exe").absolute())
	driver = webdriver.Chrome(path_to_chromedriver, options = chrome_options)
	print('initialized Chrome window!')

'''
Navigate to the login page.
Sometimes it throws you back to the homepage for teachers
without even logging you in. That's what the alternative_login function is for
'''
def login(username, password):
	print('Attempting to log in...')
	driver.get('https://skillshare.com/login')
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
		print(links)
		print(len(links))

	videos_list_json = []

	for index in range(len(links)):
		videos_list_json.append(index)
		print("K:" + links[index])
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
		print(video_links[index])
		video_titles[index] = video_json['name']
		print(video_titles[index])

	return video_links, video_titles

def write_links_to_file():
	windows_cat_path = Path("./binaries/cat.exe").absolute()
	windows_grep_path = Path("./binaries/grep.exe").absolute()
	windows_uniq_path = Path("./binaries/uniq.exe").absolute()
	command_videos_string = str(windows_cat_path) + ' skillshare.log | ' + str(windows_grep_path) + ' -o -E "https://edge.api.brightcove.com/playback/v1/accounts/[01234567890]{1,}/videos/[0123456789]{1,}" | ' + str(windows_uniq_path) + ' > skillshare_links.txt'
	os.system(command_videos_string)
	command_accept_value_string = str(windows_cat_path) + ' skillshare.log | ' + str(windows_grep_path) + ' -o -E "application/json;pk=[0123456789ABCDEFGHIJKLMNOPQRSTUVWXZYabcdefghijklmnopqrstuvwxyz-]{1,}" | ' + str(windows_uniq_path) + ' > skillshare_accept.txt'
	os.system(command_accept_value_string)

def get_accept_value():
	with open("skillshare_accept.txt", "r") as file:
		accept_value = file.read()
	return accept_value.strip()

def downloadVideosWithTitles(video_links, video_titles):
	for index in range(len(video_links)):
		urllib.request.urlretrieve(video_links[index],repairFilename(video_titles[index]) + ".mp4")

def cleanUp():
	if os.path.isfile("bmp.log") == True:
		os.remove("bmp.log")
	if os.path.isfile("server.log") == True:
		os.remove("server.log")
	if os.path.isfile("skillshare_accept.txt") == True:
		os.remove("skillshare_accept.txt")
	if os.path.isfile("skillshare_links.txt") == True:
		os.remove("skillshare_links.txt")
	if os.path.isfile("skillshare.log") == True:
		os.remove("skillshare.log")

def loginRoutine():
	username = input("Please enter your E-Mail: ")
	password = input("Please enter your password: ")
	login(username, password)
	logged_in_status = input("Are you logged in and on the homepage? [y/Y/n/N]: ")
	if logged_in_status == 'y' or 'Y':
		print("Logged in!")
	else:
		print("Not logged in!")
		exit()

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
	course_title = repairFilename(course_title)
	if "/" in course_title:
		course_title.replace("/","-")
	if not os.path.exists(course_title):
		os.makedirs(course_title)
		os.chdir(course_title)
	else:
		os.chdir(course_title)

def main():
	initializeChrome()
	print("Go to the page of the course you want to download and press a key when you're done.")
	input("Waiting for a key to be pressed... ")
	print("You pressed it!")
	print("Current URL: " + driver.current_url)
	proxy.new_har("skillshare", options={'captureHeaders': True})
	driver.refresh()
	course_title = getCourseTitle()
	videos_list = []
	number_of_videos, titles_list = get_number_of_videos()
	print(titles_list)
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
	#print(videos_list)
	write_links_to_file()
	accept_value = get_accept_value()
	videos_list_json = downloadAllVideosJson(accept_value, videos_list, titles_list)
	video_links, video_titles = getVideoLinksAndTitle(videos_list_json)
	#video_links, titles_list = getVideoLinksAndTitle(videos_list_json)
	print(titles_list)
	#print(video_titles)
	#downloadVideosWithTitles(video_links, video_titles)
	makeDirectoryForCourse(course_title)
	downloadVideosWithTitles(video_links, titles_list)
	#downloadVideosWithTitles(video_links,tit)
	cleanUp()

if __name__ == '__main__':
	main()