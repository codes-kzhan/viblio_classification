from BeautifulSoup import BeautifulSoup
import re
import urllib
import gdata.youtube
import gdata.youtube.service

class VideoUrls():
    def __init__(self):
        self.root_url = ''
        self.video_urls = []
        
    def search(self, query):
        pass 
    def get_urls(self):
        return self.video_urls
    def get_vid_duration(self):
        return self.vid_duration
    def get_nvids_found(self):
        return len(self.video_urls)

class YouTubeVideoUrls(VideoUrls):
    
    def search(self, query,min_duration=20,max_duration=180, max_videos=950):
        
        if max_videos < 20:
            print "Maximum videos for YouTube Search must be at least 20, setting to 20"
            max_videos = 20

        yt_service = gdata.youtube.service.YouTubeService()
        ytquery = gdata.youtube.service.YouTubeVideoQuery()
        ytquery.vq = query
        ytquery.orderby = 'relevance'
        #ytquery.racy = 'include'
        max_results = 10 # There was a reason left as 10....to have more url possible on youtube! do not change it.
        max_num_videos_allowed_in_youtube = max_videos
        ytquery.max_results = max_results
        start_index = range( 1, max_results, max_num_videos_allowed_in_youtube-max_results-1 )
        self.video_urls = []
        self.vid_duration=[]
        for s in start_index:    
            ytquery.start_index = s
            try:
                feed = yt_service.YouTubeQuery(ytquery)
                for entry in feed.entry:
                    video_duration= int(entry.media.duration.seconds)
                    cur_url = entry.GetSwfUrl()
                    if cur_url and video_duration<max_duration and video_duration>min_duration :
                        self.video_urls.append(cur_url)
                        self.vid_duration.append(video_duration)
                        #print cur_url
            except:
                pass
        
