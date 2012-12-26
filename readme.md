Youtube Playlists For RRR Radio Programs
----------------------------------------

To listen to playlists from [RRR](http://www.rrr.org.au/ "102.7 FM in Melbourne") as a youtube playlist
visit [rrr.melb.playlists.unofficial](http://www.youtube.com/channel/UCBAHkGQ_pUcp-TnoLIyRR6A/videos?sort=dd&flow=list&view=1)
on youtube. Currently only the [Beat Orgy](http://www.rrr.org.au/program/beat-orgy/) program has been converted (see Future section below).

The Code
--------

The code in this repository is a scraper and parser, which create the youtube playlists in the link
above from the data on the RRR website. Chances are very high you don't want or need to run this code
if you just want to listen to music from RRR with videos.

If you do want to run the code, create a file called `credentials` in the root directory and put the following details in:

    {
    	"client_id": "YOUR_GOOGLE_APP_CLIENT_KEY",
    	"developer_key": "YOUR_GOOGLE_APP_DEVELOPER_KEY",
    	"email": "YOUR_YOUTUBE_EMAIL",
    	"password": "YOUR_YOUTUBE_PASSWORD",
    	"source": "is_left_as_an_empty_string"
    }

These credentials allow the script to access your youtube account and create the playlists.

Disclaimer
----------

I have no affiliation with RRR and do not make any money from this. I did this in my time off work
because I wanted to be able to play videos with music at parties and the RRR playlists are awesome.

If you can think of a way to monetise this I will be more than happy to implement it and donate the
revenue to RRR.

Future
------

Currently only Beat Orgy has been converted into youtube playlists. Other programs may be converted in
the future, pending a more stable internet connection (I currently only have mobile broadband, thanks to
slow Telstra connection of my broadband service).
