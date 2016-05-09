**************************************************
Application, build and deployment
**************************************************

My app is available at http://click-tracker-1301.appspot.com/
unless it is temporary offline because of my trial version of Google Cloud Platform.

It exposes two APIs. The Admin API is implemented with Cloud Endpoints, on the other hand, the Tracker API
is implemented as an webapp2 WSGI application, which enables HTTP redirection.

The app can be deployed using GAE through command line with 
"{google_appengine_folder}/appcfg.py -A {application-id} -V v1 update {path_to_my_folder}\click_tracker".
An easier way is to deploy it with Google App Engine Launcher.


**************************************************
NDB Models
**************************************************
	The API is simple enough to have only one DataStore entity (Campaign).
	
	
**************************************************
Admin API Authentication
**************************************************	
	It uses basic authentication which is secure in conjunction with the confidentiality SSL provides.
	Google Cloud Endpoints uses SSL exclusively. Each method call requires the "Authorization header".

	generic redentials:
		username: 'matej'
		password: 'stolfa'

**************************************************
API Testing
**************************************************
I suggest using 'Postman' (REST Client) to test the APIs:
https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop

Make sure you set
	- Content-Type header = application/json
	- Authorization = Basic bWF0ZWpzOnN0b2xmYQ==
	
- select 'raw' option
- send JSON to the API methods

**************************************************
Examples
**************************************************
DESC: insert or update a campaign
METHOD: admin.campaign.insert [POST]
PATH: https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign
INPUT:
{
    "id": "TalkingTomCat",
    "redirect_url": "https://www.youtube.com/user/TalkingTomCat",
    "platforms": [
            "Android",
            "Iphone",
            "WindowsPhone"
        ]
    
}

OUTPUT:
{
  "platforms": [
    {
      "platform": "WindowsPhone",
      "enabled": true,
      "clicks": "0"
    },
    {
      "platform": "Android",
      "enabled": true,
      "clicks": "0"
    },
    {
      "platform": "IPhone",
      "enabled": true,
      "clicks": "0"
    }
  ],
  "created_at": "2016-05-09 19:40",
  "updated_at": "2016-05-09 19:41",
  "redirect_url": "https://www.youtube.com/user/TalkingTomCat",
  "id": "TalkingTomCat",
  "kind": "admin#campaignItem",
  "etag": "\"9ffFBMl9VjqXYgiVeXwUEuoxdJk/-kZE8H6Kfnr7blkDeBY6AHQkXzA\""
}
**************************************************
DESC: get a specific campaign info
METHOD: admin.campaign.get [GET]
PATH: https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/TalkingTomCat
	  https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/{campaign_id}
INPUT:
none

OUTPUT:
{
  "platforms": [
    {
      "platform": "WindowsPhone",
      "enabled": true,
      "clicks": "0"
    },
    {
      "platform": "Android",
      "enabled": true,
      "clicks": "0"
    },
    {
      "platform": "IPhone",
      "enabled": true,
      "clicks": "0"
    }
  ],
  "created_at": "2016-05-09 19:40",
  "updated_at": "2016-05-09 19:41",
  "redirect_url": "https://www.youtube.com/user/TalkingTomCat",
  "id": "TalkingTomCat",
  "kind": "admin#campaignItem",
  "etag": "\"9ffFBMl9VjqXYgiVeXwUEuoxdJk/-kZE8H6Kfnr7blkDeBY6AHQkXzA\""
}
**************************************************
DESC: delete a specific campaign
METHOD: admin.campaign.delete [DELETE]
PATH: https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/TalkingTomCat
	  https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/{campaign_id}
INPUT:

OUTPUT:
{
  "id": "TalkingTomCat",
  "kind": "admin#campaignItem",
  "etag": "\"9ffFBMl9VjqXYgiVeXwUEuoxdJk/Bvl8sh8ebIaMkZZxAUpPB3eNVAE\""
}
**************************************************
DESC: get campaigns on a specific platform
METHOD:  admin.campaign.get_on_platform [GET]
PATH: https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/on/Android
	  https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/on/{Platform}
INPUT:

OUTPUT:
{
  "campaigns": [
    {
      "platforms": [
        {
          "platform": "WindowsPhone",
          "enabled": true,
          "clicks": "0"
        },
        {
          "platform": "Android",
          "enabled": true,
          "clicks": "0"
        },
        {
          "platform": "IPhone",
          "enabled": true,
          "clicks": "0"
        }
      ],
      "created_at": "2016-05-09 19:54",
      "updated_at": "2016-05-09 19:54",
      "redirect_url": "http://outfit7.com/apps/my-talking-angela/",
      "id": "TalkingAngelaCat"
    },
    {
      "platforms": [
        {
          "platform": "WindowsPhone",
          "enabled": true,
          "clicks": "0"
        },
        {
          "platform": "Android",
          "enabled": true,
          "clicks": "0"
        },
        {
          "platform": "IPhone",
          "enabled": true,
          "clicks": "0"
        }
      ],
      "created_at": "2016-05-09 19:53",
      "updated_at": "2016-05-09 19:53",
      "redirect_url": "https://www.youtube.com/user/TalkingTomCat",
      "id": "TalkingTomCat"
    }
  ],
  "kind": "admin#campaignItem",
  "etag": "\"9ffFBMl9VjqXYgiVeXwUEuoxdJk/-u1h8dsZeLJxjtt9qQiktVElo2I\""
}
**************************************************
DESC: get all clicks on a platform
METHOD: admin.campaign.clicks_on_platform [GET]
PATH: https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/clicks/Android
	  https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/clicks/{platform}
INPUT:

OUTPUT:
{
  "platform": "Android",
  "clicks": "2",
  "kind": "admin#campaignItem",
  "etag": "\"9ffFBMl9VjqXYgiVeXwUEuoxdJk/-eeNvc6TKEu1K67dDgYUxbo6khM\""
}
**************************************************
DESC: get all campaign clicks on a platform
METHOD:  admin.campaign.campaign_clicks_on_platform [GET]
PATH: https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/clicks/TalkingAngelaCat/Android
	  https://click-tracker-1301.appspot.com/_ah/api/admin/v1/campaign/clicks/{campaign_id}/{platform}
INPUT:

OUTPUT:
{
  "platform": "Android",
  "enabled": true,
  "clicks": "2",
  "campaign": "TalkingAngelaCat",
  "kind": "admin#campaignItem",
  "etag": "\"9ffFBMl9VjqXYgiVeXwUEuoxdJk/IzxWSX-07IGLEbSUz1UMyFv88V8\""
}
**************************************************
Tracker API
**************************************************
DESC: required parameters: 'id' and 'platform'
METHOD: [GET]
PATH: http://click-tracker-1301.appspot.com/tracker?id=TalkingAngelaCat&platform=Android
	  http://click-tracker-1301.appspot.com/tracker?id={campaign_id}&platform={platform}
INPUT:

OUTPUT:
Redirects the user appropriately.
