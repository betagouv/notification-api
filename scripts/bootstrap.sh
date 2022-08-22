#!/bin/bash

# Install Python development dependencies
pip3 install -r requirements_for_test.txt

# Upgrade databases
flask db upgrade
