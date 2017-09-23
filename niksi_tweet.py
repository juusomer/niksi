import os
import twython
import markovify

OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_SECRET = os.environ['OAUTH_SECRET']
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']

with open('model.json') as f:
    model = markovify.Text.from_json(f.read())

niksi = model.make_short_sentence(140)
twitter = twython.Twython(API_KEY, API_SECRET, OAUTH_TOKEN, OAUTH_SECRET)
twitter.update_status(status=niksi)
