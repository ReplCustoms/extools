import os
import json
import random
import asyncio
import repltalk
import requests
from markdown2 import Markdown
from markdown import markdown
from bs4 import BeautifulSoup


int = int
str = str
float = float
len = len
enumerate = enumerate

statuses = ['primary', 'danger', 'info', 'success', 'warning']
mdc = Markdown()
client = repltalk.Client()
loop = asyncio.get_event_loop()

def genTimeObj(dateObj):
	return {
		"day.text" : dateObj.strftime("%A"),
		"month.text" : dateObj.strftime("%B"),
		"year.text" : dateObj.strftime("%Y"),
		"half-date.text" : dateObj.strftime("%B %d, %Y"),
		"full-date.text" : dateObj.strftime("%A - %B %d, %Y"),

		"day.num" : dateObj.strftime("%d"),
		"month.num" : dateObj.strftime("%m"),
		"year.num" : dateObj.strftime("%Y"),
		"full-date.num" : dateObj.strftime("%m-%d-%Y"),
	}

def genUser(name):
	async def getUser(x):
		global user
		user = await client.get_user(x)
	
	loop.run_until_complete(getUser(x=name))
	return user

def genPost(id):
	async def getPost(ids):
		global post
		post = await client.get_post(ids)
	
	loop.run_until_complete(getPost(ids=id))
	return post

def genPostResults(q, o):
	async def soo(x, y):
		global pRes
		pRes = []
		async for post in client.boards.all.get_posts(sort=y, search=x):
			if post not in pRes:
				pRes.append(post)
			else: pass
	
	loop.run_until_complete(soo(q, o))
	return pRes

def getUserSubs(user):
	s = user.subscription
	if str(s) == 'None': 
		return 'Starter'
	elif str(s) == 'hacker':
		return 'Hacker'
	else: 
		return 'Not Found'

def getUserComments(user, limit=30, order='new'):
	async def foo(user, l, o):
		global p
		p = await user.get_comments(limit=l, order=o)

	try:
		loop.run_until_complete(foo(user, limit, order))
	except:
		return None

	return p

def getUserPosts(user, limit=30, order='new'):
	async def poo(user, l, o):
		global k
		k = await user.get_posts(limit=l, order=o)

	try:
		loop.run_until_complete(poo(user, limit, order))
	except Exception as e:
		print(e) 
		return None
	return k

devs = ['irethekid','codemonkey51']
def getUserRoles(user):
	roles = []
	for i in user.roles:
		roles.append(i['name'])
	if(user.name.lower() in devs):
		roles.insert(0,'RC dev')

	return roles

def getUserSpamScore(user):
	q = user.name
	r = requests.get(f'http://bad-boi-api.codemonkey51.repl.co/api/number/{q}')
	if not r.text:
		return 'User Not Found'
	else:
		try:
			score = int(r.text)
		except ValueError:
			score = 10

	if score >= 100:
		color = '#FF0000'
		icon = "Terrible"
	elif score >= 70:
		color = 'orange'
		icon = "Bad"
	elif score >= 40:
		color = '#CCFF00'
		icon = "Sneaky" 
	else:
		color = '#90EE90'
		icon = "Amazing"
	
	return {
		"score" : score,
		"color" : color,
		"emoji" : icon
	}
	
def getUserSpamPercent(user):
	q = user.name
	r = requests.get(f'http://bad-boi-api.codemonkey51.repl.co/api/percent/{q}')
	score = r.text[:-1]
	print(score)
	found = True

	if not r.text: return 'User Not Found'
	else:
		if r.text[-1:] == '%': score = r.text
		else: found = False

	if found:
		try:
			scoreT = score[:-1].split('-')
			scoreAverage = (int(scoreT[0])+int(scoreT[1]))/2
		except IndexError:
			scoreAverage = int(score[:-1])
	else:
		return {
			"score" : r.text,
			"color" : "#FF0000",
			"emoji" : "Terrible"
		}

	if scoreAverage >= 100: color = '#FF0000'; icon = "Terrible"
	elif scoreAverage >= 70: color = 'orange'; icon = "Bad"
	elif scoreAverage >= 40: color = '#CCFF00'; icon = "Sneaky" 
	else: color = '#90EE90'; icon = "Amazing"
	
	return {
		"score" : score,
		"color" : color,
		"emoji" : icon
	}

def genLeaderboard(cap):
	async def genBoard(lim):
		global lboard
		lboard = await client.get_leaderboard(limit=lim)	

	loop.run_until_complete(genBoard(lim=cap))
	return lboard

def genLeaderboardPercentage(cap):
	async def genBoard(lim):
		global lboard
		lboard = await client.get_leaderboard(limit=lim)

	loop.run_until_complete(genBoard(lim=cap))

	over1000 = []
	over500 = []
	over250 = []
	over100 = []
	less100 = []

	for user in lboard:
		if user.cycles >= 1000:
			over1000.append(user.name)
		elif user.cycles >= 500:
			over500.append(user.name)
		elif user.cycles >= 250:
			over250.append(user.name)
		elif user.cycles >= 100:
			over100.append(user.name)
		else:
			less100.append(user.name)

	return {
		'>1000 Cycles' : {
			"size" : len(over1000),
			"users" : over1000,
		},
		'>500 Cycles' : {
			"size" : len(over500),
			"users" : over500
		},
		'>250 Cycles' : {
			"size" : len(over250), 
			"users": over250
		},
		'>100 Cycles' : {
			"size" : len(over100),
			"users" : over100
		},
		'<100 Cycles' : {
			"size" : len(less100),
			"users" : less100
		},
	}

def genRandomStatus(carp=False):
	if not carp:
		statuses = [
			'primary', 'secondary',
			'success', 'danger', 'warning']
	else:
		statuses = [
			'primary', 'success',
			'danger', 'warning', 'info']

		return random.choice(statuses)


def genUserPercentile(user):
	if user.cycles > 1000:
		return {
			"percentile.decimal" : 4.4,
			"percentile.rounded" : 4,
			"color" : " #90EE90"
		}
	elif user.cycles > 500:
		return {
			"percentile.decimal" : 8.0,
			"percentile.rounded" : 8,
			"color" : "#90EE90"
		}
	elif user.cycles > 250:
		return {
			"percentile.decimal" : 9.2,
			"percentile.rounded" : 9,
			"color" : "#CCFF00"
		}
	elif user.cycles > 100:
		return {
			"percentile.decimal" : 25.0,
			"percentile.rounded" : 25,
			"color" : "#CCFF00"
		}
	else:
		return {
			"percentile.decimal" : 55.4,
			"percentile.rounded" : 55,
			"color" : "#FF0000"
		}

def saveChartData(**z):
	cName = z["cName"]
	uTotal = z["uTotal"]

	r = requests.get(f'http://rcapi.irethekid.repl.co/call/{cName}/{uTotal}')
	if r.text:
		with open(f'rc/app/static/me/charts/json/{cName}-{uTotal}.json', 'w') as fh:
			fh.write(r.text)
		return True
	else:
		return False

def renderMD(content, internal=False):
	def _add_a_attrs(soup):
		for tag in soup.find_all("a"):
			tag['rel'] = "nofollow"
			tag['target'] = "_blank"

	def repStrs(target, strs, new):
		for s in strs:
			target = target.replace(s, '')
		return "<html>", target, "</html>"

	soup = BeautifulSoup(
		markdown(content, extensions=['codehilite']), 
		features="html5lib"
	)

	_add_a_attrs(soup)
	res = str(soup.prettify())

	if internal == False:
		return res
	else:
		return repStrs(
			res,
			['<html>', '</html>', '<head>', '</head>', '<body>', '</body>'],
			""
		)

def renderMD2(target):
	return str(mdc.convert(target))

def renderMD3(content):
	res = requests.post(
		"https://api.github.com/markdown",
		headers={"accept" : 'application/vnd.github.v3+json'},
		data=json.dumps({
			"text": str(content),
			"mode": "gfm"
		})
	)

	return res.text
