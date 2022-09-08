"""

Revision ID: 27e4d084fc09
Revises: 0420_add_redacted_template
Create Date: 2022-08-22 20:58:36.856950

"""
import uuid

import sqlalchemy as sa
from alembic import op

revision = "27e4d084fc09"
down_revision = "0420_add_redacted_template"


def upgrade():
    op.execute(
        "INSERT INTO provider_details \
        (id, display_name, identifier, priority, notification_type, active, version, supports_international) \
        VALUES \
        ('{}', 'SendInBlue Email', 'sib_email', 5, 'email', true, 1, true), \
        ('{}', 'SendInBlue SMS', 'sib_sms', 5, 'sms', true, 1, true)".format(
            str(uuid.uuid4()), str(uuid.uuid4())
        )
    )

    # d6aa2c68-a2d9-4437-ab19-3ae8eb202553 is our default service
    op.execute(
        "UPDATE services SET \
        name = 'Notifications', \
        email_from = 'notifications', \
        default_branding_is_french = TRUE \
        WHERE id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'"
    )

    op.execute(
        "UPDATE service_sms_senders SET \
        sms_sender = 'BetaGouv' \
        WHERE service_id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'"
    )


def downgrade():
    op.execute("DELETE FROM provider_details WHERE identifier IN ('sib_email', 'sib_sms')")

    # d6aa2c68-a2d9-4437-ab19-3ae8eb202553 is our default service
    op.execute(
        "UPDATE services SET \
        name = 'Notification', \
        email_from = 'notification', \
        default_branding_is_french = FALSE \
        WHERE id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'"
    )

    op.execute(
        "UPDATE service_sms_senders SET \
        sms_sender = 'GOVUK' \
        WHERE service_id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'"
    )
