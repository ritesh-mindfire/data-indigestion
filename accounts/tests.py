from django.test import TestCase
from accounts.models import Manufacturer

class ManufacturerTestCase(TestCase):
    def setUp(self):
        print('.........setup ruunning')
        Manufacturer.objects.create(name="test1", car_model='maruti', car_year=2021,
                                    country='India', price=20000)
        Manufacturer.objects.create(name="test2", car_model='marutisu', car_year=2020,
                                    country='India', price=2200)

    def test_manufacturing_year(self):
        obj1 = Manufacturer.objects.get(name="test1")
        obj2 = Manufacturer.objects.get(name="test2")
        self.assertEqual(obj1.is_current_year_model(), True)
        self.assertEqual(obj2.is_current_year_model(), False)

    def test_car_name(self):
        obj3 = Manufacturer.objects.get(name="test1")
        self.assertTrue(obj3.name.isupper())

    def test_car_model_datatype(self):
        obj3 = Manufacturer.objects.get(name="test1")
        self.assertEqual(type(obj3.car_model), int)
