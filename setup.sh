#!/bin/bash

func=$1
port=$2

if [ "$#" -lt 2 ]
then
	echo "$(tput setaf 6)Usage: ./setup.sh <action/help> $(tput bold)PORT$(tput sgr0)"
else
	case $func in
		run)
		  sudo apt install python3-pip
		  pip install numpy
		  pip install pycryptodome
			pip install termcolor
			pip install flask_cors
			export FLASK_APP=rest.py
			export FLASK_DEBUG=1
			flask run --host=0.0.0.0 --port=$port
			;;
		init)
			if [ "$#" -ne 3 ]
			then
				echo "$(tput setaf 6)Usage: ./setup.sh init $(tput bold)PORT num_of_nodes$(tput sgr0)"
			else
				num_of_nodes=$3
				curl http://localhost:$port/init/$num_of_nodes
			fi
			;;
		connect)
			if [ "$#" -ne 3 ]
			then
				echo "$(tput setaf 6)Usage: ./setup.sh connect $(tput bold)PORT IP$(tput sgr0)"
			else
				ip=$3
				curl http://localhost:$port/connect/$ip/$port
			fi
			;;
		*)
	esac
fi