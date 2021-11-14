#!/usr/bin/env python
# coding: utf-8

import sys
from main_dash import app
from app_details import app_design

if __name__ == '__main__':

    sys.stderr = open('warnings.log', 'w')
    sys.stdout = open('outputs.log', 'w')

    app.layout = app_design()

    app.run_server()
