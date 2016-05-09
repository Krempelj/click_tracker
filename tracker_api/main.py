import webapp2
from admin_api.models import *


REDIRECT_LINK = 'http://outfit7.com'


class Tracker(webapp2.RequestHandler):
    def get(self):
        campaign_id = self.request.get('id')
        platform = self.request.get('platform')

        if not campaign_id or not platform:
            return self.redirect(REDIRECT_LINK)

        campaign = Campaign.get_key(campaign_id).get()  # strong consistency
        if not campaign:
            return self.redirect(REDIRECT_LINK)

        index = -1
        valid_platform = False
        for num in range(0, len(campaign.platforms)):
            if campaign.platforms[num].platform == platform and campaign.platforms[num].enabled:
                valid_platform = True
                index = num
                break
        if not valid_platform:
            return self.redirect(REDIRECT_LINK)

        # save click
        # ndb.Key.get() method guarantee strong consistency
        campaign.platforms[index].clicks += 1
        campaign.put()

        # could put a click entity here

        self.redirect(str(campaign.redirect_url))


app = webapp2.WSGIApplication(
        [
            webapp2.Route(r'/tracker', methods=['GET'], handler=Tracker)
        ], config={}, debug=True)
