from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from ..models.users import User
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import db

order_namespace = Namespace('order', description='namespace for order')

order_model = order_namespace.model(
    'Order', {
        'id': fields.Integer(description='An ID'),
        'size': fields.String(description='Size of order', required=True,
            enum = ['SMALL','MEDIUM','LARGE','EXTRA_LARGE']
        ),
        'order_status': fields.String(description='The Status of our Order', required=True,
            enum = ['PENDING','IN_TRANSIT','DELIVERED']
        ),
        'flavour': fields.String(description='The flavour of the Pizza', required=True),
        'quantity': fields.Integer(description='The quantity od Pizza ordered', requires=True, default=1)
    }
)

order_status_model = order_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(description='Order Status', required=True,
            enum = ['PENDING','IN_TRANSIT','DELIVERED']
        )
    }
)


@order_namespace.route('/orders')
class OrderGetCreate(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description='Get all orders')
    @jwt_required()
    def get(self):
        """
        Get all orders
        """
        orders = Order.query.all()

        return orders, HTTPStatus.OK 

    @jwt_required()
    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description='Place an order',)
    def post(self):
        """
        place and order
        """

        username = get_jwt_identity()

        current_user = User.query.filter_by(username=username).first()

        data = order_namespace.payload
        
        new_order = Order(
            size = data['size'],
            quantity = data['quantity'],
            flavour = data['flavour']
        )

        new_order.user = current_user

        new_order.save()


        return new_order, HTTPStatus.CREATED
    

@order_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):

    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description='Get an order by id')
    @jwt_required()
    def get(self, order_id):
        """
        Retrieve an order by id
        """
        order = Order.get_by_id(order_id)

        return order, HTTPStatus.OK
    
    
    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description='Update an order by id', 
        params={'order_id': 'An ID'
        })
    @jwt_required()
    def put(self, order_id):
        """
        Update an order by id
        """
        order_to_update = Order.get_by_id(order_id)

        data = order_namespace.payload

        order_to_update.size = data.Optional["size"]
        order_to_update.quantity = data.Optional["quantity"]
        order_to_update.flavour = data.Optional["flavour"]

        db.session.commit()

        return order_to_update, HTTPStatus.OK


    @order_namespace.doc(description='Delete an order by id')
    @jwt_required()
    def delete(self, order_id):
        """
        Delete an order by id
        """
        order_to_delete = Order.get_by_id(order_id)

        order_to_delete.delete()

        return {"message": "Deleted Successfully"}, HTTPStatus.OK
        

@order_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderByUser(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description='Get a specific order by user id and order id',
        params={
            'user_id': 'The user id',
            'order_id': 'The order id'
        })
    
    @jwt_required()
    def get(self, user_id, order_id):
        """
        Retrieve a user specific order by id
        """
        user = User.get_by_id(user_id)

        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

        return order, HTTPStatus.OK



@order_namespace.route('/user/<int:user_id>/orders')
class GetAllOrderByUser(Resource):
    @order_namespace.marshal_list_with(order_model)
    @order_namespace.doc(
        description='Get all Orders by user id',
        params={
            'user_id': 'The id for a specific user\'s order'
        })
    @jwt_required()
    def get(self, user_id):
        """
        Retrieve all order by user
        """
        user = User.get_by_id(user_id)

        orders = user.orders

        return orders, HTTPStatus.OK


@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):
    @order_namespace.expect(order_status_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description='Update an order\'s status',
        params={
            'order_id': 'The id for a specific order'
        })
    @jwt_required()
    def patch(self, order_id):
        """
        Update an order Status
        """
        data = order_namespace.payload

        order_to_update = Order.get_by_id(order_id)

        order_to_update.order_status = data["order_status"]

        db.session.commit()

        return order_to_update, HTTPStatus.OK
