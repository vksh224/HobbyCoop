import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("hobbycoop")

from flask import Flask
app = Flask(__name__)
app.config.from_object('config')

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask.ext.cors import CORS
cors = CORS(app)

from flask_restful import Api
from api import OwnerItems
from api import UserLogIn
from api import UserRegistration
from api import RenteeRequestItem
from api import Search
from api import IndexPage
from api import CategoryListing
from api import RenteeItems
from api import SuggestedItemPickupFromOwnerToRentee
from api import ScheduledItemPickupFromOwnerToRentee
from api import ConfirmItemPickupFromOwnerToRentee
from api import ReturnRequestByRentee
from api import SuggestedItemPickupFromRenteeToOwner
from api import ScheduledItemPickupFromRenteeToOwner
from api import ConfirmItemPickupFromRenteeToOwner
from api import ListedItemEndPoint
api = Api(app)
api.add_resource(UserLogIn, '/login')
api.add_resource(RenteeRequestItem, '/requestItem')
api.add_resource(UserRegistration, '/register')
api.add_resource(OwnerItems, '/user/<int:owner_id>/items')
api.add_resource(Search, '/search/<keyword>')
api.add_resource(IndexPage, "/")
api.add_resource(CategoryListing, "/categories")
api.add_resource(RenteeItems, '/user/<int:rentee_id>/rentee')
api.add_resource(SuggestedItemPickupFromOwnerToRentee,
                 '/suggestExchangeTimeAndLocation')
api.add_resource(ScheduledItemPickupFromOwnerToRentee,
                 '/confirmExchangeTimeAndLocation')
api.add_resource(ConfirmItemPickupFromOwnerToRentee,
                 '/confirmItemPickup')
api.add_resource(ReturnRequestByRentee,
                 '/requestReturnItem')
api.add_resource(SuggestedItemPickupFromRenteeToOwner,
                 '/suggestReturnTimeAndLocation')
api.add_resource(ScheduledItemPickupFromRenteeToOwner,
                 '/scheduleReturn')
api.add_resource(ConfirmItemPickupFromRenteeToOwner,
                 '/confirmItemReturn')
api.add_resource(ListedItemEndPoint,
                 '/item', '/item/<int:listed_item_id>')
