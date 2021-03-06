###############################################################################
# Author: Greg Zynda
# Last Modified: 01/15/2021
###############################################################################
# BSD 3-Clause License
#
# Copyright (c) 2018, Texas Advanced Computing Center - UT Austin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

import sys, os, logging, json
logger = logging.getLogger(__name__)

try:
	import urllib2
	pyv = 2
except:
	import urllib.request as urllib2
	pyv = 3

from rgc.ContainerSystem.url import url_parser
from rgc.helpers import translate, iterdict, retry_call, delete

class metadata(url_parser):
	'''
	Class for interacting with variable cache

	# Attributes
	self.categories (dict)= {url: category list}
	self.keywords (dict)= {url: keyword list}
	self.description (dict)= {url: description}
	self.homepage (dict)= {url: homepage url}
	'''
	def __init__(self):
		super(metadata, self).__init__()
		self.categories = {}
		self.keywords = {}
		self.description = {}
		self.homepage = {}
	def _getMetadata(self, url):
		'''
		Assuming the image is a biocontainer,

		 - `self.categories[url]`
		 - `self.keywords[url]`
		 - `self.description[url]`
		 - `self.homepage[url]`

		are set after querying https://dev.bio.tools

		# Parameters
		url (str): Image url used to pull
		'''
		if url in self.description and url in self.keywords and url in self.description:
			logger.debug("Metadata already set for %s"%(url))
			return
		if url not in self.name: self.parseURL(url)
		name = self.name[url]
		self.homepage[url] = False
		try:
			# Check dev.bio.tools
			md_url = "https://dev.bio.tools/api/tool/%s?format=json"%(name)
			resp_json = json.loads(translate(urllib2.urlopen(md_url).read()))
			topics = [topic['term'] for topic in resp_json['topic']]
			topics = [t for t in topics if t != 'N/A']
			functions = [o['term'] for f in resp_json['function'] for o in f['operation']]
			desc = resp_json['description']
			if 'homepage' in resp_json: self.homepage[url] = resp_json['homepage']
		except urllib2.HTTPError:
			try:
				# Check Launchpad
				md_url = "https://api.launchpad.net/devel/%s"%(name)
				resp_json = json.loads(translate(urllib2.urlopen(md_url).read()))
				desc = resp_json['description']
				self.homepage[url] = resp_json['homepage_url']
				topics = ["Container"]
				functions = ["Unknown"]
			except:
				# Default values
				logger.debug("No record of %s on dev.bio.tools or launchpad"%(name))
				functions = ["Unknown"]
				topics = ["Container"]
				desc = "The %s package"%(name)
		self.categories[url] = functions
		self.keywords[url] = topics
		self.description[url] = desc
