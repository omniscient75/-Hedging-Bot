#!/bin/bash
export $(grep -v '^#' .env | xargs)
python main.py 