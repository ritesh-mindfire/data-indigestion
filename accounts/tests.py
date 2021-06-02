from django.test import TestCase
from django.test import Client

from accounts.models import Manufacturer

from django.contrib.auth import get_user_model
User = get_user_model()


# class ManufacturerTestCase(TestCase):
#     def setUp(self):
#         print('.........setup ruunning')
#         Manufacturer.objects.create(name="test1", car_model='maruti', car_year=2021,
#                                     country='India', price=20000)
#         Manufacturer.objects.create(name="test2", car_model='marutisu', car_year=2020,
#                                     country='India', price=2200)

#     def test_manufacturing_year(self):
#         obj1 = Manufacturer.objects.get(name="test1")
#         obj2 = Manufacturer.objects.get(name="test2")
#         self.assertEqual(obj1.is_current_year_model(), True)
#         self.assertEqual(obj2.is_current_year_model(), False)

#     def test_car_name(self):
#         obj3 = Manufacturer.objects.get(name="test1")
#         self.assertTrue(obj3.name.isupper())

#     def test_car_model_datatype(self):
#         obj3 = Manufacturer.objects.get(name="test1")
#         self.assertEqual(type(obj3.car_model), int)


class UserTestCase(TestCase):
    def setUp(self):
        obj = User.objects.create(username='admin')
        obj.set_password('1234')
        obj.save()
        self.client = Client()

    def test_get_request(self):
        # Issue a GET request.
        response = self.client.get('/api/userinfo/')
        
        # Check that the response is 405 Method not allowed.
        self.assertEqual(response.status_code, 405)

    def test_post_request_valid_creds(self):
        #check for valid credentials
        response = self.client.post('/api/userinfo/', {'username': 'admin', 'password': '1234'})
        self.assertEqual(response.status_code, 200)

    def test_post_request_invalid_creds(self):
        #check for no username credentials
        response1 = self.client.post('/api/userinfo/', {'username': '', 'password': 'admin'})
        self.assertEqual(response1.status_code, 400)

        #check for invalid credentials
        response2 = self.client.post('/api/userinfo/', {'username': 'admin', 'password': 'abcde'})
        self.assertEqual(response2.status_code, 400)

        
        