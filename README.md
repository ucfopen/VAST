# VAST (Video Accessibility Scanning Tool)
VAST is a Python script that searches an Instructure Canvas course for media and returns results in a CSV file.

## Requirements
* Python 2.7
* YouTube API Key
* Vimeo API Key

## Installation
* Install all dependencies by using `pip install -r requirements.txt`
* Create a config file by copying the template: `cp vast_config.template.py vast_config.py`
* Supply the following in vast_config.py:
    * api_key (Canvas API Key. **Note**: To scan a course you are not enrolled in, you must provide a sub-account or admin level api key to access other courses)
    * api_url (Canvas URL and API e.g. https://example.instructure.com/api/v1/)
    * youtube_apikey (obtain from https://console.developers.google.com/)
    * vimeo_apikey (obtain from https://developer.vimeo.com/apps. Only public and private access is needed.)
    * courses_url (e.g. https://example.instructure.com/courses)

## Testing
A free test course is provided in Canvas Commons. Search for **VAST Test Course** in Canvas Commons. Directions for searching Canvas Commons are located at https://community.canvaslms.com/docs/DOC-11177-38287725291

## Types of Media
VAST will identify the following types of media:
* YouTube videos (iframe and links)
* Vimeo videos (iframe and links)
* Video files linked from the Rich Content Editor
* Audio files linked from the Rich Content Editor
* SWF  files linked from the Rich Content Editor
* Media comments in the Rich Content Editor
* Links from video providers:
    * Films on Demand
    * Alexander Street Press
    * Kanopy
* Note: VAST relies on the mime type of the file provided by Canvas

## Customization of Video Provider Links
Update the lib_media_urls list in the vast_config.py file to include additional sources of video. These links will be contained in the report and not checked automatically for captions. For instance, to check any videos from daily motion, add 'dailymotion.com' to the end of the list.

* **Example**: lib_media_urls = ['fod.infobase.com', 'search.alexanderstreet.com', 'kanopystreaming-com', **'dailymotion.com'**]

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
5. The report will be saved in the same directory as the vast.py script. The file name will be the course name.

## Contributors

Project Lead
John Raible

Contributors
Matt Emond