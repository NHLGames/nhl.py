from flask import Flask, request
import json
import urllib2
import os
import time
import datetime
app = Flask(__name__)

@app.route("/")
def get_games():
	cdn = 'hlslive-l3c'
	folder = 'ls04'
	todaysDate = time.strftime("%Y-%m-%d")
	date = request.args.get('date')
	textOnly = request.args.get('text')
	if date:
		todaysDate = date
	try:
		date = datetime.datetime.strptime(todaysDate,"%Y-%m-%d")
	except Exception, e:
		return '<html><body><div>Invalid Date Format</div></body></html>'
	if (datetime.datetime.today() - date).days > 3:
		cdn = 'hlsvod-akc'
		folder = 'ps01'
	
	page=''
	try:
		if os.path.exists('nhl/' + todaysDate + '.json') == False:
			response = urllib2.urlopen('http://statsapi.web.nhl.com/api/v1/schedule?teamId=&startDate=' + todaysDate + '&endDate=' + todaysDate + '&expand=schedule.teams,schedule.game.content.media.epg')
			games = response.read()
			with open('nhl/' + todaysDate + '.json', 'w') as file:
    				file.write(games)
		with open('nhl/games.txt') as availableGames:
    			gamesArray = availableGames.readlines()
		for index in range(len(gamesArray)):
			gamesArray[index] = gamesArray[index].replace('\n','')
	except Exception, e:
		return '<html><body><div>' + str(e).replace('<','').replace('>','') + '</div></body></html>'
		
	gamesFile = open('nhl/' + todaysDate + '.json')
	data = json.load(gamesFile)
	
	if textOnly and textOnly == 'true':
		if data['dates']:
			for game in data['dates'][0]['games']:
				# Sample date 2016-03-03T00:00:00Z
				matchTime = datetime.datetime.strptime(str(game['gameDate']), "%Y-%m-%dT%H:%M:%SZ")
				hours = matchTime.hour
				minutes = matchTime.minute
				nhldate = matchTime
				
				for media in game['content']['media']['epg']:
					if media['title'] == 'NHLTV':
						for stream in media['items']:
							if(str(stream['mediaPlaybackId']) in gamesArray):
								status = 'Available'
							else:
								status = 'Unavailable'
							if stream['mediaFeedType'] != 'COMPOSITE' and stream['mediaFeedType'] != 'ISO':
								page += status + ',' + matchTime.strftime('%H:%M') + ',' + game['teams']['away']['team']['name'] + ' (' + game['teams']['away']['team']['abbreviation'] + '),' + game['teams']['home']['team']['name'] + ' (' + game['teams']['home']['team']['abbreviation'] + '),'
								page += str(stream['mediaFeedType']) + ',http://' + cdn + '.med2.med.nhl.com/' + folder + '/nhl/' + nhldate.strftime("%Y/%m/%d") + '/NHL_GAME_VIDEO_' + \
								str(game['teams']['away']['team']['abbreviation']) + str(game['teams']['home']['team']['abbreviation']) + '_M2_' + str(stream['mediaFeedType']).replace('AWAY','VISIT') + \
								'_' + nhldate.strftime("%Y%m%d") + '/master_wired60.m3u8,' + \
								'http://hlsvod-akc.med2.med.nhl.com/ps01/nhl/' + nhldate.strftime("%Y/%m/%d") + '/NHL_GAME_VIDEO_' + \
								str(game['teams']['away']['team']['abbreviation']) + str(game['teams']['home']['team']['abbreviation']) + '_M2_' + str(stream['mediaFeedType']).replace('AWAY','VISIT') + \
								'_' + nhldate.strftime("%Y%m%d") + '/master_wired60.m3u8,' + \
								str(stream['mediaPlaybackId']) + '\r\n'
	else:
		if data['dates']:
			page += '<html><body><div>All times are UTC.<br/><br/>'
			for game in data['dates'][0]['games']:
				# Sample date 2016-03-03T00:00:00Z
				matchTime = datetime.datetime.strptime(str(game['gameDate']), "%Y-%m-%dT%H:%M:%SZ")
				hours = matchTime.hour
				minutes = matchTime.minute
				nhldate = matchTime
				
				page +=  matchTime.strftime('%H:%M') + ' - ' + game['teams']['away']['team']['name'] + ' (' + game['teams']['away']['team']['abbreviation'] + ') @ ' + game['teams']['home']['team']['name'] + ' (' + game['teams']['home']['team']['abbreviation'] + ')<br/>'
				page += 'Key: <a href="http://nhl.com/tv/' + str(game['gamePk']) + '" target="_new">' + str(game['gamePk']) + '</a><br/>'
				for media in game['content']['media']['epg']:
					if media['title'] == 'NHLTV':
						for stream in media['items']:
							if(str(stream['mediaPlaybackId']) in gamesArray):
								status = 'Available'
							else:
								status = 'Unavailable'
							if stream['mediaFeedType'] != 'COMPOSITE' and stream['mediaFeedType'] != 'ISO':
								page += str(stream['mediaFeedType']) + ': ' + str(stream['mediaPlaybackId']) + ' <a href="http://' + cdn + '.med2.med.nhl.com/' + folder + '/nhl/' + nhldate.strftime("%Y/%m/%d") + '/NHL_GAME_VIDEO_' + \
								str(game['teams']['away']['team']['abbreviation']) + str(game['teams']['home']['team']['abbreviation']) + '_M2_' + str(stream['mediaFeedType']).replace('AWAY','VISIT') + \
								'_' + nhldate.strftime("%Y%m%d") + '/master_wired60.m3u8">m3u8</a> ' + \
								' <a href="http://hlsvod-akc.med2.med.nhl.com/ps01/nhl/' + nhldate.strftime("%Y/%m/%d") + '/NHL_GAME_VIDEO_' + \
								str(game['teams']['away']['team']['abbreviation']) + str(game['teams']['home']['team']['abbreviation']) + '_M2_' + str(stream['mediaFeedType']).replace('AWAY','VISIT') + \
								'_' + nhldate.strftime("%Y%m%d") + '/master_wired60.m3u8">vod</a> ' + \
								'(' + status + ')<br/>'

				page += '<br/>'
	
		page += '</div></body></html>'
	return page

if __name__ == "__main__":
	app.debug = True
	app.run('0.0.0.0',5001)
