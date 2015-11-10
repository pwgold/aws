#################
# Port Settings:
#################
# Type   | Protocol | Port Range | Source   | Purpose
# SSH    | TCP      | 22         | Anywhere | default
# HTTPS  | TCP      | 443        | Anywhere |  ??
# Custom | TCP      | 8888       | Anywhere | IPython Notebook
# Custom | TCP      | 8787       | Anywhere | RStudio
# Custom | TCP      | 3838       | Anywhere | Shiny Server

############################################################
# Ubuntu tools
############################################################
# TODO: o remove unnecessary packages
sudo apt-get update
for LINE in openjdk-7-jdk git python-software-properties python g++ make gdebi-core Cython python-pandas emacs ipython ipython-notebook;
do
   sudo apt-get -y install $LINE
done

##########
# pip installs
##########
pip install scrapy

############################################################
# IPython Notebook Setup: available on http://<public dns>:8888/
############################################################
# Seems to require anaconda as well as passwd
# References: https://gist.github.com/iamatypeofwalrus/5183133
# Anaconda: https://www.continuum.io/downloads
# Notes: ipython notebook --no-browser
#        then check (eg) https://ec2-54-149-185-144.us-west-2.compute.amazonaws.com:8888

wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86_64.sh
bash Anaconda-2.3.0-Linux-x86_64.sh
source .bashrc

# Create passwrod
#In [1]: from IPython.lib import passwd
#In [2]: passwd()
#Enter password:
#Verify password:
#Out[2]: 'sha1:fc2be5181923:b2b82730872f2c512af20c9dd1157731d2014502'
# then
mkdir certificates
cd certificates
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
cd ../

NB_USER=nbserver
ipython profile create $NB_USER
CONFIG="/home/ubuntu/.ipython/profile_$NB_USER/ipython_notebook_config.py"
# Add these lines to the config file
#c.IPKernelApp.pylab = 'inline'
#c.NotebookApp.certfile = '/home/ubuntu/certificates/mycert.pem'
#c.NotebookApp.ip = '*'
#c.NotebookApp.open_browser = False"
#c.NotebookApp.password = 'sha1:f9b4b2742cb8:a49b862c7cc1958ef17750f0b44c6f82ffba47a6'"
#c.NotebookApp.port = 8888 # NB: You'll have to open this port to"
ipython notebook --profile=nbserver
# importantly you should see:
# The IPython Notebook is running at: http***s***://[all ip addresses on your system]:8888/

############################################################
# R Upgrade - do this prior to Rstudio and Shiny setup
############################################################
# Reference: http://www.r-bloggers.com/amazon-ec2-upgrading-r/
sudo apt-get remove -y r-base-core
# Add 'deb http://cran.rstudio.com/bin/linux/ubuntu trusty/' to /etc/apt/sources.list
# Didn't try:
# gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
# gpg -a --export E084DAB9 | apt-key add -
sudo apt-get update -y
sudo apt-get upgrade # -y might work if we fix gpg
sudo apt-get install r-base # Ibid.
R --version | grep 3.2.2 # verify it says ~ R version 3.2.2 (2015-08-14) -- "Fire Safety"

for PKG in shiny ggplot2 rmarkdown dplyr;
do
    sudo su - -c "R -e \"install.packages('$PKG', repos='http://cran.rstudio.com/')\""
done

############################################################
# Rstudio Setup: available on http://<public dns>:8787/  # NB: *not* https
############################################################
# Reference: http://blog.yhathq.com/posts/r-in-the-cloud-part-1.html
# TODO: o find a quicker version, maybe: http://www.r-bloggers.com/instructions-for-installing-using-r-on-amazon-ec2/
sudo apt-get install -y gdebi-core libapparmor1
wget http://download2.rstudio.org/rstudio-server-0.97.551-amd64.deb
sudo gdebi rstudio-server-0.97.551-amd64.deb
# Setup a user: http://www.indicatrix.org/2014/08/10/running-rstudio-server-on-amazon-ec2/ (Step 7)
sudo passwd ubuntu
# make sure everything is working
sudo rstudio-server verify-installation

############################################################
# Shiny Setup: available on http://<public dns>:3838/ and http://<public dns>:3838/sample_apps
############################################################
# This file: /opt/shiny-server/config/default.config sets port and host dir, by default 3838 and /srv/shiny-server
# References: http://www.r-bloggers.com/deploying-shiny-server-on-amazon-some-troubleshoots-and-solutions/
#             http://www.r-bloggers.com/how-to-host-your-shiny-app-on-amazon-ec2-for-mac-osx/
#             http://www.r-bloggers.com/deploying-shiny-server-on-amazon-some-troubleshoots-and-solutions/
#             https://www.digitalocean.com/community/tutorials/how-to-set-up-shiny-server-on-ubuntu-14-04
wget -O shiny-server.deb http://download3.rstudio.org/ubuntu-12.04/x86_64/shiny-server-1.3.0.403-amd64.deb
sudo gdebi shiny-server.deb

############################################################
# HTML Hosting
############################################################
# References: http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-hosting-your-website.html#upload-files
# Files you can view in console here: https://console.aws.amazon.com/s3/home?region=us-west-2&bucket=arithmetic02.com&prefix=
# are available here: http://arithmetic02.com.s3-website-us-west-2.amazonaws.com/ + auctions/AUctionUpdates.html


############################################################
# Pyjnius / IFA setup
############################################################
# Reference: https://github.com/kivy/pyjnius
# Note that you need to call 'make' and not 'sudo python setup.py install' for installation. 
# Usage: 
# export CLASSPATH=/home/ubuntu/ifa-1.7.jar # only works with 1.7 version export:
# export PYTHONPATH=/home/ubuntu/pyjnius/ # only works with 1.7 version export:
# "In Eclipse, Ctrl-click on project > Properties > Java Compiler > Compiler compliance level -> change to 1.7,
#  build jar and it will be in creditanalytics/CreditAnalytics/dev/ifa-1.7.jar",
## scp -i Downloads/wiz.pem git/creditanalytics/CreditAnalytics/dev/ifa-1.7.jar $USER@$IP:/home/$USER # relative to /Users/petergoldstein
# then from directory under pyjnius, you can run:
# python  -c "from jnius import autoclass as ac; ac('org.drip.sample.bloomberg.SWPM').main([''])"
git clone https://github.com/kivy/pyjnius.git
cd pyjnius
make 
cd ../






