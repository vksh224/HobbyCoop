import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("hobbycooperative.createSample")

from backend import db
from backend.schema import User
from backend.schema import ListedItem 
from backend.schema import Category
from backend.schema import RequestToRent
from backend.schema import ProposedPickupTime
from backend.schema import Transaction
from backend.schema import ReturnRequest
from backend.schema import ProposedReturnTime
from backend.schema import ReturnTime
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from db_create import createInitialCategories

import random
random.seed(0)

SAMPLE_LATITUDE_RANGE = (37.911594, 38.006472)
SAMPLE_LATITUDE = lambda: random.uniform(*SAMPLE_LATITUDE_RANGE)
SAMPLE_LONGITUDE_RANGE = (-91.687430, -91.827505)
SAMPLE_LONGITUDE = lambda: random.uniform(*SAMPLE_LONGITUDE_RANGE)

NUM_LISTED_ITEMS = 10

def createSampleUsers():
  return [ 
    User(
      f='DrTools', l="",
      email='drtools@aol.com',
      password='tools4schools',
      lat=SAMPLE_LATITUDE(),
      lon=SAMPLE_LONGITUDE(),
    ),
    User(
      f='builderdude1998', l="",
      email='h44xxoorr@gmail.com',
      password='mypasswordisstrong',
      lat=SAMPLE_LATITUDE(),
      lon=SAMPLE_LONGITUDE(),
    ),
  ]


from pprint import pprint
if __name__ == "__main__":

  db.drop_all()
  db.create_all()

  users = createSampleUsers()
  db.session.add_all(users)
  db.session.commit()
  print("Users signed up in the system:")
  pprint(User.query.all())
  print("-"*80)

  # Create categories!
  ALL_CATEGORIES, LEAF_CATEGORIES = createInitialCategories()
  db.session.add_all(ALL_CATEGORIES)
  db.session.commit()

  print("Categories available:")
  pprint(Category.query.all())
  print("-"*80)

  # Let's create some random listings!
  items = []
  for i in range(NUM_LISTED_ITEMS):
    randomCategory = random.choice(LEAF_CATEGORIES)
    items.append(randomCategory.listMyItem(
      daily_rate=random.randrange(1, 26, 1),
      owner=users[0],
    ))
  db.session.add_all(items)
  db.session.commit()
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print("-"*80)

