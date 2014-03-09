#!/usr/bin/env python

# Ubuntu Unity indicator for Newsblur

# Copyright 2014 Ali Gunduz <ali@aligunduz.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import indicate

import requests

import os
import subprocess
from time import time
import gobject
import gtk


USERNAME = ''
PASSWORD = ''

dirname = os.path.dirname(os.path.realpath(__file__))
desktop_file = os.path.join(dirname, 'Newsblur.desktop')
count = '0'
frequency = 120	# in seconds


def open_newsblur():
	gtk.show_uri(gtk.gdk.Screen(), 'https://newsblur.com/', 0)


def get_auth():
	query = subprocess.check_output('zenity --password --username --title="Newsblur Indicator"', shell=True)
	username = query.split('|')[0]
	password = query.split('|')[1].rstrip()
	return username, password


def get_unread():
	session = requests.Session()
	session.post('https://www.newsblur.com/api/login', {'username': USERNAME, 'password': PASSWORD})
	hash_response = session.get('https://www.newsblur.com/reader/unread_story_hashes')
	hashes = hash_response.json()['unread_feed_story_hashes']
	unread = 0
	for hash in hashes:
		unread += len(hashes[hash])
	return unread

def server_display(server, time):
	open_newsblur()


def indicator_display(source, time):
	open_newsblur()


def check_feeds(source):
	unread = get_unread()
	global count
	if unread is not None and unread is not int(count):
		source.set_property('draw-attention', 'true')
    	count = str(unread)
    	source.set_property('count', count)
    	source.show()
	source.set_property_time("time", time())
	return True


if __name__ == '__main__':
	USERNAME, PASSWORD = get_auth()

	# Server
	server = indicate.indicate_server_ref_default()
	server.set_type('message.im')
	server.set_desktop_file(desktop_file)
	server.connect('server-display', server_display)
	server.show()

	# Source
	source = indicate.Indicator()
	source.set_property('subtype', 'im')
	source.set_property('sender', 'Unread stories')
	source.set_property('body', 'Test body')
	source.set_property('count', count)
	source.set_property_time("time", time())
	source.show()
	source.connect('user-display', indicator_display)

	# Loop
	check_feeds(source)
	gobject.timeout_add_seconds(frequency, check_feeds, source)
	gtk.main()