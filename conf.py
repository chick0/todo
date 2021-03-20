# -*- coding: utf-8 -*-
from os import path, listdir, mkdir
from configparser import ConfigParser

BASE_DIR = path.dirname(__file__)
CONF_DIR = path.join(BASE_DIR, "conf")

if not path.exists(CONF_DIR):
    mkdir(CONF_DIR)

conf = ConfigParser()
conf.read(
    filenames=[path.join(CONF_DIR, f) for f in listdir(path.join(CONF_DIR)) if f.endswith(".ini")],
    encoding="utf-8"
)
