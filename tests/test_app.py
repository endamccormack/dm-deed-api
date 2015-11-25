from application import app
from application.deed.model import Deed
from tests.helper import DeedHelper, DeedModelMock
from flask.ext.api import status
import unittest
import json
import mock


class TestRoutes(unittest.TestCase):

    DEED_ENDPOINT = "/deed/"

    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status, '200 OK')

    def test_deed(self):
        self.assertEqual((self.app.get('/deed')).status,
                         '301 MOVED PERMANENTLY')

    def test_model(self):
        test_deed = Deed()
        test_token = test_deed.generate_token()
        self.assertTrue(len(test_token) == 6)

    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create(self, mock_Borrower, mock_Deed):
        payload = json.dumps(DeedHelper._invalid_phone_numbers)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create(self, mock_Borrower, mock_Deed):
        payload = json.dumps(DeedHelper._json_doc)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_title_format(self):
        payload = json.dumps(DeedHelper._invalid_title)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()

        response = self.app.get(self.DEED_ENDPOINT + 'AB1234')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("DN100" in response.data.decode())

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint_not_found(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = None

        response = self.app.get(self.DEED_ENDPOINT + 'CD3456')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
