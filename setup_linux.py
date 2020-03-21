'''
setup.py
for skillshare-dl
'''
import os
import shutil
try:
	user_id = os.geteuid()

except AttributeError:
	# Running Windows...
	"This script does not support Windows at the moment, sorry. Exiting..."
	exit()

if user_id != 0:
	print("This script needs to be run as root! Exiting...")
	exit()

print("------------skillshare-dl setup/installer------------")
print("This script is going to install all the neccessary dependencies",
"and tools needed to run skillshare-dl. Keep in mind:\n",
"This tool has only been tested on Linux using Chrome 79 (at the time of writing).\n")
choice = input("Are you sure you want to proceed? [y/n]: ").lower().strip()
if choice != 'y':
	print("Exiting...")
	exit()

print("The following tools are needed:")
print("- Chrome/Chromium\n- Python 3 (preferably 3.7)\n- Selenium")
print("- browsermob-proxy\n- Chrome WebDriver\n- pip/pip3")

chrome_installed_flag = input("Is Chrome or Chromium installed and running the latest version? [y/n]: ").lower().strip()
if chrome_installed_flag == 'n':
	print("Installing Chrome now...")
	os.system('wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - ')
	os.system('sudo echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list')
	os.system('sudo apt-get update')
	os.system('sudo apt-get install google-chrome-stable')
else:
	print("Chrome already installed, skipping!")

print("Installing Python 3...")
os.system("apt-get install python3")

print("Installing Java JRE...")
os.system("apt-get install default-jre")

print("Installing Selenium...")
os.system('python3 -m pip install selenium')

print("Installing browsermob-proxy...")
os.system("python3 -m pip install browsermob-proxy")

print("Setting permissions...")
os.system("chmod +x binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy")
os.system("chmod +x binaries/chromedriver")
'''
Mac:
install brew by running:
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install wget

wget https://dl.google.com/mac/stable/GGRO/googlechrome.dmg
open ~/Downloads/googlechrome.dmg
wait until the image has been opened
sudo cp -r /Volumes/Google\ Chrome/Google\ Chrome.app /Applications/
'''