import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from flask_jwt_extended import create_access_token
from ..models.orders import Order

class OrderTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.app = None
        self.client =None
        self.appctx.pop()


    def test_get_all_orders(self):
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.get('/order/orders', headers=headers)
        assert response.status_code == 200
        assert response.json == []


    def test_create_order(self):     
        data = {
            "size": "MEDIUM",
            "quantity": "2",
            "flavour": "Apple"
        }
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.post('/order/orders', json=data, headers=headers)
        assert response.status_code == 201
        orders = Order.query.all()
        assert len(orders) == 1
        assert response.json['size'] == 'Sizes.MEDIUM'

    # Function to test the retrieval of a single order
    def test_get_single_order(self):
        order = Order(
            size = 'LARGE',
            quantity = 1,
            flavour = 'Pepperoni'
        )

        order.save()
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.get('/order/order/1', headers=headers)

        assert response.status_code == 200

    
    