USER=ubuntu
IP=$1 # 54.148.37.26 # 54.149.185.144 # TODO: o generate new ip by aws cli
scp -i Downloads/wiz.pem git/creditanalytics/CreditAnalytics/dev/ifa-1.7.jar $USER@$IP:/home/$USER # relative to /Users/petergoldstein
scp -i Downloads/wiz.pem install.sh $USER@$IP:/home/$USER # relative to /Users/petergoldstein
ssh -i Downloads/wiz.pem $USER@$IP
