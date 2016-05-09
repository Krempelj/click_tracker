import unittest
import logging

from google.appengine.ext import ndb
from google.appengine.ext import testbed


TARGET_PLATFORMS = ['Android', 'IPhone', 'WindowsPhone']
MEMCACHE_KEYS = ['clicks_android', 'clicks_iphone', 'clicks_wp']


class Platform(ndb.Model):
    platform = ndb.StringProperty(required=True, choices=TARGET_PLATFORMS)
    clicks = ndb.IntegerProperty(default=0, indexed=False)
    enabled = ndb.BooleanProperty(default=True)


class Campaign(ndb.Model):
    id = ndb.StringProperty(required=True)
    redirect_url = ndb.StringProperty(required=True, indexed=False)

    platforms = ndb.StructuredProperty(Platform, repeated=True)

    created_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    updated_at = ndb.DateTimeProperty(indexed=False, auto_now=True)

    @classmethod
    def _get_kind(cls):
        return 'Campaign'

    @classmethod
    def get_key(cls, campaign_id):
        return ndb.Key(cls._get_kind(), campaign_id)

    @staticmethod
    def make_platform_list(lst):
        platform_list = []
        for platform in lst:
            platform_list.append(Platform(platform=platform))
        return platform_list

    def update_platforms(self, lst):  # preserves clicks if a platform gets removed
        new_platform_list = []
        not_found_new_elts = []
        not_found_old_elts = []

        for elt in lst:  # find new platforms to insert
            found = False
            for platform in self.platforms:
                if platform.platform == elt:
                    # append matched ones
                    new_platform_list.append(Platform(platform=platform.platform,
                                                      clicks=platform.clicks, enabled=True))
                    found = True
                    break
            if not found:
                not_found_new_elts.append(elt)

        for elt in self.platforms:
            found = False
            for platform in lst:
                if platform == elt.platform:
                    found = True
                    break
            if not found:
                not_found_old_elts.append(elt)

        for elt in not_found_new_elts:  # enable new platforms
            new_platform_list.append(Platform(platform=elt))

        for elt in not_found_old_elts:  # disable old platforms
            new_platform_list.append(Platform(platform=elt.platform, clicks=elt.clicks, enabled=False))

        return new_platform_list

    @classmethod
    def create_update(cls, campaign_id, redirect_url, enabled_platforms):
        try:
            # check if exists
            campaign = Campaign.get_key(campaign_id).get()
            if campaign:  # update
                campaign.id = campaign_id
                campaign.redirect_url = redirect_url
                # preserve click data
                campaign.platforms = cls.update_platforms(campaign, enabled_platforms)
                key = campaign.put()
                campaign = key.get()
            else:  # create
                campaign = cls(key=cls.get_key(campaign_id),
                               id=campaign_id,
                               redirect_url=redirect_url,
                               platforms=cls.make_platform_list(enabled_platforms))

                campaign.put()
            return campaign

        except Exception, e:
            logging.error(e)
            return None


class DataStoreTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    @staticmethod
    def getEnabled(campaign, platform_name):
        for platform in campaign.platforms:
            if platform.platform == platform_name:
                return platform.enabled
        return None

    def testPreserveTags(self):
        Campaign.create_update("Campaign_1",
                               "https://www.youtube.com/user/TalkingTomCat",
                               ['Android'])

        campaign = Campaign.create_update("Campaign_1",
                                          "https://www.youtube.com/user/TalkingTomCat",
                                          ['Android'])

        self.assertEqual(True, self.getEnabled(campaign, 'Android'))  # no change

        campaign = Campaign.create_update("Campaign_1",
                                          "https://www.youtube.com/user/TalkingTomCat",
                                          ['WindowsPhone'])

        self.assertEqual(False, self.getEnabled(campaign, "Android"))  # android deactivated
        self.assertEqual(True, self.getEnabled(campaign, "WindowsPhone"))  # wp activated (added)

        campaign = Campaign.create_update("Campaign_1",
                                          "https://www.youtube.com/user/TalkingTomCat",
                                          ['Android', 'IPhone'])

        self.assertEqual(True, self.getEnabled(campaign, "Android"))  # android activated
        self.assertEqual(True, self.getEnabled(campaign, "IPhone"))  # IPhone activated (added)
        self.assertEqual(False, self.getEnabled(campaign, "WindowsPhone"))  # wp deactivated

        campaign = Campaign.create_update("Campaign_1",
                                          "https://www.youtube.com/user/TalkingTomCat",
                                          ['Android', 'IPhone', 'WindowsPhone'])

        self.assertEqual(True, self.getEnabled(campaign, "Android"))  # android activated
        self.assertEqual(True, self.getEnabled(campaign, "IPhone"))  # IPhone activated (added)
        self.assertEqual(True, self.getEnabled(campaign, "WindowsPhone"))  # wp activated


if __name__ == '__main__':
    unittest.main()
