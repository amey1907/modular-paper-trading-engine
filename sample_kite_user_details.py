from kiteconnect import KiteConnect
import requests
# from flask import Flask, request, redirect, url_for

# app = Flask(__name__)

# Initial setup (replace with your actual keys and URL)
api_key = "eemxwu7uqp9zrloq"

api_secret = "mju9wh2k1jemo7i3sviro7rmw2krkou4"
redirect_url = "http://127.0.0.1:5000/callback"

# 1. Generate login URL and redirect user
kite = KiteConnect(api_key=api_key)
login_url = kite.login_url()
print(login_url)