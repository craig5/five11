#!/bin/bash

GUNICORN_BIN=`which gunicorn`
SERVER_PORT=8888

###
# error codes
E_OK=0
E_MISSING_COMMAND=11
E_UNKNOWN_COMMAND=12
E_UNKNOWN=255

function showHelp() {
	echo "Available commands:"
	echo "	fg	starts up gunicorn server in the foreground"
	echo "	start	starts up gunicorn server (exec)"
	echo "	stop	stops server (via pidi)"
	echo "	status	shows whether server is running or not"
	echo "	info	prints various internal variables"
	echo "	help	this message"
}

function startForeground() {
	echo "Starting in the foreground."
	$GUNICORN_BIN -b 0.0.0.0:$SERVER_PORT
}

function main() {
	command=$1
	if [ -z "$command" ]; then
		echo "Please enter a command."
		showHelp
		exit $E_MISSING_COMMAND
	fi
	case $command in
		'fg')
			startForeground
			;;
		'start')
			echo "Starting server."
			;;
		'stop')
			echo "Stopping server."
			;;
		'status')
			echo "Status:"
			;;
		'info')
			echo "gunicorn bin: $GUNICORN_BIN"
			echo "server port: $SERVER_PORT"
			;;
		'help')
			showHelp
			;;
		*)
			echo "Unknown command."
			showHelp
			exit $E_UNKNOWN_COMMAND
	esac
}

main $@
# End of file.
