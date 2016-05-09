from protorpc import message_types
from protorpc import messages


class CampaignInsertRequest(messages.Message):
    id = messages.StringField(1, required=True)
    redirect_url = messages.StringField(2, required=True)
    platforms = messages.StringField(3, repeated=True)


class PlatformResponse(messages.Message):
    platform = messages.StringField(1, required=True)
    clicks = messages.IntegerField(2, required=True)
    enabled = messages.BooleanField(3, required=True)


class CampaignResponse(messages.Message):
    id = messages.StringField(1, required=True)
    redirect_url = messages.StringField(2, required=True)
    platforms = messages.MessageField(PlatformResponse, 3, repeated=True)
    created_at = messages.StringField(4, required=True)
    updated_at = messages.StringField(5, required=True)


class CampaignMultiResponse(messages.Message):
    campaigns = messages.MessageField(CampaignResponse, 1, repeated=True)


class CampaignDeleteMessage(messages.Message):
    id = messages.StringField(1, required=True)


class ClicksOnCampaignPlatformResponse(messages.Message):
    campaign = messages.StringField(1, required=True)
    platform = messages.StringField(2, required=True)
    enabled = messages.BooleanField(3, required=True)
    clicks = messages.IntegerField(4, required=True)


class ClicksOnPlatformResponse(messages.Message):
    platform = messages.StringField(1, required=True)
    clicks = messages.IntegerField(2, required=True)
