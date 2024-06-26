#!/bin/bash

function=$1

echo "$(tput setaf 6)Enter <help> for options"
echo "<Running: "$function">$(tput sgr0)"

functions=( "init" "connect" "new_transaction" "view_transactions" "show_balance" "show_stake" "update_stake" "view_block" "blockchain" "timers")

expl=('initialize network with bootstrap node'
		'connect node to network'
		'create a transaction'
		"view transactions in last validated block"
		"view node\'s balance"
		"view node\'s stake"
		"update node\'s stake"
		"view the transactions of the last block"
		"view node\'s blockchain"
		"view timers for node")

use=('use: ./cli.sh init <PORT> <number of nodes>'
	'use: ./cli.sh connect <IP> <PORT>'
	'use: ./cli.sh new_transaction  <PORT> <ID> <amount> <message>'
	'use: ./cli.sh view_transactions <PORT>'
	'use: ./cli.sh show_balance <PORT>'
	'use: ./cli.sh show_stake <PORT>'
	'use: ./cli.sh update_stake <PORT> <amount>'
	'use: ./cli.sh view_block <PORT>'
	'use: ./cli.sh blockchain <PORT>'
	'use: ./cli.sh timers <PORT>')

case $function in
	init)
		port=$2
		num_of_nodes=$3
		# use: ./cli.sh init <PORT> <number of nodes>
		curl http://localhost:$port/init/$num_of_nodes
		;;
	connect)
		ip=$2
		port=$3
		# use: ./cli.sh connect <IP> <PORT>
		# IP format: 192.168.1.<num>
		curl http://localhost:$port/connect/$ip/$port
		;;
	new_transaction)
		port=$2
		id=$3
		amount=$4
		message=$5
		# data="{\"id\":\"$id\",\"amount\":$amount}"
		data="{\"id\":\"$id\",\"message\":\"$message\",\"amount\":\"$amount\"}"
		echo "$data"
		# use ./cli.sh new_transaction <PORT> <ID> <amount>
		curl -d $data -H "Content-Type: application/json" -X POST http://localhost:$port/transaction/new
		;;
	view_transactions)
		port=$2
		# use ./cli.sh view_transactions <PORT>
		curl http://localhost:$port/transactions/view
		;;
	show_balance)
		port=$2
		# use ./cli.sh balance <PORT>
		curl http://localhost:$port/show_balance
		;;
	show_stake)
		port=$2
		# use ./cli.sh balance <PORT>
		curl http://localhost:$port/show_stake
		;;
  update_stake)
		port=$2
		amount=$3
		data="{\"amount\":\"$amount\"}"
		echo "$data"
		# use ./cli.sh balance <PORT>
		curl -d $data -H "Content-Type: application/json" -X POST http://localhost:$port/update_stake
		;;
	view_block)
		port=$2
		# use ./cli.sh balance <PORT>
		curl http://localhost:$port/transactions/view
		;;
	blockchain)
		port=$2
		# use ./cli.sh blockchain <PORT>
		curl http://localhost:$port/blockchain/view
		;;
	timers)
		port=$2
		# use ./cli.sh timers <PORT>
		curl http://localhost:$port/time/transaction
		curl http://localhost:$port/time/block
		;;
	help)
		for i in {0..6}
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