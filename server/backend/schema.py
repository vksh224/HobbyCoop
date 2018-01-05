import logging
logger = logging.getLogger("hobbycooperative.schema")
from backend import db

#try:
#  from geopy.geocoders import Nominatim

#except:
#  logger.exception("""
#
#Please install geopy.
#$ sudo pip install geopy
#  """)
#  exit()

#else:
#  GEOLOCATOR = Nominatim()


from datetime import datetime


# For the time being, we'll be doing simple plaintext passwords. However, this
#  will need to be changed once this system is fully up and running.
class User(db.Model):
  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key=True)
  firstname = db.Column(db.String(80))
  lastname = db.Column(db.String(80))
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)

  def __init__(self, f, l, email, password, lat, lon):
    self.firstname = f
    self.lastname = l
    self.username = "{0} {1}".format(f, l)
    self.email = email
    self.password = password
    self.latitude = lat
    self.longitude = lon

  def getCityInfo(self):
    """
    try:
      location = GEOLOCATOR.reverse(
        query="{0.latitude}, {0.longitude}".format(self),
        exactly_one=True,
      )
      city = location.raw['address']['city']
      state = location.raw['address']['state']
    except:
      logging.exception("Something went wrong reverse looking up lat-longs"
                        " into a city and state combo.")
      city = "<private>"
      state = "Missouri"

    return "{0}, {1}".format(city, state)
    """
    return "Rolla, MO"

  def __repr__(self):
    return "<{0} at ({1}, {2})>".format(
      self.username,
      self.latitude,
      self.longitude,
    )


class ListedItem(db.Model):
  __tablename__ = "listed_item"
  id = db.Column(db.Integer, primary_key=True)

  # This is the number of cents one wants to sell.
  #  Divide by 100 to show dollar amount.
  daily_rate = db.Column(db.Integer, nullable=False)
  is_available = db.Column(db.Boolean, nullable=False)

  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  owner = db.relationship(
    'User',
    backref=db.backref('items', lazy='dynamic'),
  )

  item_type_id = db.Column(db.Integer, db.ForeignKey('category.id'))
  item_type = db.relationship(
    'Category',
    backref=db.backref('listed_items', lazy='dynamic'),
  )

  def __init__(self, rate, owner, item_type):
    self.daily_rate = rate
    self.owner = owner
    self.item_type = item_type
    self.is_available = True

  def requestToRent(self, rentee, duration):
    request = RequestToRent(
      listed_item=self,
      duration_of_rent=duration,
      rentee=rentee,
    )
    return request

  def __repr__(self):
    return ("<{4}{0} (item #{1}) from {2} rated at"
            " ${3:,.2f} daily>".format(
      self.item_type.name,
      self.id,
      self.owner.username,
      float(self.daily_rate)/100,
      "" if self.is_available else "UNAVAILABLE: ",
    ))


class Category(db.Model):
  __tablename__ = "category"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  image_url = db.Column(db.String(120))

  # Might be more efficient to list children via foreign key and
  #  parent via backref.
  parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
  parent = db.relationship(
    'Category',
    remote_side=id,
    backref=db.backref('children', lazy='dynamic'),
  )

  def __init__(self, name, image_url=None, parent=None):
    self.name = name
    self.image_url = image_url
    self.parent = parent

  def listMyItem(self, owner, daily_rate):
    # The Category needs to be a leaf category.
    if self.children.count() == 0:
      logger.debug("#"*80)
      logger.info("New item listed!")
      l = ListedItem(
        rate=daily_rate, 
        owner=owner,
        item_type=self,
      )
      logger.info(l)
      logger.debug("#"*80)
      return l

    else:
      raise Exception("An item cannot be listed as an vague item type."
                      " Please choose the most descriptive item category"
                      " available.")

  def __repr__(self):
    if self.parent == None:
      return self.name

    else:
      return "{0} > {1}".format(self.parent, self.name)


class RequestToRent(db.Model):
  __tablename__ = "request_to_rent"
  id = db.Column(db.Integer, primary_key=True)
  request_created_timestamp = db.Column(db.DateTime, nullable=False)
  #days_of_rent = db.Column(db.Integer, nullable=False)
  duration_of_rent = db.Column(db.Interval, nullable=False)

  listed_item_id = db.Column(db.Integer, db.ForeignKey('listed_item.id'))
  listed_item = db.relationship(
    'ListedItem',
    backref=db.backref('requests', lazy='dynamic'),
  )
  rentee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  rentee = db.relationship(
    'User',
    backref=db.backref('requests', lazy='dynamic'),
  )

  def __init__(self, listed_item, duration_of_rent, rentee):
    self.request_created_timestamp = datetime.utcnow()
    self.listed_item = listed_item
    self.rentee = rentee
    self.duration_of_rent = duration_of_rent

  def suggestPickupTimes(self, available_from, available_until, location):
    return ProposedPickupTime(
      request=self,
      meetup_time=available_from,
      available_until=available_until,
      location=location,
    )

  def __repr__(self):
    return (
    "<{0} requested a {1} (item #{2}) at {3} for {4}\n"
    "{5} will need to choose pickup times before request is accepted>".format(
      self.rentee.username,
      self.listed_item.item_type.name,
      self.listed_item.id,
      self.request_created_timestamp,
      self.duration_of_rent,
      self.listed_item.owner.username,
    ))


class ProposedPickupTime(db.Model):
  __tablename__ = "proposed_pickup_time"
  id = db.Column(db.Integer, primary_key=True)
  proposed_meetup_time = db.Column(db.DateTime, nullable=False)
  owner_available_until = db.Column(db.DateTime, nullable=False)
  location = db.Column(db.String(120), nullable=False)

  request_id = db.Column(db.Integer, db.ForeignKey('request_to_rent.id'))
  request = db.relationship(
    'RequestToRent',
    backref=db.backref(
      "pickup_times",
      lazy='dynamic',
      cascade="save-update, merge, delete"
    ),
  )

  def __init__(self, request, meetup_time, available_until, location):
    self.request = request
    self.proposed_meetup_time = meetup_time
    self.owner_available_until = available_until
    self.location = location

  def accept(self, exact_pickup_time):
    # Create the transaction item.
    duration_of_rent = self.request.duration_of_rent
    item = self.request.listed_item
    money_owed = duration_of_rent.days*item.daily_rate
    transaction_to_pay = Transaction(
      start_timestamp=exact_pickup_time,
      duration=self.request.duration_of_rent,
      payment_total=money_owed,
      listed_item=item,
      rentee=self.request.rentee,
      pickup_location=self.location,
    )
    item.is_available = False
    db.session.delete(self.request)
    db.session.commit()

    # Delete associated proposed pickup times and rent request items.
    return transaction_to_pay

  def __repr__(self):
    return "{0} proposed {1} pickup the {2} between {3} and {4} at {5}".format(
      self.request.listed_item.owner.username,
      self.request.rentee.username,
      self.request.listed_item.item_type.name,
      self.proposed_meetup_time,
      self.owner_available_until,
      self.location,
    )


class Transaction(db.Model):
  __tablename__ = "transaction"
  id = db.Column(db.Integer, primary_key=True)
  start_timestamp = db.Column(db.DateTime, nullable=False)
  pickup_location = db.Column(db.String(120), nullable=False)
  duration = db.Column(db.Interval, nullable=False)
  payment_total = db.Column(db.Integer, nullable=False)
  is_complete = db.Column(db.Boolean, nullable=False)
  is_with_rentee = db.Column(db.Boolean, nullable=False)

  listed_item_id = db.Column(db.Integer, db.ForeignKey('listed_item.id'))
  listed_item = db.relationship(
    'ListedItem',
    backref=db.backref('transactions', lazy='dynamic'),
  )

  rentee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  rentee = db.relationship(
    'User',
    backref=db.backref('transactions', lazy='dynamic'),
  )

  def __init__(self, start_timestamp, duration, payment_total,
               listed_item, rentee, pickup_location):
    self.start_timestamp = start_timestamp
    self.duration = duration
    self.payment_total = payment_total
    self.listed_item = listed_item
    self.rentee = rentee
    self.pickup_location = pickup_location
    self.is_with_rentee = False
    self.is_complete = False

  def confirmDroppedOffWithRentee(self):
    self.is_with_rentee = True
    db.session.commit()

  def requestToReturn(self):
    # Iterate through each proposed meetup points.
    return ReturnRequest(tx=self)

  def __repr__(self):
    return ("<Tx #{0.id}: {0.rentee.username} paid {0.payment_total} to rent "
            "{0.listed_item.item_type.name} for {0.duration} starting on "
            "{0.start_timestamp}.".format(self))

class ReturnRequest(db.Model):
  __tablename__ = "return_request"
  id = db.Column(db.Integer, primary_key=True)
  creation_time = db.Column(db.DateTime, nullable=False)

  transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
  transaction = db.relationship(
    'Transaction',
    backref=db.backref('return_requested', lazy='dynamic'),
  )

  def __init__(self, tx):
    self.creation_time = datetime.now()
    self.transaction = tx

  def proposeReturnTimes(self, return_times):
    # The owner proposes return times to the rentee.
    return_time_proposals = []
    for meetup_start, meetup_stop, location in return_times:
      proposal = ProposedReturnTime(
        start=meetup_start,
        stop=meetup_stop,
        request=self,
        location=location,
      )
      return_time_proposals.append(proposal)
    return return_time_proposals

  def __repr__(self):
    return "{0} has requested returning {1} to {2}".format(
      self.transaction.rentee.username,
      self.transaction.listed_item.item_type.name,
      self.transaction.listed_item.owner.username,
    )


class ProposedReturnTime(db.Model):
  __tablename__ = "proposed_return_time"
  id = db.Column(db.Integer, primary_key=True)
  location = db.Column(db.String(80), nullable=False)
  proposed_timestamp = db.Column(db.DateTime, nullable=False)
  can_pickup_until = db.Column(db.DateTime, nullable=False)

  request_id = db.Column(db.Integer, db.ForeignKey('return_request.id'))
  request = db.relationship(
    'ReturnRequest',
    backref=db.backref(
      'times_to_return',
      lazy='dynamic',
      cascade="all, delete-orphan"
    ),
  )

  def __init__(self, start, stop, request, location):
    self.location = location
    self.proposed_timestamp = start
    self.can_pickup_until = stop
    self.request = request

  def returnOn(self, return_time):
    r = ReturnTime(
      return_time=return_time,
      request=self.request,
      location=self.location,
    )
    return r

  def __repr__(self):
    tx = self.request.transaction
    item = tx.listed_item
    return ("{0} is available to recieve {1} from {2}"
            " between {3} and {4} at {5}".format(
      item.owner.username,
      item.item_type.name,
      tx.rentee.username,
      self.proposed_timestamp,
      self.can_pickup_until,
      self.location,
    ))


class ReturnTime(db.Model):
  __tablename__ = "return_time"
  id = db.Column(db.Integer, primary_key=True)
  accepted_return_time = db.Column(db.DateTime, nullable=False)
  location = db.Column(db.String(120), nullable=False)

  request_id = db.Column(db.Integer, db.ForeignKey('return_request.id'))
  request = db.relationship(
    'ReturnRequest',
    backref=db.backref(
      'will_be_returned_on',
      lazy='dynamic',
      cascade="all, delete-orphan",
    ),
  )

  def __init__(self, return_time, request, location):
    self.accepted_return_time = return_time
    self.request = request
    self.location = location

  def confirmReturned(self):
    # The item should be marked as available again.
    tx = self.request.transaction
    tx.is_complete = True
    tx.is_with_rentee = False
    tx.listed_item.is_available = True

    # All return request objects should be deleted.
    db.session.delete(self.request)
    db.session.commit()
    return True

  def __repr__(self):
    tx = self.request.transaction
    item = tx.listed_item
    return "{0} will return {1}'s {2} on {3} at {4}".format(
      tx.rentee.username,
      item.owner.username,
      item.item_type.name,
      self.accepted_return_time,
      self.location,
    )

