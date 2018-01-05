import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("hobbycooperative.driver")

import settings
import os
if os.path.exists(settings.DB_PATH):
  os.remove(settings.DB_PATH)

from schema import db
from schema import User
from schema import ListedItem 
from schema import Category
from schema import RequestToRent
from schema import ProposedPickupTime
from schema import Transaction
from schema import ReturnRequest
from schema import ProposedReturnTime
from schema import ReturnTime
import ip2coords
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
from pytz import timezone


def createSampleUsers():
  coords = ip2coords.getCoordsFromIP('131.151.88.173')

  hobbyist = User(
    username='DrTools',
    email='drtools@aol.com',
    password='tools4schools',
    lat=coords[0],
    lon=coords[1],
  )

  newbie = User(
    username='builder1998',
    email='builder1998@gmail.com',
    password='beiber4life',
    lat=coords[0],
    lon=coords[1],
  )

  return hobbyist, newbie


def createSampleCategories():
  tools_and_hardware = Category(name="Tools & Hardware")
  power_tools = Category(name="Power Tools", parent=tools_and_hardware)
  woodworking_tools = Category(name="Woodworking Tools", parent=power_tools)
  drills = Category(
    name="Power Drills",
    parent=woodworking_tools,
    image_url="http://i.imgur.com/8GiKI3rm.jpg",
  )
  return (
    tools_and_hardware,
    power_tools,
    woodworking_tools,
    drills,
  )


from pprint import pprint
if __name__ == "__main__":
  db.create_all()

  # Two users sign up for this system.
  #  hobbyist owns many tools, and is looking to rent them out.
  #  newbie is an industrius young adult, but does not own tools.
  #  hobbyist will be renting his tools to newbie.
  hobbyist, newbie = createSampleUsers()
  db.session.add(hobbyist)
  db.session.add(newbie)
  db.session.commit()
  print("Users signed up in the system:")
  pprint(User.query.all())
  print("-"*80)

  # hobbyist decides to rent out his power drill.
  # First, the administrator of HobbyCooperative needs to add
  #  categories for which a powerdrill can be added.
  # Tools & Hardware > Power Tools > Woodworking Tools
  #                  > Drills > Cordless Drills
  categories = createSampleCategories()
  cordless_drills_category = categories[-1]
  db.session.add_all(categories)
  db.session.commit()
  print("Categories available:")
  pprint(Category.query.all())
  print("-"*80)

  # With the categories created, hobbyist can list this coordless power drill
  listed_drill = cordless_drills_category.listMyItem(
    daily_rate=500,
    owner=hobbyist,
  )
  db.session.add(listed_drill)
  db.session.commit()
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print("-"*80)

  # The power drill is listed, and newbie finds it, wishing to rent it.
  #  newbie will have to request the item with various pick up times.
  one_day = timedelta(days=1)
  rental_request = listed_drill.requestToRent(
    rentee=newbie,
    duration=one_day,
  )

  db.session.add(rental_request)
  db.session.commit()
  print("Requests from buyers to rent items:")
  pprint(RequestToRent.query.all())
  print('-'*80)
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print('='*80)

  # It is now up to hobbyest to accept the rental request.
  # By hobbyist suggesting times for pickup, he implicitly accepts the
  #  rental proposal and commits to proving the item to newbie.
  tomorrow = date.today() + one_day
  central_tz = timezone('US/Central')
  afternoon = time(hour=14, tzinfo=central_tz)
  tomorrow_afternoon = datetime.combine(tomorrow, afternoon)

  two_hours = timedelta(hours=2)
  owner_available_until = tomorrow_afternoon + two_hours

  proposed_pickup_time = rental_request.suggestPickupTimes(
    available_from=tomorrow_afternoon,
    available_until=owner_available_until,
    location="Walmart parking lot",
  )

  db.session.add(proposed_pickup_time)
  db.session.commit()
  print("The owner has proposed the following times for the rentee to pickup!")
  pprint(ProposedPickupTime.query.all())
  print('-'*80)
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print('='*80)


  # newbie now needs to accept the proposed meetup time. Upon accepting it,
  #  the newbie will be charged for the rental transaction.
  tx = proposed_pickup_time.accept(exact_pickup_time=tomorrow_afternoon)
  db.session.add(tx)
  db.session.commit()
  print("Transactions committed!")
  pprint(Transaction.query.all())
  print("-"*40)
  print("Requests from buyers to rent items:")
  pprint(RequestToRent.query.all())
  print('-'*40)
  print("Proposed times still present")
  pprint(ProposedPickupTime.query.all())
  print('-'*80)
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print('='*80)


  # Time passes, and newbie is ready to return the item. He must propose
  #  several times to return.
  return_request = tx.requestToReturn()
  db.session.add(return_request)
  db.session.commit()
  print("A return request has been sent to the owner from the rentee!")
  pprint(ReturnRequest.query.all())
  print("-"*80)
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print('='*80)


  # The owner now indicates when they are free to accept the item.
  return_time_start = tomorrow_afternoon + timedelta(days=2)
  return_time_stop = return_time_start + timedelta(hours=4)
  times_available_for_return = [
    (return_time_start, return_time_stop)
  ]
  proposed_return_times = return_request.proposeReturnTimes(
    return_times=times_available_for_return
  )
  db.session.add_all(proposed_return_times)
  db.session.commit()
  print("The owner will meet the rentee for a return.")
  pprint(ProposedReturnTime.query.all())
  print("-"*80)
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print('='*80)


  # The rentee now selects some time to meet up with the owner.
  accepted_return_time = proposed_return_times[0].returnOn(
    return_time=return_time_start + timedelta(hours=1)
  )
  db.session.add(accepted_return_time)
  db.session.commit()
  print("The rentee has now selected a return time.")
  pprint(ReturnTime.query.all())
  print("-"*40)
  print("The proposed return times should remain, in case something"
        " goes wrong")
  pprint(ProposedReturnTime.query.all())
  print("-"*80)
  print("Items listed for rent:")
  pprint(ListedItem.query.all())
  print('='*80)


  # After the owner has the item, he must confirm receipt for it
  #  to be relisted.
  has_been_relisted = accepted_return_time.confirmReturned()
  print("The owner now has the item again!")
  pprint(ListedItem.query.all())
  print("-"*40)
  print("The previous ProposedReturnTimes should be deleted")
  pprint(ProposedReturnTime.query.all())
  print("-"*40)
  print("...as well as the return time.")
  pprint(ReturnTime.query.all())
  print("-"*40)
  print("...and the requested return.")
  pprint(ReturnRequest.query.all())
  print("-"*80)
