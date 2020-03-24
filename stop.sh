#!/usr/bin/env bash
ps -ef | grep :5000 | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep bs.py | grep -v grep | awk '{print $2}' | xargs kill -9
