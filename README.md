# VAST (Video Accessibility Scanning Tool)
VAST is a Python script that searches an Instructure Canvas course for media and returns results in a CSV file.

## Installation
* Install all dependencies by using pip install -r https://***REMOVED***/john.raible/course-media-search-tool-V2/requirements.txt
* Make sure vast.py and vast_config.py are in same location

## Requirements
* Python 2.7
* YouTube API Key
* Vimeo API Key

## Types of Media
VAST will identify the following types of media:
* YouTube videos (iframe and links)
* Vimeo videos (iframe and links)
* Video files linked from the Rich Content Editor
* Audio files linked from the Rich Content Editor
* SWF  files linked from the Rich Content Editor
* Media comments in the Rich Content Editor
* Links from video providers:
⋅⋅* Films on Demand
⋅⋅* Alexander Street Press
⋅⋅* Kanopy
Note: VAST relies on the mime type of the file provided by Canvas

## Limitations
* VAST does not check the Quizzes tool
* VAST can not determine if captions exist on video file, audio files, swf files, media comments, or video providers. The report will list the location of the file to check manually and provide a download link. Make sure to be logged into Canvas first; unless the download link will not work.
* VAST may not be able to check all YouTube or Vimeo videos for captions. If it can't, the report will note so.

## Windows Compatibility
VAST is designed to be used as a desktop utility on Mac or Linux. To run on Windows, backslashes will have be changed to forwardslashes in the the file paths.

## Use
1. Open up a terminal window
2. Go to the directory containing vast.py (use cd command)
3. Type "python vast.py"
4. Enter the Canvas course id number e.g.(**1234567** from https://example.instructure.com/courses/**1234567**)
5. The report will be saved in the same directory as the vast.py script