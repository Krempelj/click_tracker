import endpoints
from models import *
from messages import *
from protorpc import remote
from google.appengine.api import memcache

from functools import wraps
import hashlib
import base64
import re
import logging


def auth(fun):
    @wraps(fun)
    def inner(*args):
        basic_auth = args[0].request_state.headers.get('authorization')
        if basic_auth:
            auth_type, credentials = basic_auth.split(' ')
            username, password = base64.b64decode(credentials).split(':')
            # test account credentials; username: 'matej', password: 'stolfa'
            if hashlib.md5(username).hexdigest() == '485c859f2df22f1147ba3798b4485d48' and hashlib.md5(
                    password).hexdigest() == '22761e242a12d5c0992061cbd6364b12':
                return fun(*args)
        raise endpoints.UnauthorizedException('Invalid credentials.')

    return inner


def validate_url(url):
    regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain ...
            r'localhost|'  # localhost ...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ... or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


def validate_platforms(lst):
    if len(lst) < 1:
        return False
    for platform in lst:
        if platform not in TARGET_PLATFORMS:
            return False
    return True


def date_time_string(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M')


def make_campaign_response(campaign):
    platform_list = []
    for platform in campaign.platforms:
        platform_list.append(PlatformResponse(platform=platform.platform,
                                              clicks=platform.clicks, enabled=platform.enabled))
    return CampaignResponse(
        id=campaign.id, redirect_url=campaign.redirect_url,
        platforms=platform_list,
        created_at=date_time_string(campaign.created_at), updated_at=date_time_string(campaign.updated_at)
    )


@endpoints.api(name='admin', version='v1', description='Admin API')
class AdminApi(remote.Service):
    @auth
    @endpoints.method(CampaignInsertRequest, CampaignResponse,
                      path='campaign',
                      http_method='POST',
                      name='campaign.insert')
    def campaign_create_update(self, request):
        campaign_id = request.id
        redirect_url = request.redirect_url
        platforms = list(set(request.platforms))  # distinct list

        if not validate_url(redirect_url):
            raise endpoints.BadRequestException('Invalid url.')

        if not validate_platforms(platforms):
            raise endpoints.BadRequestException(
                    'One ore more invalid platforms provided. ' +
                    'Available platforms: ' + str(TARGET_PLATFORMS))

        if not campaign_id:
            raise endpoints.BadRequestException('Please provide a (campaign) id.')

        campaign = Campaign.create_update(campaign_id, redirect_url, platforms)
        if not campaign:
            raise endpoints.InternalServerErrorException('DataStore error.')

        return make_campaign_response(campaign)

    RESOURCE_ID = endpoints.ResourceContainer(
        message_types.VoidMessage,
        id=messages.StringField(2, variant=messages.Variant.STRING, required=True)
    )

    @auth
    @endpoints.method(RESOURCE_ID, CampaignDeleteMessage,
                      path='campaign/{id}',
                      http_method='DELETE',
                      name='campaign.delete')
    def campaign_delete(self, request):
        key = Campaign.get_key(request.id)
        campaign = key.get()
        if not campaign:
            raise endpoints.BadRequestException('No such campaign id.')
        key.delete()
        return CampaignDeleteMessage(id=request.id)

    @auth
    @endpoints.method(RESOURCE_ID, CampaignResponse,
                      path='campaign/{id}',
                      http_method='GET',
                      name='campaign.get')
    def campaign_info(self, request):
        campaign = Campaign.get_key(request.id).get()
        if not campaign:
            raise endpoints.BadRequestException('No such campaign id.')
        return make_campaign_response(campaign)

    RESOURCE_PLATFORM = endpoints.ResourceContainer(
        message_types.VoidMessage,
        platform=messages.StringField(2, variant=messages.Variant.STRING, required=True)
    )

    @auth
    @endpoints.method(RESOURCE_PLATFORM, CampaignMultiResponse,
                      path='campaign/on/{platform}',
                      http_method='GET',
                      name='campaign.get_on_platform')
    def campaigns_on_platforms(self, request):
        if not validate_platforms([request.platform]):
            raise endpoints.BadRequestException('Please specify a valid platform: ' + str(TARGET_PLATFORMS))
        campaigns = Campaign.query(Campaign.platforms.platform == request.platform).fetch()

        campaigns_message_list = []
        for model_instance in campaigns:
            campaigns_message_list.append(
                make_campaign_response(model_instance)
            )

        return CampaignMultiResponse(campaigns=campaigns_message_list)

    RESOURCE_CLICKS_CAMPAIGN_PLATFORM = endpoints.ResourceContainer(
        message_types.VoidMessage,
        campaign=messages.StringField(1, variant=messages.Variant.STRING, required=True),
        platform=messages.StringField(2, variant=messages.Variant.STRING, required=True)
    )

    @auth
    @endpoints.method(RESOURCE_CLICKS_CAMPAIGN_PLATFORM, ClicksOnCampaignPlatformResponse,
                      path='campaign/clicks/{campaign}/{platform}',
                      http_method='GET',
                      name='campaign.campaign_clicks_on_platform')
    def campaign_clicks_on_platform(self, request):
        if not request.campaign or not request.platform:
            raise endpoints.BadRequestException('Invalid input.')

        campaign = Campaign.get_key(request.campaign).get()
        if not campaign:
            raise endpoints.NotFoundException('No campaign with such id.')

        found = False
        clicks = 0
        enabled = None
        for platform in campaign.platforms:
            if platform.platform == request.platform:  # show also disabled platforms
                found = True
                clicks = platform.clicks
                enabled = platform.enabled

        if not found:
            raise endpoints.NotFoundException('Campaign "' + campaign.id +
                                              '" does not have "' + request.platform +
                                              '" specified as a target platform.')

        return ClicksOnCampaignPlatformResponse(campaign=campaign.id,
                                                platform=request.platform,
                                                enabled=enabled,
                                                clicks=clicks)

    @auth
    @endpoints.method(RESOURCE_PLATFORM, ClicksOnPlatformResponse,
                      path='campaign/clicks/{platform}',
                      http_method='GET',
                      name='campaign.clicks_on_platform')
    def clicks_on_platform(self, request):  # NDB takes care of caching with memcache by itself
        if not request.platform:
            raise endpoints.BadRequestException('Please provide a platform.')

        # memcache_key = None
        found = False
        for num in range(0, len(TARGET_PLATFORMS)):
            if TARGET_PLATFORMS[num] == request.platform:
                found = True
                # memcache_key = MEMCACHE_KEYS[num]

        if not found:
            raise endpoints.BadRequestException('Please provide a valid platform: ' + str(TARGET_PLATFORMS))

        # clicks = memcache.get(memcache_key)
        # if clicks is None:
            # query for results

        clicks = 0
        for campaign in Campaign.query():
            for platform in campaign.platforms:
                if platform.platform == request.platform:
                    clicks += platform.clicks

            # if not memcache.add(memcache_key, clicks, time=3600):
            #     logging.error('Memcache set failed!')

        return ClicksOnPlatformResponse(platform=request.platform, clicks=clicks)


api = endpoints.api_server([AdminApi])
