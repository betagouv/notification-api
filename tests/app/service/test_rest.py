import json
from flask import url_for
from app.dao.services_dao import save_model_service
from app.models import (Service, ApiKey, Template)
from tests import create_authorization_header
from tests.app.conftest import sample_user as create_sample_user


def test_get_service_list(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests GET endpoint '/' to retrieve entire service list.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.get_service'),
                                                      method='GET')
            response = client.get(url_for('service.get_service'),
                                  headers=[auth_header])
            assert response.status_code == 200
            json_resp = json.loads(response.get_data(as_text=True))
            # TODO assert correct json returned
            assert len(json_resp['data']) == 2
            assert json_resp['data'][0]['name'] == sample_service.name
            assert json_resp['data'][0]['id'] == sample_service.id


def test_get_service(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests GET endpoint '/<service_id>' to retrieve a single service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.get_service', service_id=sample_service.id),
                                                      method='GET')
            resp = client.get(url_for('service.get_service',
                                      service_id=sample_service.id),
                              headers=[auth_header])
            assert resp.status_code == 200
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == sample_service.name
            assert json_resp['data']['id'] == sample_service.id


def test_post_service(notify_api, notify_db, notify_db_session, sample_user, sample_admin_service_id):
    """
    Tests POST endpoint '/' to create a service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Service.query.count() == 1
            data = {
                'name': 'created service',
                'users': [sample_user.id],
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_service'),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.post(
                url_for('service.create_service'),
                data=json.dumps(data),
                headers=headers)
            assert resp.status_code == 201
            service = Service.query.filter_by(name='created service').first()
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == service.name
            assert json_resp['data']['limit'] == service.limit


def test_post_service_multiple_users(notify_api, notify_db, notify_db_session, sample_user, sample_admin_service_id):
    """
    Tests POST endpoint '/' to create a service with multiple users.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            another_user = create_sample_user(
                notify_db,
                notify_db_session,
                "new@digital.cabinet-office.gov.uk")
            assert Service.query.count() == 1
            data = {
                'name': 'created service',
                'users': [sample_user.id, another_user.id],
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_service'),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.post(
                url_for('service.create_service'),
                data=json.dumps(data),
                headers=headers)
            assert resp.status_code == 201
            service = Service.query.filter_by(name='created service').first()
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == service.name
            assert json_resp['data']['limit'] == service.limit
            assert len(service.users) == 2


def test_post_service_without_users_attribute(notify_api, notify_db, notify_db_session, sample_admin_service_id):
    """
    Tests POST endpoint '/' to create a service without 'users' attribute.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Service.query.count() == 1
            data = {
                'name': 'created service',
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_service'),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.post(
                url_for('service.create_service'),
                data=json.dumps(data),
                headers=headers)
            assert resp.status_code == 400
            assert Service.query.count() == 1
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['message'] == '{"users": ["Missing data for required attribute"]}'


def test_put_service(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>' to edit a service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Service.query.count() == 2
            new_name = 'updated service'
            data = {
                'name': new_name,
                'users': [sample_service.users[0].id],
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_service',
                                                                   service_id=sample_service.id),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.put(
                url_for('service.update_service', service_id=sample_service.id),
                data=json.dumps(data),
                headers=headers)
            assert Service.query.count() == 2
            assert resp.status_code == 200
            updated_service = Service.query.get(sample_service.id)
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == updated_service.name
            assert json_resp['data']['limit'] == updated_service.limit
            assert updated_service.name == new_name


def test_put_service_not_exists(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>' service doesn't exist.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            sample_user = sample_service.users[0]
            new_name = 'updated service'
            data = {
                'name': new_name,
                'users': [sample_user.id],
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_service', service_id="123"),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            resp = client.put(
                url_for('service.update_service', service_id="123"),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 404
            assert Service.query.first().name == sample_service.name
            assert Service.query.first().name != new_name


def test_put_service_add_user(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>' add user to the service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Service.query.count() == 2
            another_user = create_sample_user(
                notify_db,
                notify_db_session,
                "new@digital.cabinet-office.gov.uk")
            new_name = 'updated service'
            sample_user = sample_service.users[0]
            data = {
                'name': new_name,
                'users': [sample_user.id, another_user.id],
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_service',
                                                                   service_id=sample_service.id),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.put(
                url_for('service.update_service', service_id=sample_service.id),
                data=json.dumps(data),
                headers=headers)
            assert Service.query.count() == 2
            assert resp.status_code == 200
            updated_service = Service.query.get(sample_service.id)
            json_resp = json.loads(resp.get_data(as_text=True))
            assert len(json_resp['data']['users']) == 2
            assert sample_user.id in json_resp['data']['users']
            assert another_user.id in json_resp['data']['users']
            assert updated_service.users == [sample_user, another_user]


def test_put_service_remove_user(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>' add user to the service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            sample_user = sample_service.users[0]
            another_user = create_sample_user(
                notify_db,
                notify_db_session,
                "new@digital.cabinet-office.gov.uk")
            data = {
                'name': sample_service.name,
                'users': [sample_user.id, another_user.id],
                'limit': sample_service.limit,
                'restricted': sample_service.restricted,
                'active': sample_service.active}
            save_model_service(sample_service, update_dict=data)
            assert Service.query.count() == 2
            data['users'] = [another_user.id]

            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_service',
                                                                   service_id=sample_service.id),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.put(
                url_for('service.update_service', service_id=sample_service.id),
                data=json.dumps(data),
                headers=headers)
            assert Service.query.count() == 2
            assert resp.status_code == 200
            updated_service = Service.query.get(sample_service.id)
            json_resp = json.loads(resp.get_data(as_text=True))
            assert len(json_resp['data']['users']) == 1
            assert sample_user.id not in json_resp['data']['users']
            assert another_user.id in json_resp['data']['users']
            assert sample_user not in updated_service.users
            assert another_user in updated_service.users


def test_delete_service(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests DELETE endpoint '/<service_id>' delete service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_service',
                                                                   service_id=sample_service.id),
                                                      method='DELETE')
            resp = client.delete(
                url_for('service.update_service', service_id=sample_service.id),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 202
            json_resp = json.loads(resp.get_data(as_text=True))
            json_resp['data']['name'] == sample_service.name
            assert Service.query.count() == 1


def test_delete_service_not_exists(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests DELETE endpoint '/<service_id>' delete service doesn't exist.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Service.query.count() == 2
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_service', service_id="123"),
                                                      method='DELETE')
            resp = client.delete(
                url_for('service.update_service', service_id="123"),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 404
            assert Service.query.count() == 2


def test_renew_api_key_should_create_new_api_key_for_service(notify_api, notify_db,
                                                             notify_db_session,
                                                             sample_service,
                                                             sample_admin_service_id):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            data = {'name': 'some secret name'}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.renew_api_key',
                                                                   service_id=sample_service.id),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            response = client.post(url_for('service.renew_api_key', service_id=sample_service.id),
                                   data=json.dumps(data),
                                   headers=[('Content-Type', 'application/json'), auth_header])
            assert response.status_code == 201
            assert response.get_data is not None
            saved_api_key = ApiKey.query.filter_by(service_id=sample_service.id).first()
            assert saved_api_key.service_id == sample_service.id
            assert saved_api_key.name == 'some secret name'


def test_renew_api_key_should_expire_the_old_api_key_and_create_a_new_api_key(notify_api, notify_db, notify_db_session,
                                                                              sample_api_key, sample_admin_service_id):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert ApiKey.query.count() == 2
            data = {'name': 'some secret name'}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.renew_api_key',
                                                                   service_id=sample_api_key.service_id),
                                                      method='POST',
                                                      request_body=json.dumps(data))

            response = client.post(url_for('service.renew_api_key', service_id=sample_api_key.service_id),
                                   data=json.dumps(data),
                                   headers=[('Content-Type', 'application/json'), auth_header])
            assert response.status_code == 201
            assert ApiKey.query.count() == 3
            all_api_keys = ApiKey.query.filter_by(service_id=sample_api_key.service_id).all()
            for x in all_api_keys:
                if x.id == sample_api_key.id:
                    assert x.expiry_date is not None
                else:
                    assert x.expiry_date is None
                    assert x.secret is not sample_api_key.secret


def test_renew_api_key_should_return_error_when_service_does_not_exist(notify_api, notify_db, notify_db_session,
                                                                       sample_service, sample_admin_service_id):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.renew_api_key', service_id="123"),
                                                      method='POST')
            response = client.post(url_for('service.renew_api_key', service_id=123),
                                   headers=[('Content-Type', 'application/json'), auth_header])
            assert response.status_code == 404


def test_revoke_api_key_should_expire_api_key_for_service(notify_api, notify_db, notify_db_session,
                                                          sample_api_key, sample_admin_service_id):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert ApiKey.query.count() == 2
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.revoke_api_key',
                                                                   service_id=sample_api_key.service_id),
                                                      method='POST')
            response = client.post(url_for('service.revoke_api_key', service_id=sample_api_key.service_id),
                                   headers=[auth_header])
            assert response.status_code == 202
            api_keys_for_service = ApiKey.query.filter_by(service_id=sample_api_key.service_id).first()
            assert api_keys_for_service.expiry_date is not None


def test_create_service_should_create_new_service_for_user(notify_api, notify_db, notify_db_session, sample_user,
                                                           sample_admin_service_id):
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            data = {
                'name': 'created service',
                'users': [sample_user.id],
                'limit': 1000,
                'restricted': False,
                'active': False}
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_service'),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            headers = [('Content-Type', 'application/json'), auth_header]
            resp = client.post(url_for('service.create_service'),
                               data=json.dumps(data),
                               headers=headers)
            assert resp.status_code == 201


def test_create_template(notify_api, notify_db, notify_db_session, sample_service, sample_admin_service_id):
    """
    Tests POST endpoint '/<service_id>/template' a template can be created
    from a service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Template.query.count() == 0
            template_name = "template name"
            template_type = "sms"
            template_content = "This is a template"
            data = {
                'name': template_name,
                'template_type': template_type,
                'content': template_content,
                'service': sample_service.id
            }
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_template',
                                                                   service_id=sample_service.id),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            resp = client.post(
                url_for('service.create_template', service_id=sample_service.id),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 201
            assert Template.query.count() == 1
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == template_name
            assert json_resp['data']['template_type'] == template_type
            assert json_resp['data']['content'] == template_content


def test_create_template_service_not_exists(notify_api, notify_db, notify_db_session, sample_service,
                                            sample_admin_service_id):
    """
    Tests POST endpoint '/<service_id>/template' a template can be created
    from a service.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Template.query.count() == 0
            template_name = "template name"
            template_type = "sms"
            template_content = "This is a template"
            data = {
                'name': template_name,
                'template_type': template_type,
                'content': template_content,
                'service': sample_service.id
            }
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_template', service_id="123"),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            resp = client.post(
                url_for('service.create_template', service_id="123"),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 404
            assert Template.query.count() == 0
            json_resp = json.loads(resp.get_data(as_text=True))
            assert "Service not found" in json_resp['message']


def test_update_template(notify_api, notify_db, notify_db_session, sample_template, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>/template/<template_id>' a template can be
    updated.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Template.query.count() == 1
            sample_service = Service.query.first()
            old_name = sample_template.name
            template_name = "new name"
            template_type = "sms"
            template_content = "content has been changed"
            data = {
                'name': template_name,
                'template_type': template_type,
                'content': template_content,
                'service': sample_service.id
            }
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_template',
                                                                   service_id=sample_service.id,
                                                                   template_id=sample_template.id),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            resp = client.put(
                url_for('service.update_template',
                        service_id=sample_service.id,
                        template_id=sample_template.id),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 200
            assert Template.query.count() == 1
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == template_name
            assert json_resp['data']['template_type'] == template_type
            assert json_resp['data']['content'] == template_content
            assert old_name != template_name


def test_update_template_service_not_exists(notify_api, notify_db, notify_db_session,
                                            sample_template, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>/template/<template_id>' a 404 if service
    doesn't exist.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Template.query.count() == 1
            template_name = "new name"
            template_type = "sms"
            template_content = "content has been changed"
            data = {
                'name': template_name,
                'template_type': template_type,
                'content': template_content,
                'service': sample_template.service_id
            }
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_template',
                                                                   service_id="123",
                                                                   template_id=sample_template.id),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            resp = client.put(
                url_for('service.update_template',
                        service_id="123",
                        template_id=sample_template.id),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 404
            json_resp = json.loads(resp.get_data(as_text=True))
            assert "Service not found" in json_resp['message']
            assert template_name != sample_template.name


def test_update_template_template_not_exists(notify_api, notify_db, notify_db_session,
                                             sample_template, sample_admin_service_id):
    """
    Tests PUT endpoint '/<service_id>/template/<template_id>' a 404 if template
    doesn't exist.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Template.query.count() == 1
            sample_service = Service.query.first()
            template_name = "new name"
            template_type = "sms"
            template_content = "content has been changed"
            data = {
                'name': template_name,
                'template_type': template_type,
                'content': template_content,
                'service': sample_service.id
            }
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.update_template',
                                                                   service_id=sample_service.id,
                                                                   template_id="123"),
                                                      method='PUT',
                                                      request_body=json.dumps(data))
            resp = client.put(
                url_for('service.update_template',
                        service_id=sample_service.id,
                        template_id="123"),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 404
            json_resp = json.loads(resp.get_data(as_text=True))
            assert "Template not found" in json_resp['message']
            assert template_name != sample_template.name


def test_create_template_unicode_content(notify_api, notify_db, notify_db_session, sample_service,
                                         sample_admin_service_id):
    """
    Tests POST endpoint '/<service_id>/template/<template_id>' a template is
    created and the content encoding is respected after saving and loading
    from the db.
    """
    with notify_api.test_request_context():
        with notify_api.test_client() as client:
            assert Template.query.count() == 0
            template_name = "template name"
            template_type = "sms"
            template_content = 'Россия'
            data = {
                'name': template_name,
                'template_type': template_type,
                'content': template_content,
                'service': sample_service.id
            }
            auth_header = create_authorization_header(service_id=sample_admin_service_id,
                                                      path=url_for('service.create_template',
                                                                   service_id=sample_service.id),
                                                      method='POST',
                                                      request_body=json.dumps(data))
            resp = client.post(
                url_for('service.create_template', service_id=sample_service.id),
                data=json.dumps(data),
                headers=[('Content-Type', 'application/json'), auth_header])
            assert resp.status_code == 201
            assert Template.query.count() == 1
            json_resp = json.loads(resp.get_data(as_text=True))
            assert json_resp['data']['name'] == template_name
            assert json_resp['data']['template_type'] == template_type
            assert json_resp['data']['content'] == template_content
