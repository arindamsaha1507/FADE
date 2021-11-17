#!/usr/bin/env python
# coding: utf-8

import sys
from main_dash import app
from app_details import app_design
import os
import yaml

if __name__ == '__main__':

    with open('file_paths.yml', 'r') as f:
        fp = yaml.safe_load(f)
    os.chdir(fp['fade_directory'])

    app.layout = app_design(file_paths=fp)
    app.run_server()
