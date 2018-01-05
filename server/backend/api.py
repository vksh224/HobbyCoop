import logging
logger = logging.getLogger("hobbycoop.schema")

from flask import Flask
from flask import json
from flask import request
from flask import Response
from flask_restful import Resource
from flask_restful import reqparse

from schema import db
from schema import ListedItem
from schema import RequestToRent
from schema import ProposedPickupTime
from schema import Transaction
from schema import Category
from schema import User
from schema import ReturnRequest
from schema import ProposedReturnTime
from schema import ReturnTime
from sqlalchemy import and_
from flask.json import jsonify
from datetime import datetime
from datetime import timedelta

TIME_FMT = "%x at %-I:%M %p"
INCOMING_DATETIME_READER = lambda(d): d

class IndexPage(Resource):
  def get(self):
    return "Hello, world!"

#####################################################################
# User profile loading by user ID
#################################
# Owner-specific listings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OwnerItems(Resource):
  def get(self, owner_id):
    api_results = {}
    # Get the items this owner has listed.
    owners_items = ListedItem.query.with_entities(ListedItem.id)\
                                   .filter_by(owner_id=owner_id).all()
    owners_items = set([i for i, in owners_items])

    # 1. Owned items pending a rent request from a rentee
    rentRequests = self.getItemsPendingRentRequest(owners_items)
    rentRequests['fieldType'] = 'rentRequests'
    api_results['rentRequests'] = rentRequests

    #owners_items.difference_update(rentRequests.keys())

    # 2. Owned items that will be exchanged with the rentee soon.
    outgoingItems = self.getItemsToBeDroppedWithRentee(owners_items)
    outgoingItems['fieldType'] = 'itemDropOffs'
    api_results['itemDropOffs'] = outgoingItems

    #owners_items.difference_update(outgoingItems.keys())

    # 3. Owned items that are in the hands of the rentee at the moment.
    #  Note: some of these may have a return request!
    rentedItems = self.getItemsHeldByRentee(owners_items)
    rentedItems['fieldType'] = 'rentedItems'
    api_results['rentedItems'] = rentedItems

    #owners_items.difference_update(rentedItems.keys())

    # 4. Owned items that are idle (no rent requests, not rented)
    rent_request_ids = set([i['listed_item_id'] for i in rentRequests['items']])
    idleItems = self.getIdleItems(owner_id, rent_request_ids)
    idleItems['fieldType'] = 'idleItems'
    api_results['idleItems'] = idleItems

    return jsonify(api_results)

  def getItemsPendingRentRequest(self, owners_items):
    items_json = {
      'items': [],
      'description': 'Rental Requests (Response Needed)',
    }
    if not owners_items:
      return items_json

    # Find the items requested by rentees that are owned by this owner
    results = RequestToRent.query.filter(
      RequestToRent.listed_item_id.in_(owners_items)
    ).all()

    # Prepare for jsonifying
    for r in results:
      print("#"*100)
      print(r)
      print(r.listed_item)
      print("#"*100)
      listed_item = r.listed_item
      item_type = listed_item.item_type
      days_of_rent = r.duration_of_rent.days
      rentee = r.rentee
      item = {
        'id': r.id,
        'listed_item_id': listed_item.id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'cost': listed_item.daily_rate*days_of_rent,
        'duration': days_of_rent,
        'rentee': {
          'username': rentee.username,
          'id': rentee.id,
        },
      }

      # If the owner has specified a proposed exchange time, fill in
      #  the details of the request.
      proposed_pickup = r.pickup_times.first()
      if proposed_pickup is not None:
        item['suggestedMeetup'] = {
          'location': proposed_pickup.location,
          'from': proposed_pickup.proposed_meetup_time.strftime(TIME_FMT),
          'to': proposed_pickup.owner_available_until.strftime(TIME_FMT),
        }

      items_json['items'].append(item)
    return items_json


  def getItemsToBeDroppedWithRentee(self, owners_items):
    desc="Rented Items (Drop Off Pending)"
    if not owners_items:
      return {
        'items': [],
        'description': desc,
      }

    # Find all transactions with items owned by this owner
    #  that have yet to be dropped off.
    # We assume that, if the drop off timestamp is in the future,
    #  the item is still in the owner's hands.
    results = Transaction.query.filter(and_(
      Transaction.listed_item_id.in_(owners_items),
      Transaction.is_complete==False,
      Transaction.is_with_rentee==False,
    )).all()

    # listed_item.requests.count() from specific user
    return self.jsonifyTransactions(
      results, 
      desc=desc,
    )


  def getItemsHeldByRentee(self, owners_items):
    items_json = {
      'items': [],
      'description': "Rented Items"
    }
    if not owners_items:
      return items_json

    # Find all transactions with items owned by this owner
    #  whose starting time stamps are after right now.
    #  It is assumed the rentee has claimed the item.
    results = Transaction.query.filter(and_(
      Transaction.listed_item_id.in_(owners_items),
      Transaction.is_complete == False,
      Transaction.is_with_rentee == True,
    )).all()

    # Prepare for jsonifying
    for r in results:
      listed_item = r.listed_item
      item_type = listed_item.item_type
      rentee = r.rentee
      returnRequest = r.return_requested.first()

      item_result = {
        'listed_item_id': listed_item.id,
        'id': r.id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'rentee': {
          'username': rentee.username,
          'id': rentee.id,
        },
        'dueDate': (r.start_timestamp + r.duration).strftime(TIME_FMT),
      }

      if returnRequest is not None:
        item_result['returnRequested'] = True
        returnTime = returnRequest.will_be_returned_on.first()
        if returnTime is not None:
          item_result['meetupAt'] = {
            'location': returnTime.location,
            'time': returnTime.accepted_return_time.strftime(TIME_FMT),
            'return': True,
            'id': returnTime.id,
          }

        else:
          item_result['meetupAt'] = {'return': False}
          proposedReturnTime = returnRequest.times_to_return.first()
          if proposedReturnTime is not None:
            item_result['suggestedReturn'] = {
              'location': proposedReturnTime.location,
              'from': proposedReturnTime.proposed_timestamp.strftime(TIME_FMT),
              'to': proposedReturnTime.can_pickup_until.strftime(TIME_FMT),
            }

      else:
        item_result['returnRequested'] = False
        item_result['meetupAt'] = {
          'location': r.pickup_location,
          'time': r.start_timestamp.strftime(TIME_FMT),
          'return': False,
        }

      items_json['items'].append(item_result)
    return items_json


  def getIdleItems(self, owner_id, rentRequests):
    activeTx = Transaction.query.with_entities(Transaction.listed_item_id)\
                          .filter_by(is_complete=False).all()
    activeTx = set([i for i, in activeTx])
    rentRequestsAndActiveTransactions = rentRequests.union(activeTx)
    results = {
      'items': [],
      'description': "Idle Items"
    }
    logger.debug("$"*100)
    logger.debug("Return requests and incomplete transactions")
    logger.debug(rentRequestsAndActiveTransactions)
    logger.debug("$"*100)
    if rentRequestsAndActiveTransactions:
      idle_items = ListedItem.query.filter(and_(
        ListedItem.owner_id==owner_id,
        ~ListedItem.id.in_(rentRequestsAndActiveTransactions),
      ))
    else:
      idle_items = ListedItem.query.filter(
        ListedItem.owner_id==owner_id,
      )

    for i in idle_items.all():
      item_type = i.item_type
      results['items'].append({
        'id': i.id,
        'daily_rate': i.daily_rate,
        'name': item_type.name,
        'pic': item_type.image_url,
      })
    return results


  def jsonifyTransactions(self, txs, desc):
    items_json = {
      'items': [],
      'description': desc,
    }
    if not txs:
      return items_json

    # Prepare for jsonifying
    for r in txs:
      listed_item = r.listed_item
      item_type = listed_item.item_type
      rentee = r.rentee

      items_json['items'].append({
        'listed_item_id': listed_item.id,
        'id': r.id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'meetupAt': {
          'location': r.pickup_location,
          'time': r.start_timestamp.strftime(TIME_FMT),
        },
        'rentee': {
          'username': rentee.username,
          'id': rentee.id,
        },
      })
    return items_json

#################################
# Rentee-specific listings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class RenteeItems(Resource):
  def get(self, rentee_id):
    api_results = {}
    # Load pending requests
    # Load actively rented items

    # 1. Load request-rented items pending approval from the seller
    rentRequests = self.getItemsPendingRentRequest(rentee_id)
    rentRequests['fieldType'] = 'rentRequests'
    api_results['rentRequests'] = rentRequests

    # 2. Load items approved for rent by the owner, who has specified times
    #     he is available to drop off.
    approvedTimePending = self.getItemsApprovedByOwnerPendingTime(rentee_id)
    approvedTimePending['fieldType'] = 'pendingApproval'
    api_results['pendingApproval'] = approvedTimePending

    # 3. Load items to be picked up from the owner to the rentee
    itemsToPickup = self.getItemsToPickUp(rentee_id)
    itemsToPickup['fieldType'] = 'pendingPickup'
    api_results['pendingPickup'] = itemsToPickup

    # 4. Load items held by rentee who is actively using them.
    rentedActiveItems = self.getActiveRentedItems(rentee_id)
    rentedActiveItems['fieldType'] = 'rentedActiveItems'
    api_results['rentedActiveItems'] = rentedActiveItems

    # 5. Load items held by rentee, who has requested a return.
    returnRequestedItems = self.getReturnRequestedItems(rentee_id)
    returnRequestedItems['fieldType'] = 'returnRequestedItems'
    api_results['returnRequestedItems'] = returnRequestedItems

    # 6. Load items held by rentee, which the owner has specified some times
    #     for possible pickup.
    proposedReturnTimeItems = self.getItemsWithProposedReturnTimes(rentee_id)
    proposedReturnTimeItems['fieldType'] = 'proposedReturnTimeItems'
    api_results['proposedReturnTimeItems'] = proposedReturnTimeItems

    # 7. Load items scheduled for return.
    returnScheduledItems = self.getItemsWithScheduledReturn(rentee_id)
    returnScheduledItems['fieldType'] = 'returnScheduledItems'
    api_results['returnScheduledItems'] = returnScheduledItems

    # 8. Get completed transactions.
    completedTransactions = self.getCompletedTransactionsAsRentee(rentee_id)
    completedTransactions['fieldType'] = 'completedTransactions'
    api_results['completedTransactions'] = completedTransactions

    return jsonify(api_results)


  def getItemsPendingRentRequest(self, rentee_id):
    # These are items in the RequestToRent table with made by
    #  the rentee that the owner has not responded to.
    #  Thus, these are items not in ProposedPickupTimes
    requested_items = RequestToRent.query.filter(and_(
      RequestToRent.rentee_id==rentee_id,
    ))
    response = {
      'items': [],
      'description': "Rentals (Approval Pending)",
    }
    for i in requested_items.all():
      if i.pickup_times.count()>0:
        continue

      listed_item = i.listed_item
      item_type = listed_item.item_type
      owner = listed_item.owner
      days_of_rent = i.duration_of_rent.days
      response['items'].append({
        'id': i.id,
        'listed_item_id': i.listed_item_id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'owner': owner.username,
        'time_of_request': i.request_created_timestamp.strftime(TIME_FMT),
        'duration': days_of_rent,
        'cost': days_of_rent*listed_item.daily_rate,
      })
    return response

  def getItemsApprovedByOwnerPendingTime(self, rentee_id):
    # These are items in the ProposedPickupTime table.
    requested_items = RequestToRent.query.filter(and_(
      RequestToRent.rentee_id==rentee_id,
    ))
    response = {
      'items': [],
      'description': "Rentals (Approved for Scheduling and Payment)",
    }
    for i in requested_items.all():
      if i.pickup_times.count()==0:
        continue

      meetUpSuggestions = []
      meetups = i.pickup_times
      for m in meetups.all():
        _id = m.id
        meetUpSuggestions.append({
          'id': m.id,
          'location': m.location,
          'start_time': m.proposed_meetup_time.strftime(TIME_FMT),
          'end_time': m.owner_available_until.strftime(TIME_FMT),
        })

      listed_item = i.listed_item
      item_type = listed_item.item_type
      owner = listed_item.owner
      days_of_rent = i.duration_of_rent.days
      response['items'].append({
        'id': _id,
        'listed_item_id': i.listed_item_id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'owner': owner.username,
        'time_of_request': i.request_created_timestamp.strftime(TIME_FMT),
        'duration': days_of_rent,
        'cost': days_of_rent*listed_item.daily_rate,
        'meetupAt': meetUpSuggestions,
      })
    return response


  def getItemsToPickUp(self, rentee_id):
    # These items in the Transaction table have not been picked up yet.
    txs = Transaction.query.filter(and_(
      Transaction.rentee_id==rentee_id,
      Transaction.is_complete==False,
      Transaction.is_with_rentee==False,
    ))

    response = {
      "items": [],
      "description": "Scheduled Pick Ups",
    }
    for t in txs.all():
      listed_item = t.listed_item
      item_type = listed_item.item_type
      response['items'].append({
        'id': t.id,
        'pickup': True,
        'listed_item_id': listed_item.id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'owner': listed_item.owner.username,
        'duration': t.duration.days,
        'meetupAt': {
          'location': t.pickup_location,
          'time': t.start_timestamp.strftime(TIME_FMT),
        },
      })

    return response

  def getActiveRentedItems(self, rentee_id):
    # These items in the Transaction table held by the rentee, without any
    #  return requested.
    txs = Transaction.query.filter(and_(
      Transaction.rentee_id==rentee_id,
      Transaction.is_complete==False, #Transaction.start_timestamp<datetime.now(),
      Transaction.is_with_rentee==True,
    ))

    response = {
      "items": [],
      "description": "Rented Items",
    }
    for t in txs.all():
      if t.return_requested.count()>0:
        continue

      listed_item = t.listed_item
      item_type = listed_item.item_type
      duration = t.duration
      response['items'].append({
        'id': t.id,
        'listed_item_id': listed_item.id,
        'pic': item_type.image_url,
        'name': item_type.name,
        'owner': listed_item.owner.username,
        'duration': duration.days,
        'dueDate': (duration+t.start_timestamp).strftime(TIME_FMT),
      })
    return response

  def getReturnRequestedItems(self, rentee_id):
    # These items in the Transaction table where the rentee is finished and
    #  has requested a return. The owner has not responded yet.
    txs = Transaction.query.filter(and_(
      Transaction.rentee_id==rentee_id,
      Transaction.is_complete==False,
    ))

    response = {
      "items": [],
      "description": "Returns (Pending)",
    }
    for t in txs.all():
      return_requested = t.return_requested.first()
      if return_requested is None:
        continue

      elif return_requested.times_to_return.count() == 0:
        listed_item = t.listed_item
        item_type = listed_item.item_type
        duration = t.duration
        response['items'].append({
          'id': return_requested.id,
          'listed_item_id': listed_item.id,
          'pic': item_type.image_url,
          'name': item_type.name,
          'owner': listed_item.owner.username,
          'requestTime': return_requested.creation_time.strftime(TIME_FMT),
          'dueDate': (duration+t.start_timestamp).strftime(TIME_FMT),
        })
    return response

  def getItemsWithProposedReturnTimes(self, rentee_id):
    # These items in the Transaction table which the rentee wants to return,
    #  and the owner has proposed pickup times.
    txs = Transaction.query.filter(and_(
      Transaction.rentee_id==rentee_id,
      Transaction.is_complete==False,
    ))

    response = {
      "items": [],
      "description": "Returns (Approved for Scheduling)",
    }
    for t in txs.all():
      returnRequest = t.return_requested.first()
      if returnRequest is None:
        continue

      if (returnRequest.times_to_return.count() > 0 and returnRequest.will_be_returned_on.count() == 0):
        meetupTimes = []
        times_to_return = returnRequest.times_to_return.all()
        for r in times_to_return:
          _id = r.id
          meetupTimes.append({
            'id': r.id,
            'location': r.location,
            'start_time': r.proposed_timestamp.strftime(TIME_FMT),
            'end_time': r.can_pickup_until.strftime(TIME_FMT),
          })

        listed_item = t.listed_item
        item_type = listed_item.item_type
        duration = t.duration
        response['items'].append({
          'id': _id,
          'tx_id': t.id,
          'listed_item_id': listed_item.id,
          'pic': item_type.image_url,
          'name': item_type.name,
          'owner': listed_item.owner.username,
          'dueDate': (duration+t.start_timestamp).strftime(TIME_FMT),
          'meetupAt': meetupTimes,
        })
    return response

  def getItemsWithScheduledReturn(self, rentee_id):
    # These items in the Transaction table which the rentee wants to return,
    #  the owner has proposed pickup times, and a time has been scheduled.
    txs = Transaction.query.filter(and_(
      Transaction.rentee_id==rentee_id,
      Transaction.is_complete==False,
    ))

    response = {
      "items": [],
      "description": "Returns (Scheduled)",
    }
    for t in txs.all():
      returnRequest = t.return_requested.first()
      if returnRequest is None:
        continue

      if returnRequest.will_be_returned_on.count()==1:
        time_and_location = returnRequest.will_be_returned_on.first()
        listed_item = t.listed_item
        item_type = listed_item.item_type
        duration = t.duration
        response['items'].append({
          'id': t.id,
          'dropoff': True,
          'listed_item_id': listed_item.id,
          'pic': item_type.image_url,
          'name': item_type.name,
          'owner': listed_item.owner.username,
          'dueDate': (duration+t.start_timestamp).strftime(TIME_FMT),
          'meetupAt': {
            'location': time_and_location.location,
            'time': time_and_location.accepted_return_time\
                                     .strftime(TIME_FMT),
          },
        })
    return response

  def getCompletedTransactionsAsRentee(self, rentee_id):
    # These items in the Transaction table which the rentee wants to return,
    #  the owner has proposed pickup times, and a time has been scheduled.
    txs = Transaction.query.filter(and_(
      Transaction.rentee_id==rentee_id,
      Transaction.is_complete==True,
    ))

    response = {
      "items": [],
      "description": "Completed Transactions",
    }
    for t in txs.all():
        listed_item = t.listed_item
        item_type = listed_item.item_type
        days_of_rent = t.duration.days
        response['items'].append({
          'id': t.id,
          'listed_item_id': listed_item.id,
          'pic': item_type.image_url,
          'name': item_type.name,
          'owner': listed_item.owner.username,
          'cost': days_of_rent*listed_item.daily_rate,
        })
    return response


# User registration
class UserRegistration(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'firstName',
      help="First name of user",
      required=True,
    )
    parser.add_argument(
      'lastName',
      help="Last name of user",
      required=True,
    )
    parser.add_argument(
      'email',
      help="User's email address",
      required=True,
    )
    parser.add_argument(
      'password',
      help="Password",
      required=True,
    )
    parser.add_argument(
      'lat',
      type=float,
      help="User's location (latitude decimal degrees)",
    )
    parser.add_argument(
      'lon',
      type=float,
      help="User's location (longitude decimal degrees)",
    )
    args = parser.parse_args()

    print(request.form)
    firstName = args['firstName'] #request.form['firstName']
    lastName = args['lastName'] #request.form['lastName']
    email = args['email'] #request.form['email']
    password = args['password'] #request.form['password']

    """
    if "lat" in request.form and "long" in request.form:
      lat = request.form.get('lat', type=float)
      lon = request.form.get('lon', type=float)

    """
    lat = args['lat']
    lon = args['lon']
    if lat is None:
      lat = 35.4
      lon = -91.33

    try:
      new_user = User(
        f=firstName, l=lastName,
        email=email, password=password,
        lat=lat, lon=lon,
      )
      db.session.add(new_user)
      db.session.commit()
      _id = User.query.filter_by(email=email).first().id
      return {'user_id': _id}

    except:
      return {"status": "Error"}


# User log in
class UserLogIn(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'email',
      help="User's email address",
      required=True,
    )
    parser.add_argument(
      'password',
      help="User's password",
      required=True
    )
    args = parser.parse_args()

    """
    print(request.form)
    email = request.form.get('email')
    password = request.form.get('password')
    """
    email = args['email']
    password = args['password']
    matching_user = User.query.filter_by(email=email).first()
    if matching_user:
      return {'user_id': matching_user.id}

    else:
      return {'user_id': 2}


# Top-most categories listing
# Instant searching returns category names
# Keyword-based item listing
# Item details by category ID

class CategoryListing(Resource):
  def get(self):
    # Find leaf-node categories
    leaf_categories = Category.query.filter(
      Category.children==None,
    )

    # Find items listed in this category.
    categories_to_return = []
    for c in leaf_categories.all():
      fullname = str(c)
      parent_name = fullname.split(">")[0].strip()
      categories_to_return.append({
        'name': c.name,
        'pretty_print_name': c.name + " in " + parent_name,
      })

    return Response(
      json.dumps(categories_to_return),
      mimetype='application/json'
    )


#####################################################################
# Category-based item listing
#############################
class Search(Resource):
  def get(self, keyword):
    result = {
      "keyword": keyword,
    }

    # Find the category that has keyword in its name.
    qualifying_categories = Category.query.filter(and_(
      Category.name.ilike('%{}%'.format(keyword.lower())),
      Category.children==None,
    ))

    # Find items listed in this category.
    matching_items = []
    for c in qualifying_categories.all():
      category = {
        'id': c.id,
        'name': c.name,
        'fullname': str(c),
        'image_url': c.image_url,
      }

      processed_items = []
      raw_items = c.listed_items
      for i in raw_items.all():
        if i.is_available:
          processed_items.append({
            'id': i.id,
            'daily_rate': i.daily_rate,
            'image_url': c.image_url,
            'name': c.name,
            'owner': {
              'id': i.owner.id,
              'username': i.owner.username,
              'location': i.owner.getCityInfo(),
            }
          })
        
      category['items'] = processed_items
      matching_items.append(category)

    return Response(
      json.dumps(matching_items),
      mimetype='application/json'
    )


# Request item listing by Listed ID
class RenteeRequestItem(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'rentee_id',
      type=int,
      help='Primary key of user requesting item for rent',
    )
    parser.add_argument(
      'item_id',
      type=int,
      help='ListedItem primary key of item being requested',
    )
    parser.add_argument(
      'duration',
      type=int,
      help='Duration of time the rentee wishes to rent item',
    )
    args = parser.parse_args()
    rentee_id = args['rentee_id']
    listed_item_id = args['item_id']
    duration = args['duration']

    print("#"*100)
    print("POST request: {0}".format(args))
    rentee_id = args['rentee_id']
    listed_item_id = args['item_id']
    duration = args['duration']

    print("Rentee ID: {0}".format(rentee_id))
    print("Listed Item ID: {0}".format(listed_item_id))
    print("Duration: {0} days".format(duration))
    print("#"*100)
    rentee = User.query.filter_by(id=rentee_id).first()
    listed_item = ListedItem.query.filter_by(id=listed_item_id).first()
    r = listed_item.requestToRent(
      rentee=rentee, duration=timedelta(days=duration),
    )
    db.session.add(r)
    db.session.commit()
    return {'response': "Success!"}


# Owner suggests exchange time and location to the rentee for a
#  rent request.
class SuggestedItemPickupFromOwnerToRentee(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'fromTime',
      required=True,
      type=INCOMING_DATETIME_READER,
      help="The time the owner is able to meet up",
    )
    parser.add_argument(
      'toTime',
      required=True,
      type=INCOMING_DATETIME_READER,
      help="The time the owner will be unavailable after the fromTime",
    )
    parser.add_argument(
      'meetupAt',
      required=True,
      help="The location the owner is suggesting to meet up with the rentee",
    )
    parser.add_argument(
      'item_request_id',
      required=True,
      type=int,
      help="The associated RequestToRent id",
    )
    args = parser.parse_args()

    initial_request = RequestToRent.query.filter_by(
      id=args['item_request_id']
    ).first()
    suggestion = initial_request.suggestPickupTimes(
      available_from=args['fromTime'],
      available_until=args['toTime'],
      location=args['meetupAt']
    )
    db.session.add(suggestion)
    db.session.commit()
    return {'response': "Success!"}


# Rentee confirms an exchange time and location to the owner for
#  a rent request.
class ScheduledItemPickupFromOwnerToRentee(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'exactTime',
      required=True,
      type=INCOMING_DATETIME_READER,
      help="The time the rentee has confirmed to meet up with the owner",
    )
    parser.add_argument(
      'meetupAt',
      required=True,
      help="The location the rentee has agreed to meet up with the owner",
    )
    parser.add_argument(
      'item_request_id',
      dest="proposed_meetup_time_id",
      required=True,
      type=int,
      help="The ProposedMeetupTime primary key",
    )
    args = parser.parse_args()
    print(args)

    proposed_pickup_time = ProposedPickupTime.query.filter_by(
      id=args['proposed_meetup_time_id'],
    ).first()
    transaction = proposed_pickup_time.accept(
      exact_pickup_time=args['exactTime'],
    )
    db.session.add(transaction)
    db.session.commit()

    return {'response': "Success!"}


# Rentee confirm receipt of item from owner
class ConfirmItemPickupFromOwnerToRentee(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'item_request_id',
      dest='tx_id',
      type=int,
      help="Transaction ID of item being picked up by rentee",
      required=True,
    )
    args = parser.parse_args()
    tx = Transaction.query.filter_by(id=args['tx_id']).first()
    tx.confirmDroppedOffWithRentee()
    return {'response': "Success!"}


# User requests returning an item
class ReturnRequestByRentee(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'transaction_id',
      help="Unique ID for the transaction",
      required=True,
      type=int,
    )
    args = parser.parse_args()

    tx = Transaction.query.filter_by(id=args['transaction_id']).first()
    return_request = tx.requestToReturn()
    db.session.add(return_request)
    db.session.commit()
    
    return {'response': "Success!"}


# Owner suggests exchange time and location to the rentee for a
#  rent request.
class SuggestedItemPickupFromRenteeToOwner(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'fromTime',
      required=True,
      type=INCOMING_DATETIME_READER,
      help="The time the owner is able to meet up",
    )
    parser.add_argument(
      'toTime',
      required=True,
      type=INCOMING_DATETIME_READER,
      help="The time the owner will be unavailable after the fromTime",
    )
    parser.add_argument(
      'meetupAt',
      required=True,
      help="The location the owner is suggesting to meet up with the rentee",
    )
    parser.add_argument(
      'tx_id',
      dest='returnRequestId',
      required=True,
      type=int,
      help="The associated Transaction id",
    )
    args = parser.parse_args()
    print("#"*100)
    print(type(args['fromTime']))
    print("#"*100)

    return_request = ReturnRequest.query.filter_by(
      id=args['returnRequestId']
    ).first()
    suggestions = return_request.proposeReturnTimes(
      return_times=[
        (args['fromTime'], args['toTime'], args['meetupAt'])
      ]
    )
    db.session.add_all(suggestions)
    db.session.commit()
    return {'response': "Success!"}


# Rentee confirms an exchange time and location to the owner for
#  a return request.
class ScheduledItemPickupFromRenteeToOwner(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'exactTime',
      required=True,
      type=INCOMING_DATETIME_READER,
      help="The time the rentee has confirmed to meet up with the owner",
    )
    parser.add_argument(
      'meetupAt',
      required=True,
      help="The location the rentee has agreed to meet up with the owner",
    )
    parser.add_argument(
      'return_request_id',
      dest="proposed_meetup_time_id",
      required=True,
      type=int,
      help="The ProposedReturnTime primary key",
    )
    args = parser.parse_args()
    print(args)

    proposed_time = ProposedReturnTime.query.filter_by(
      id=args['proposed_meetup_time_id'],
    ).first()
    return_time = proposed_time.returnOn(
      return_time=args['exactTime'],
    )
    db.session.add(return_time)
    db.session.commit()

    return {'response': "Success!"}


# Owner confirms receipt of item from rentee
class ConfirmItemPickupFromRenteeToOwner(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'return_time_id',
      type=int,
      help="Transaction ID of item being picked up by rentee",
      required=True,
    )
    args = parser.parse_args()
    returnTime = ReturnTime.query.filter_by(id=args['return_time_id']).first()
    returnTime.confirmReturned()
    return {'response': "Success!"}


class ListedItemEndPoint(Resource):
  # Get specific information on a particular item
  def get(self, listed_item_id):
    pass

  # Create new listed item
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'item_type_id',
      type=int,
      required=True,
      help="Item Type of item to be listed",
    )
    parser.add_argument(
      'user_id',
      type=int,
      required=True,
      help="User ID of item owner",
    )
    parser.add_argument(
      'daily_rate',
      type=int,
      required=True,
      help="Daily rental rate of item",
    )
    args = parser.parse_args()

    item_category = Category.query.filter_by(id=args['item_type_id']).first()
    owner = User.query.filter_by(id=args['user_id']).first()
    listed_item = item_category.listMyItem(
      owner=owner,
      daily_rate=args['daily_rate'],
    )
    db.session.add(listed_item)
    db.session.commit()
    return {"response": "Success!"}


  # Update listed item with a new daily rate
  def put(self):
    parser = reqparse.RequestParser()
    parser.add_argument(
      'listed_item_id',
      type=int,
      required=True,
      help="Item Type of item to be listed",
    )
    parser.add_argument(
      'user_id',
      type=int,
      required=True,
      help="User ID of item owner",
    )
    parser.add_argument(
      'daily_rate',
      type=int,
      required=True,
      help="Daily rental rate of item",
    )
    args = parser.parse_args()

    listed_item = ListedItem.query.filter_by(id=args['listed_item_id']).first()
    listed_item.daily_rate = args['daily_rate']
    db.session.commit()
    return {"response": "Success!"}


  # Delete a listed item
  def delete(self, listed_item_id=None):
    if listed_item_id is None:
      print("!"*100)
      print("User did not use the RESTful URL!")
      print("!"*100)
      parser = reqparse.RequestParser()
      parser.add_argument(
        'listed_item_id',
        type=int,
        required=True,
        help="Item Type of item to be deleted",
      )
      args = parser.parse_args()
      listed_item_id = args['listed_item_id']

    ListedItem.query.filter_by(id=listed_item_id).delete()
    db.session.commit()
    return {"response": "Success!"}


if __name__ == '__main__':
  app = Flask(__name__)
  api = Api(app)
  app.run(debug=True)

