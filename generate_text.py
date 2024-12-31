from flask import Flask, render_template, request, redirect, url_for, make_response
import subprocess
import random
import deepl
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

