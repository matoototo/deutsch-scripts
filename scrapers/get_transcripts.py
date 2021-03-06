import json
import argparse
import pathlib
from pyyoutube import Api
from youtube_transcript_api import YouTubeTranscriptApi

parser = argparse.ArgumentParser(description='Gets manual German transcripts of every video from a given channel name.')
parser.add_argument('-i', metavar='id', type=str, help='channel name', required=True)
parser.add_argument('-o', metavar='filepath', type=pathlib.Path, help='filepath pointing to the output JSON file', required=True)
parser.add_argument('-k', metavar='api_key', type=str, help='google API key', required=True)

args = parser.parse_args()
channel_name = args.i
out_filename = args.o
API_KEY = args.k

api = Api(api_key=API_KEY)

channel_res = api.get_channel_info(channel_name=channel_name)
playlist_id = channel_res.items[0].contentDetails.relatedPlaylists.uploads
playlist_res = api.get_playlist_items(playlist_id=playlist_id, count = None)

videos = []
for i, video in enumerate(playlist_res.items):
    if i%10 == 0:
        print(i, '/', len(playlist_res.items))

    try:
        transcript = YouTubeTranscriptApi.list_transcripts(video.contentDetails.videoId).find_manually_created_transcript(['de']).fetch()
    except:
        continue # No manual transcript found

    transcript = ' '.join(list(map(lambda x : x['text'].replace('\n', ' '), transcript)))
    videos.append({'title': video.snippet.title, 'id': video.contentDetails.videoId,
                  'transcript': transcript})

json.dump(videos, open(out_filename, 'w'), separators=(',', ': '), indent=4)
