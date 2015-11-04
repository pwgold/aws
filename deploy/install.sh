sudo apt-get update

# TODO: o remove unnecessary packages
for LINE in openjdk-7-jdk git python-software-properties python g++ make r-base gdebi-core Cython python-pandas emacs ipython ipython-notebook;
do
   sudo apt-get -y install $LINE
done

git clone https://github.com/kivy/pyjnius.git
cd pyjnius
make # as per https://github.com/kivy/pyjnius, not: sudo python setup.py install
# go back; also won't run from above pyjnius/
cd ../

export CLASSPATH=/home/ubuntu/ifa-1.7.jar # only works with 1.7 version export:
export PYTHONPATH=/home/ubuntu/pyjnius/ # only works with 1.7 version export:
# Ctrl-click on project > Properties > Java Compiler > Compiler compliance level -> change to 1.7
python  -c "from jnius import autoclass as ac; ac('org.drip.sample.bloomberg.SWPM').main([''])"

#ipython notebook --no-browser
# then check (eg) https://ec2-54-149-185-144.us-west-2.compute.amazonaws.com:8888
