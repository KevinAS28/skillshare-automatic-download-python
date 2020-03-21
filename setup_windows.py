'''
setup.py
for skillshare-dl
'''
import os
import shutil
import zipfile

print("------------skillshare-dl setup/installer------------")
print("This script is going to install all the neccessary dependencies",
"and tools needed to run skillshare-dl.")
choice = input("Are you sure you want to proceed? [y/Y/n/N]: ").lower().strip()
if choice != 'y':
	print("Exiting...")
	exit()

print("The following tools are needed:")
print("- Chrome/Chromium\n- Python 3 (preferably 3.7)\n- Selenium")
print("- browsermob-proxy\n- Chrome WebDriver\n- pip/pip3")

chrome_installed_flag = input("Is Chrome or Chromium installed and running the latest version? [y/Y/n/N]: ").lower().strip()
if chrome_installed_flag == 'n':
	print("Please install Chrome. Exiting now...")
	exit()

#Installs it on both python2 and python3 because that's how things work, apparently

print("Installing Selenium...")
try:
	os.system('python3 -m pip install --user selenium')
except:
	print("PASS")
	pass
try:
	os.system('python -m pip install --user selenium')
except:
	print("PASS")
	pass

print("Installing browsermob-proxy...")
try:
	os.system("python3 -m pip install --user browsermob-proxy")
except:
	print("PASS")
	pass
try:
	os.system("python -m pip install --user browsermob-proxy")
except:
	print("PASS")
	pass