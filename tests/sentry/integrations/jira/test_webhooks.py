from __future__ import absolute_import

import json

from mock import patch

from django.core.urlresolvers import reverse

from sentry.models import Integration
from sentry.testutils import APITestCase


SAMPLE_EDIT_ISSUE_PAYLOAD_NO_ASSIGNEE = """
{
    "changelog": {
        "items": [{
            "to": "admin",
            "field": "assignee",
            "toString": "Jess MacQueen",
            "from": null,
            "fromString": null,
            "fieldtype": "jira",
            "fieldId": "assignee"
        }],
        "id": "10172"
    },
    "issue": {
        "fields": {
            "assignee": null
        },
        "key": "APP-123"
    }
}
"""

SAMPLE_EDIT_ISSUE_PAYLOAD_ASSIGNEE = """
{
    "changelog": {
        "items": [{
            "to": "admin",
            "field": "assignee",
            "toString": "Jess MacQueen",
            "from": null,
            "fromString": null,
            "fieldtype": "jira",
            "fieldId": "assignee"
        }],
        "id": "10172"
    },
    "issue": {
        "fields": {
            "assignee": {
                "emailAddress": "jess@sentry.io"
            }
        },
        "key": "APP-123"
    }
}
"""


class JiraSearchEndpointTest(APITestCase):
    @patch('sentry.integrations.jira.webhooks.sync_group_assignee_inbound')
    def test_simple_assign(self, mock_sync_group_assignee_inbound):
        org = self.organization

        integration = Integration.objects.create(
            provider='jira',
            name='Example JIRA',
        )
        integration.add_organization(org.id)

        path = reverse('sentry-extensions-jira-issue-updated')

        with patch('sentry.integrations.jira.webhooks.get_integration_from_jwt', return_value=integration):
            resp = self.client.post(
                path,
                data=json.loads(SAMPLE_EDIT_ISSUE_PAYLOAD_ASSIGNEE.strip()),
                HTTP_AUTHORIZATION='JWT anexampletoken',
            )
            assert resp.status_code == 200
            mock_sync_group_assignee_inbound.assert_called_with(
                integration, 'jess@sentry.io', 'APP-123', assign=True,
            )

    @patch('sentry.integrations.jira.webhooks.sync_group_assignee_inbound')
    def test_simple_deassign(self, mock_sync_group_assignee_inbound):
        org = self.organization

        integration = Integration.objects.create(
            provider='jira',
            name='Example JIRA',
        )
        integration.add_organization(org.id)

        path = reverse('sentry-extensions-jira-issue-updated')

        with patch('sentry.integrations.jira.webhooks.get_integration_from_jwt', return_value=integration):
            resp = self.client.post(
                path,
                data=json.loads(SAMPLE_EDIT_ISSUE_PAYLOAD_NO_ASSIGNEE.strip()),
                HTTP_AUTHORIZATION='JWT anexampletoken',
            )
            assert resp.status_code == 200
            mock_sync_group_assignee_inbound.assert_called_with(
                integration, None, 'APP-123', assign=False,
            )
