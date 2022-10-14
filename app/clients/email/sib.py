import sib_api_v3_sdk
from flask import current_app
from sib_api_v3_sdk.rest import ApiException

from app.clients.email import EmailClient


class SendInBlueEmailClient(EmailClient):
    """
    A SendInBlue email client
    """

    def init_app(self, app, *args, **kwargs):
        configuration = sib_api_v3_sdk.Configuration()

        configuration.api_key["api-key"] = app.config.get('SIB_API_KEY')

        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    @property
    def name(self):
        return "sib_email"

    def send_email(
        self,
        source,
        to_addresses,
        subject,
        body,
        html_body="",
        reply_to_address=None,
        attachments=None,
    ):
        # Note: we don't support attachments yet.

        # Note: the original AWS SES email client from CDS sends
        # multipart emails whereas we don't. We should probably look
        # into it thought I'm not sure SendInBlue allows any of
        # it. Here's the note from the AWS SES client:

        # - If sending a TXT email without attachments:
        #   => Multipart mixed
        #
        # - If sending a TXT + HTML email without attachments:
        #   => Multipart alternative
        #
        # - If sending a TXT + HTML email with attachments
        # =>  Multipart Mixed (enclosing)
        #       - Multipart alternative
        #         - TXT
        #         - HTML
        #       - Attachment(s)

        current_app.logger.info("SendInBlue email to {}".format(to_addresses))

        sender = sib_api_v3_sdk.SendSmtpEmailSender(name='Stéphane Maniaci', email='stephane.maniaci@beta.gouv.fr')
        to = [sib_api_v3_sdk.SendSmtpEmailTo(email=to_addresses)]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            text_content=body,
            html_content=html_body,
            subject=subject
        )

        try:
            # Send a transactional email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            current_app.logger.info("SendInBlue request finished: {}".format(api_response))
        except ApiException as err:
            current_app.logger.error("SendInBlue request failed: {}".format(err))
