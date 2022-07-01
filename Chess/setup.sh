#!/bin/bash

install_modules () {
    if [[ $1=="pip3" ]]
    then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    exit
}

type -P python3 >/dev/null 2>&1 && test="Python 3 is installed"

echo $test

if [[ $test=="Python 3 is installed" ]]
then
    type -P pip3 >/dev/null 2>&1 && install_modules "pip3"
    type -P pip >/dev/null 2>&1 && install_modules "pip"
else
    sudo apt get install python3 -y
    install_modules "pip3"
fi