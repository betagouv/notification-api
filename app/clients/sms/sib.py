from pprint import pprint

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.clients.sms import SmsClient


class SendInBlueSMSClient(SmsClient):
    """
    A SendInBlue SMS client
    """

    def init_app(self, app, *args, **kwargs):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = app.config["SIB_API_KEY"]

        self.api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))
        super(SmsClient, self).__init__(*args, **kwargs)

        self.name = "sib_sms"

    def get_name(self):
        return self.name

    def send_sms(self, to, content, reference, multi=True, sender="Steph Test API"):
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(sender=sender, recipient=to, content=content, type="transactional")

        try:
            api_response = self.api_instance.send_transac_sms(send_transac_sms)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling TransactionalSMSApi->send_transac_sms: %s\n" % e)
