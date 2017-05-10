from canvasapi import Canvas
import requests
import os
import csv
import time
import re
from bs4 import BeautifulSoup 
from collections import OrderedDict
from config_course_media_search_canvasapi import *  
start_time = time.time()
course_id= raw_input('Canvas ID')
canvas = Canvas(api_url, api_key)
course = canvas.get_course(course_id)
print "Checking " + course.name
writer = csv.writer(open('%s.csv' % course.name, 'wb'))
youtube_link = {}
vimeo_link = {}
media_link = {}
link_media = {}
#checks all pages in a canvas course for media links
pages = course.get_pages()
if pages:
	print "Checking Pages"
	for page in pages:
		page_body = course.get_page(page.url)
		page_location = page.html_url
		if page_body.body:
			contents = page_body.body.encode('utf-8')
			soup = BeautifulSoup (contents, "html.parser")
			list = []
			for link in soup.find_all('a'):
				list.append(link.get('href'))
			list_filter1 = filter(None, list)
			youtube_embed = [s for s in list_filter1 if re.search(youtube_pattern, s)]
			vimeo_embed = [s for s in list_filter1 if "vimeo.com" in s]
			for link in youtube_embed:
				youtube_link.setdefault(link, [])
				youtube_link[link].append(page_location)
			for v_link in vimeo_embed:
				vimeo_link.setdefault(v_link, [])
				vimeo_link[v_link].append(page_location)
			list2 = []
			for link in soup.find_all('iframe'):
				list2.append(link.get('src')) 
			list_filter2 = filter(None, list2)
			youtube_iframe = [s for s in list_filter2 if re.search(youtube_pattern, s)]
			vimeo_iframe = [s for s in list_filter2 if "vimeo.com" in s]
			for link in youtube_iframe:
				youtube_link.setdefault(link, [])
				youtube_link[link].append(page_location)
			for v_link in vimeo_iframe:
				vimeo_link.setdefault(v_link, [])
				vimeo_link[v_link].append(page_location)
			for video in soup.find_all('video'):
				instructure = video.get('class')
				media_id = video.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Video Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(page_location)
			for audio in soup.find_all('audio'):
				instructure = audio.get('class')
				media_id = audio.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Audio Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(page_location)
			for file_link in soup.find_all('a'):
				instructure = file_link.get('class')
				location = file_link.get('data-api-endpoint')
				if location:
					try:
						file_id = location.split('/')[-1:]
						r = requests.get(api_url + 'courses/%s/files/%s'% (course_id, file_id[0]), headers = {'Authorization': 'Bearer ' + '%s' % api_key})
						data_file = r.json()
						file_location = data_file['url'].split('?')[0]
						type = data_file['mime_class']
						if "audio" in type:
							link_name = "Linked Audio File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(page_location)
							link_media[link_name].append(file_location)
						if "video" in type:
							link_name = "Linked Video File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(page_location)
							link_media[link_name].append(file_location)
						if "flash" in type.split('-')[-1:]:
							link_name = "Linked SWF File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(page_location)
							link_media[link_name].append(file_location)
					except KeyError:
						pass

#checks all assignments in a canvas course for media links
assign = course.get_assignments()
if assign:
	print "Checking Assignments"
	for item in assign:
		if item.description:
			assign_location = item.html_url
			contents = item.description.encode('utf-8')
			soup = BeautifulSoup (contents, "html.parser")
			list = []
			for link in soup.find_all('a'):
				list.append(link.get('href')) 
			list_filter1 = filter(None, list)
			youtube_embed = [s for s in list_filter1 if re.search(youtube_pattern, s)]
			vimeo_embed = [s for s in list_filter1 if "vimeo.com" in s]
			for link in youtube_embed:
				youtube_link.setdefault(link, []) 
				youtube_link[link].append(item.html_url)
			for v_link in vimeo_embed:
				vimeo_link.setdefault(v_link, []) 
				vimeo_link[v_link].append(item.html_url)
			list2 = []
			for link in soup.find_all('iframe'):
				list2.append(link.get('src')) 
			list_filter2 = filter(None, list2)
			youtube_iframe = [s for s in list_filter2 if re.search(youtube_pattern, s)]
			vimeo_iframe = [s for s in list_filter2 if "vimeo.com" in s]
			for link in youtube_iframe:
				youtube_link.setdefault(link, [])
				youtube_link[link].append(item.html_url)
			for v_link in vimeo_iframe:
				vimeo_link.setdefault(v_link, [])
				vimeo_link[v_link].append(item.html_url)
			for video in soup.find_all('video'):
				instructure = video.get('class')
				media_id = video.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Video Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(assign_location)
			for audio in soup.find_all('audio'):
				instructure = audio.get('class')
				media_id = audio.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Audio Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(assign_location)
			for file_link in soup.find_all('a'):
				instructure = file_link.get('class')
				location = file_link.get('data-api-endpoint')
				if location:
					try:
						file_id = location.split('/')[-1:]
						r = requests.get(api_url + 'courses/%s/files/%s'% (course_id, file_id[0]), headers = {'Authorization': 'Bearer ' + '%s' % api_key})
						data_file = r.json()
						file_location = data_file['url'].split('?')[0]
						type = data_file['mime_class']
						if "audio" in type:
							link_name = "Linked Audio File: %s" % data_file['filename'], data_file['url']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(assign_location)
							link_media[link_name].append(file_location)
						if "video" in type:
							link_name = "Linked Video File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							media_link[m_link].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(assign_location)
							link_media[link_name].append(file_location)
						if "flash" in type.split('-')[-1:]:
							link_name = "Linked SWF File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(assign_location)
							link_media[link_name].append(file_location)
					except KeyError:
						pass
#checks all discuss in a canvas course for media links
discuss = course.get_discussion_topics()
if discuss:
	print "Checking Discussions"
	for item in discuss:
	#	print item.message
		if item.message:
			discuss_location = item.html_url
			contents = item.message.encode('utf-8')
			soup = BeautifulSoup (contents, "html.parser")
			list = []
			for link in soup.find_all('a'):
				list.append(link.get('href')) 
			list_filter1 = filter(None, list)
			youtube_embed = [s for s in list_filter1 if re.search(youtube_pattern, s)]
			vimeo_embed = [s for s in list_filter1 if "vimeo.com" in s]
			for link in youtube_embed:
				youtube_link.setdefault(link, [])
				youtube_link[link].append(item.html_url)
			for v_link in vimeo_embed:
				vimeo_link.setdefault(v_link, [])
				youtube_link[link].append(item.html_url)  
			list2 = []
			for link in soup.find_all('iframe'):
				list2.append(link.get('src')) 
			list_filter2 = filter(None, list2)
			youtube_iframe = [s for s in list_filter2 if re.search(youtube_pattern, s)]
			vimeo_iframe = [s for s in list_filter2 if "vimeo.com" in s]
			for v_link in vimeo_iframe:
				vimeo_link.setdefault(v_link, [])
				youtube_link[link].append(item.html_url)
			for video in soup.find_all('video'):
				instructure = video.get('class')
				media_id = video.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Video Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(discuss_location)
			for audio in soup.find_all('audio'):
				instructure = audio.get('class')
				media_id = audio.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':						
						m_link = "Audio Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].apppend(discuss_location)
			for file_link in soup.find_all('a'):
				instructure = file_link.get('class')
				location = file_link.get('data-api-endpoint')
				if location:
					try:
						file_id = location.split('/')[-1:]
						r = requests.get(api_url + 'courses/%s/files/%s'% (course_id, file_id[0]), headers = {'Authorization': 'Bearer ' + '%s' % api_key})
						data_file = r.json()
						file_location = data_file['url'].split('?')[0]
						if "audio" in type:
							link_name = "Linked Audio File: %s" %data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(discuss_location)
							link_media[link_name].append(file_location)
						if "video" in type:
							link_name = "Linked Video File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(discuss_location)
							link_media[link_name].append(file_location)
						if "flash" in type.split('-')[-1:]:
							link_name = "Linked SWF File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(discuss_location)
							link_media[link_name].append(file_location)
					except KeyError:
						pass
#checks the syllabus in a canvas course for media links
syllabus = canvas.get_course(course_id, include='syllabus_body')
if syllabus.syllabus_body:
	syllabus_location = '%s/%s/assignments/syllabus' %(courses_url, course_id)
	print "Checking Syllabus"
	try:
		contents = syllabus.syllabus_body
		soup = BeautifulSoup (contents, "html.parser")
		list = []
		for link in soup.find_all('a'):
			list.append(link.get('href')) 
		list_filter1 = filter(None, list)
		youtube_embed = [s for s in list_filter1 if re.search(youtube_pattern, s)]
		vimeo_embed = [s for s in list_filter1 if "vimeo.com" in s]
		for link in youtube_embed:
			youtube_link.setdefault(link, []) 
			youtube_link[link].append(syllabus_location)
		for v_link in vimeo_embed:
			vimeo_link.setdefault(v_link, []) 
			vimeo_link[v_link].append(syllabus_location)
		list2 = []
		for link in soup.find_all('iframe'):
			list2.append(link.get('src')) 
		list_filter2 = filter(None, list2)
		youtube_iframe = [s for s in list2 if re.search(youtube_pattern, s)]
		vimeo_iframe = [s for s in list2 if "vimeo.com" in s]
		for link in youtube_iframe:
			youtube_link.setdefault(link, [])
			youtube_link[link].append(syllabus_location)
		for v_link in vimeo_iframe:
			vimeo_link.setdefault(v_link, [])
			vimeo_link[v_link].append(syllabus_location)
		for video in soup.find_all('video'):
			instructure = video.get('class')
			media_id = video.get('data-media_comment_id')
			for media_comment in instructure:
				if media_comment == 'instructure_inline_media_comment':
					m_link = "Video Media Comment %s" % media_id
					media_link.setdefault(m_link, [])
					media_link[m_link].append("Manually Check for Captions")
					media_link[m_link].append('')
					media_link[m_link].append('')
					media_link[m_link].append('')
					media_link[m_link].append(syllabus_location)
		for audio in soup.find_all('audio'):
			instructure = audio.get('class')
			media_id = audio.get('data-media_comment_id')
			for media_comment in instructure:
				if media_comment == 'instructure_inline_media_comment':
					m_link = "Audio Media Comment %s" % media_id
					media_link.setdefault(m_link, [])
					media_link[m_link].append("Manually Check for Captions")
					media_link[m_link].append('')
					media_link[m_link].append('')
					media_link[m_link].append('')
					media_link[m_link].append(syllabus_location)
		for file_link in soup.find_all('a'):
			instructure = file_link.get('class')
			location = file_link.get('data-api-endpoint')
			if location:
				file_id = location.split('/')[-1:]
				r = requests.get(api_url + 'courses/%s/files/%s'% (course_id, file_id[0]), headers = {'Authorization': 'Bearer ' + '%s' % api_key})
				data_file = r.json()
				file_location = data_file['url'].split('?')[0]
				type = data_file['mime_class']
				if "audio" in type:
					link_name = "Linked Audio File: %s" % data_file['filename']
					link_media.setdefault(link_name, [])
					link_media[link_name].append(" ")
					link_media[link_name].append(" ")
					link_media[link_name].append(" ")
					link_media[link_name].append(syllabus_location)
					link_media[link_name].append(file_location)

				if "video" in type:
					link_name = "Linked Video File: %s" % data_file['filename']
					link_media.setdefault(link_name, [])
					link_media[link_name].append("Manually Check for Captions")
					link_media[link_name].append(" ")
					link_media[link_name].append(" ")
					link_media[link_name].append(" ")
					link_media[link_name].append(syllabus_location)
					link_media[link_name].append(file_location)
				if "flash" in type.split('-')[-1:]:
					link_name = "Linked SWF File: %s" % data_file['filename']
					link_media.setdefault(link_name, [])
					link_media[link_name].append("Manually Check for Captions")
					link_media[link_name].append(" ")
					link_media[link_name].append(" ")
					link_media[link_name].append(" ")
					link_media[link_name].append(syllabus_location)
					link_media[link_name].append(file_location)
	except KeyError:
		pass
#checks all module external URLs and Files in a canvas course for media links
modules = course.get_modules()
if modules:
	print "Checking Modules"
	for module in modules:
		items = module.list_module_items(include='content_details')
		for item in items:
			youtube_embed = []
			vimeo_embed = []
			if item.type == 'ExternalUrl':
				module_url = '%s/%s/modules/items/%s' %(courses_url, course_id, item.id)
				href = item.external_url.encode('utf8')
				if "youtube" in href or "youtu.be" in href:
					youtube_embed.append(href)
				if "vimeo" in href:
					vimeo_embed.append(href)
			for y_link in youtube_embed:
				youtube_link.setdefault(y_link, []) 
				youtube_link[y_link].append(module_url)
			for v_link in vimeo_embed:
				vimeo_link.setdefault(v_link, [])
				vimeo_link[v_link].append(module_url)
			if item.type == "File":
				try:
					module_location = item.html_url
					file_id = item.content_id
					r = requests.get(api_url + 'courses/%s/files/%s'% (course_id, file_id), headers = {'Authorization': 'Bearer ' + '%s' % api_key})
					data_file = r.json()
					type = data_file['mime_class']
					if "audio" in type:
						link_name = "Linked Audio File: %s" % data_file['filename']
						link_media.setdefault(link_name, [])
						link_media[link_name].append("Manually Check for Captions")
						link_media[link_name].append(" ")
						link_media[link_name].append(" ")
						link_media[link_name].append(" ")
						link_media[link_name].append(module_location)
						link_media[link_name].append(file_location)
					if "video" in type:
						link_name = "Linked Video File: %s" % data_file['filename']
						link_media.setdefault(link_name, [])
						link_media[link_name].append("Manually Check for Captions")
						link_media[link_name].append(" ")
						link_media[link_name].append(" ")
						link_media[link_name].append(" ")
						link_media[link_name].append(module_location)
						link_media[link_name].append(file_location)
					if "flash" in type.split('-')[-1:]:
						link_name = "Linked SWF File: %s" % data_file['filename']
						link_media.setdefault(link_name, [])
						link_media[link_name].append("Manually Check for Captions")
						link_media[link_name].append(" ")
						link_media[link_name].append(" ")
						link_media[link_name].append(" ")
						link_media[link_name].append(module_location)
						link_media[link_name].append(file_location)

				except KeyError:
					pass
#checks all announcements in a canvas course for media links
announce = course.get_discussion_topics(only_announcements=True)
if announce:
	print "Checking Announcements"
	for item in announce:
		announce_location = item.html_url
	#	print item.message
		if item.message:
			contents = item.message.encode('utf-8')
			soup = BeautifulSoup (contents, "html.parser")
			list = []
			for link in soup.find_all('a'):
				list.append(link.get('href')) 
			list_filter1 = filter(None, list)
			youtube_embed = [s for s in list_filter1 if re.search(youtube_pattern, s)]
			vimeo_embed = [s for s in list_filter1 if "vimeo.com" in s]
			for link in youtube_embed:
				youtube_link.setdefault(link, [])
				youtube_link[link].append(announce_location)
			for v_link in vimeo_embed:
				vimeo_link.setdefault(v_link, [])
				vimeo_link[v_link].append(announce_location)
			list2 = []
			for link in soup.find_all('iframe'):
				list2.append(link.get('src')) 
			list_filter2 = filter(None, list2)
			youtube_iframe = [s for s in list_filter2 if re.search(youtube_pattern, s)]
			vimeo_iframe = [s for s in list_filter2 if "vimeo.com" in s]
			for link in youtube_iframe:
				youtube_link.setdefault(link, [])
				youtube_link[link].append(announce_location)
			for v_link in vimeo_iframe:
				vimeo_link.setdefault(v_link, [])
				vimeo_link[v_link].append(announce_location)
			for video in soup.find_all('video'):
				instructure = video.get('class')
				media_id = video.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Video Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(announce_location)
			for audio in soup.find_all('audio'):
				instructure = audio.get('class')
				media_id = audio.get('data-media_comment_id')
				for media_comment in instructure:
					if media_comment == 'instructure_inline_media_comment':
						m_link = "Audio Media Comment %s" % media_id
						media_link.setdefault(m_link, [])
						media_link[m_link].append("Manually Check for Captions")
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append('')
						media_link[m_link].append(announce_location)
			for file_link in soup.find_all('a'):
				instructure = file_link.get('class')
				location = file_link.get('data-api-endpoint')
				if location:
					try:
						file_id = location.split('/')[-1:]
						r = requests.get(api_url + 'courses/%s/files/%s'% (course_id, file_id[0]), headers = {'Authorization': 'Bearer ' + '%s' % api_key})
						data_file = r.json()
						file_location = data_file['url'].split('?')[0]
						type = data_file['mime_class']
						if "audio" in type:
							link_name = "Linked Audio File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(announce_location)
							link_media[link_name].append(file_location)
						if "video" in type:
							link_name = "Linked Video File: %s" %data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(announce_location)
							link_media[link_name].append(file_location)
						if "flash" in type.split('-')[-1:]:
							link_name = "Linked SWF File: %s" % data_file['filename']
							link_media.setdefault(link_name, [])
							link_media[link_name].append("Manually Check for Captions")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(" ")
							link_media[link_name].append(announce_location)
							link_media[link_name].append(file_location)
					except KeyError:
						pass
#Uses YouTube API to check each video for captions
for key in youtube_link:
	if "playlist" in key:
		youtube_link[key].insert(0, 'this is a playlist, check individual videos')
	else:
		video_id = re.findall(youtube_pattern, key, re.MULTILINE | re.IGNORECASE)
		for item in video_id:
			is_ASR = False
			is_standard = False
			try:
				r = requests.get(google_url + '?part=snippet&videoId=' + item + '&key=' + youtube_key)
				data = r.json() 
				if data['items']:
					for e in data['items']:
						if e['snippet']['trackKind'] == "standard" and e['snippet']['language'] == "en":
							is_standard = True
						if e['snippet']['trackKind'] == "ASR" and e['snippet']['language'] == "en":
							is_ASR = True
					if is_standard == True:
							youtube_link[key].insert(0, "Captions found in English")
							youtube_link[key].insert(1, '')
							youtube_link[key].insert(2, '')
							youtube_link[key].insert(3, '')
					if is_standard == False and is_ASR == True:
						youtube_link[key].insert(0, "Automatic Captions in English")
						r = requests.get(google_video + '?part=contentDetails&id=' + item + '&key=' + youtube_key)
						data = r.json() 
						for d in data['items']:
							duration = d['contentDetails']['duration']
							if "H" in duration:
								hour, min_org = duration.split('H')
								min,sec = min_org.split('M')
								youtube_link[key].insert(1, hour[2:])
								youtube_link[key].insert(2, min)
								youtube_link[key].insert(3, sec[:-1])
							else:
								min, sec = duration.split('M')
								if min == None:
									youtube_link[key].insert(1, '0')
									youtube_link[key].insert(2, '0')
									youtube_link[key].insert(3, sec[:-1])
								else:
									youtube_link[key].insert(1, '0')
									youtube_link[key].insert(2, min[2:])
									youtube_link[key].insert(3, sec[:-1])
					if is_standard == False and is_ASR == False:
						youtube_link[key].insert(0, "No Captions in English")
						r = requests.get(google_video + '?part=contentDetails&id=' + item + '&key=' + youtube_key)
						data = r.json() 
						for d in data['items']:
							duration = d['contentDetails']['duration']
							if "H" in duration:
								hour, min_org = duration.split('H')
								min,sec = min_org.split('M')
								youtube_link[key].insert(1, hour[2:])
								youtube_link[key].insert(2, min)
								youtube_link[key].insert(3, sec[:-1])
							else:
								min, sec = duration.split('M')
								if min == None:
									youtube_link[key].insert(1, '0')
									youtube_link[key].insert(2, '0')
									youtube_link[key].insert(3, sec[:-1])
								else:
									youtube_link[key].insert(1, '0')
									youtube_link[key].insert(2, min[2:])
									youtube_link[key].insert(3, sec[:-1])
				if not data['items']:
					youtube_link[key].insert(0, "No Captions")
					r = requests.get(google_video + '?part=contentDetails&id=' + item + '&key=' + youtube_key)
					data = r.json() 
					for d in data['items']:
						duration = d['contentDetails']['duration']
						if "H" in duration:
							hour, min_org = duration.split('H')
							min,sec = min_org.split('M')
							youtube_link[key].insert(1, hour[2:])
							youtube_link[key].insert(2, min)
							youtube_link[key].insert(3, sec[:-1])
						else:
							min, sec = duration.split('M')
							if min == None:
								youtube_link[key].insert(1, '0')
								youtube_link[key].insert(2, '0')
								youtube_link[key].insert(3, sec[:-1])
							else:
								youtube_link[key].insert(1, '0')
								youtube_link[key].insert(2, min[2:])
								youtube_link[key].insert(3, sec[:-1])
			except KeyError:
				youtube_link[key].insert(0, "Unable to Check Youtube Video")
				youtube_link[key].insert(1, '')
				youtube_link[key].insert(2, '')
				youtube_link[key].insert(3, '')
#Uses Vimeo API to check videos for captions				
for link in vimeo_link:
	if "player" in link:
		split_link = link.split('/')
		if "?" in split_link[4]:
			video_link = split_link[4]
			split_link_question = video_link.split('?')
			video_id = split_link_question[0]
		else:
			video_id = split_link[4]
		try:
			r = requests.get('https://api.vimeo.com/videos/%s/texttracks' % video_id, headers = {'Authorization': 'Bearer ' + '%s' % vimeo_api_key})
			data = r.json()
			if not data['data']:
				vimeo_link[link].insert(0, 'No Captions')
				r = requests.get('https://api.vimeo.com/videos/%s' % video_id, headers = {'Authorization': 'Bearer ' + '%s' % vimeo_api_key})
				data = r.json()
				vimeo_duration = data['duration']
				hour, remainder = divmod(vimeo_duration, 3600)
				minute, second = divmod(remainder, 60)
				vimeo_link[link].insert(1, hour)
				vimeo_link[link].insert(2, minute)
				vimeo_link[link].insert(3, second)
			else:
				for d in data['data']:
					if d['language'] == 'en':
						vimeo_link[link].insert(0, 'Captions in English')
						vimeo_link[link].insert(1, '')
						vimeo_link[link].insert(2, '')
						vimeo_link[link].insert(3, '')
					else:
						vimeo_link[link].insert(0, 'No English Captions')
						r = requests.get('https://api.vimeo.com/videos/%s' % video_id, headers = {'Authorization': 'Bearer ' + '%s' % vimeo_api_key})
						data = r.json()
						vimeo_duration = data['duration']
						hour, remainder = divmod(vimeo_duration, 3600)
						minute, second = divmod(remainder, 60)
						vimeo_link[link].insert(1, hour)
						vimeo_link[link].insert(2, minute)
						vimeo_link[link].insert(3, second)
		except KeyError:
			vimeo_link[link].insert(0, 'Unable to Vimeo Check Video')
			vimeo_link[link].insert(1, '')
			vimeo_link[link].insert(2, '')
			vimeo_link[link].insert(3, '')
	else:
		split_link = link.split('/')
		video_id = split_link[-1]
		try:
			r = requests.get('https://api.vimeo.com/videos/%s/texttracks' % video_id, headers = {'Authorization': 'Bearer ' + '%s' % vimeo_api_key})
			data = r.json()
			if not data['data']:
				vimeo_link[link].insert(0, 'No Captions')
				r = requests.get('https://api.vimeo.com/videos/%s' % video_id, headers = {'Authorization': 'Bearer ' + '%s' % vimeo_api_key})
				data = r.json()
				vimeo_duration = data['duration']
				hour, remainder = divmod(vimeo_duration, 3600)
				minute, second = divmod(remainder, 60)
				vimeo_link[link].insert(1, hour)
				vimeo_link[link].insert(2, minute)
				vimeo_link[link].insert(3, second)
			else:
				for d in data['data']:
					if d['language'] == 'en':
						vimeo_link[link].insert(0, 'Captions in English')
					else:
						vimeo_link[link].insert(0, 'No English Captions')
						r = requests.get('https://api.vimeo.com/videos/%s' % video_id, headers = {'Authorization': 'Bearer ' + '%s' % vimeo_api_key})
						data = r.json()
						vimeo_duration = data['duration']
						hour, remainder = divmod(vimeo_duration, 3600)
						minute, second = divmod(remainder, 60)
						vimeo_link[link].insert(1, hour)
						vimeo_link[link].insert(2, minute)
						vimeo_link[link].insert(3, second)
		except KeyError:
			vimeo_link[link].insert(0, 'Unable to Check Vimeo Video')
writer.writerow(['Video URL', 'Caption Status', 'Hour', 'Minute', 'Second', 'Page Location', 'File Location'])
for key, value in youtube_link.items():
	writer.writerow([key] + value)
for key, value in vimeo_link.items():
	writer.writerow([key] + value)
for key, value in media_link.items():
	writer.writerow([key] + value)
for key, value in link_media.items():
	writer.writerow([key] + value)
done = time.time() - start_time
if done > 60:
	new_done = done / 60
	print "This request took " + str(new_done) + " minutes"
else: 	
	print "This request took " + str(done) + " seconds"