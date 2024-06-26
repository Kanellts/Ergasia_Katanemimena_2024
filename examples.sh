#!/bin/bash

function=$1

echo "$(tput setaf 6)Enter <help> for options"
echo "<Running: "$function">$(tput sgr0)"

functions=( "init" "connect" "new_transaction" "view_transactions" "show_balance" )

expl=('initialize network with bootstrap node'
		'connect node to network'
		'create a transaction'
		"view transactions in last validated block"
		"view node\'s balance")

use=('use: ./examples.sh init <PORT> <number of nodes>'
	'use: ./examples.sh connect <IP> <PORT>'
	'use ./examples.sh new_transaction <PORT> <ID> <amount> <message>'
	'use ./examples.sh view_transactions <PORT>'
	'use ./examples.sh balance <PORT>')

case $function in
	init)
		port=$2
		num_of_nodes=$3
		# use: ./examples.sh init <PORT> <number of nodes>
		curl http://localhost:$port/init/$num_of_nodes
		;;
	connect)
		ip=$2
		port=$3
		# use: ./examples.sh connect <IP> <PORT>
		# IP format: 192.168.1.<num>
		curl http://localhost:$port/connect/$ip/$port
		;;
	new_transaction)
		port=$2
		id=$3
		amount=$4
		message=$5
		#data="{\"id\":\"$id\",\"message\":\"$message\",\"amount\":\"$amount\}"
		#data="{\"id\":\"$id\",\"message\":\"$message\",\"amount\":\"$amount\"}"
		#data="{\"id\":\"$id\",\"message\":\"$message\",\"amount\":$amount}"
		data="{\"id\":\"$id\",\"message\":\"$message\",\"amount\":\"$amount\"}"
		echo "$data"
		# use ./examples.sh new_transaction <PORT> <ID> <amount>
		curl -d $data -H "Content-Type: application/json" -X POST http://localhost:$port/transaction/new
		;;
	view_transactions)
		port=$2
		# use ./examples.sh view_transactions <PORT>
		curl http://localhost:$port/transactions/view
		;;
	show_balance)
		port=$2
		# use ./examples.sh balance <PORT>
		curl http://localhost:$port/show_balance
		;;
	help)
		for i in {0..4}
		do
			echo "$(tput setaf 3)"
			echo "$(tput setaf 6)${functions[$i]}$(tput setaf 3):  ${expl[$i]}"
			echo "${use[$i]}"
			echo "$(tput setaf 4)~~~~~~~~~~"
		done
		;;
	*)
esac

echo ""
echo "$(tput setaf 6)<Done>$(tput sgr0)"