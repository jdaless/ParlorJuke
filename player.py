import os, json, socket, threading, pygame, time, spotipy, socketserver
from http.server import *
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps

dirName = os.path.dirname(os.path.abspath(__file__))

class PlayerModel():
	def __init__(self):
		self.queue = []
		self.currentlyPlaying = []
		self.playingStarted = 0
	def pop(self):
		self.currentlyPlaying = self.queue.pop()
	def get(self):
		return dumps({0: self.currentlyPlaying, 1:self.queue, 2:self.playingStarted})

pygame.mixer.init()
spotify = spotipy.Spotify()
model = PlayerModel()

def playQueue():
	print("Jukebox thread started...")
	while(True):
		if(len(model.queue) > 0):
			model.pop()
			if(model.currentlyPlaying[0] == "file"):
				try:
					pygame.mixer.music.load(dirName + '/music/' + model.currentlyPlaying[1])
					pygame.mixer.music.play()
					model.playingStarted = time.mktime(time.localtime())
					while(pygame.mixer.music.get_busy()):
						continue

				except pygame.error:
					print("Error loading file")
			if(model.currentlyPlaying[0] == "spotify"):
				spotify.play(model.currentlyPlaying[1])
		else:
			model.currentlyPlaying = None


def socketListener():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost",15000))
	s.listen(1)
	print("Network thread started...")
	while(True):
		connection, sender = s.accept()
		try:
			data = connection.recv(256)
			data = data.decode("utf-8")
			if("add=" in data):
				start = data.index("add=")
				print("Someone added: " + data[(start+4):])
				model.queue.insert(0, ["file", data[(start+4):]])
			if data:
				connection.sendall(
					bytes(
						json.dumps([model.currentlyPlaying, list(reversed(model.queue)), model.playingStarted]),
						'utf8'))
		finally:
			connection.close()

def httpServe():
	PORT = 8000

	Handler = SimpleHTTPRequestHandler

	httpd = socketserver.TCPServer(("localhost", PORT), Handler)
	print("Server thread started...")
	httpd.serve_forever()

def api():
	app = Flask(__name__)

	@app.route("/player")
	def player():
		return model.get()

	app.run(port='5002')

socketThread = threading.Thread(target = socketListener)
playerThread = threading.Thread(target = playQueue)
serverThread = threading.Thread(target = httpServe)
apiThread = threading.Thread(target = api)

socketThread.daemon = True
playerThread.daemon = True
serverThread.daemon = True
apiThread.daemon - True

playerThread.start()
socketThread.start()
serverThread.start()
apiThread.start()

while(True):
	x = input()
	if(x=="break"):
		break
	if(x=="queue"):
		print(list(reversed(model.queue)))
	if(x=="playing"):
		print(model.currentlyPlaying)
	if(x=="library"):
		print(os.listdir(dirName + "/music"))
	if(x=="spotify"):
		model.queue.insert(0, ["spotify", "https://play.spotify.com/track/6t1FIJlZWTQfIZhsGjaulM"])
	if(x.startswith("add")):
		model.queue.insert(0, ["file", x[4:]])
