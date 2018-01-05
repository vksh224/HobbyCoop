import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("hobbycooperative.createSample")

from backend import db
from backend.schema import Category
from pprint import pprint

def createInitialCategories():
  tools_and_hardware = Category(name="Tools & Hardware")
  power_tools = Category(name="Power Tools", parent=tools_and_hardware)
  woodworking_tools = Category(name="Woodworking Tools", parent=power_tools)
  drills = Category(
    name="Power Drill",
    parent=woodworking_tools,
    image_url="http://i.imgur.com/3TKBF5L.jpg",
  )
  circular_saw = Category(
    name="Circular Saw",
    parent=woodworking_tools,
    image_url="http://i.imgur.com/eQUG4GO.jpg",
  )
  belt_sander = Category(
    name="Belt Sander",
    parent=woodworking_tools,
    image_url="http://i.imgur.com/miFFFR4.jpg",
  )

  shop_cleaning = Category(name="Workshop Cleaning", parent=power_tools)
  shop_vac = Category(
    name="Workshop Vaccuum Cleaner",
    parent=shop_cleaning,
    image_url="http://i.imgur.com/EVZna2p.jpg",
  )

  gardening = Category(name="Gardening & Lawn Care")
  lawn_care = Category(name="Lawn Care", parent=gardening)
  lawn_mower = Category(
    name="Lawn Mower",
    parent=lawn_care,
    image_url="http://i.imgur.com/O9xk2WE.jpg",
  )
  post_hole_digger = Category(
    name="Post Hole Digger",
    parent=lawn_care,
    image_url="http://i.imgur.com/Kwejc6c.jpg",
  )

  moving = Category(name="Moving Supplies")
  trucks_and_dollies = Category(name="Hand Trucks & Dollies", parent=moving)
  heavy_duty_dollies = Category(
    name="Heavy-Equipment Dolly",
    parent=trucks_and_dollies,
    image_url="http://i.imgur.com/8BUdpnF.jpg",
  )
  pet_moving = Category(name="Animal Movers", parent=moving)
  cat_carrier = Category(
    name="Cat Carrier",
    parent=pet_moving,
    image_url="http://i.imgur.com/p1mS3Xd.jpg",
  )

  outdoor_recreation = Category(name="Outdoor Recreation")
  camping = Category(name="Camping Equipment", parent=outdoor_recreation)
  tents = Category(name="Tents", parent=camping)
  four_person_tent = Category(
    name="Four-Person Tent",
    parent=tents,
    image_url="http://i.imgur.com/miFFFR4.jpg"
  )

  floating = Category(name="Water Sports")
  kayaks = Category(name="Kayaks", parent=floating)
  sot_kayak = Category(
    name="Sit-On-Top Kayak",
    parent=kayaks,
    image_url="http://i.imgur.com/ayCwLo6.jpg",
  )

  household_items = Category(name="Household Items")
  cleaning = Category(name="Cleaning Equipment", parent=household_items)
  vaccuum_cleaner = Category(
    name="Vaccuum Cleaner",
    parent=cleaning,
    image_url="http://i.imgur.com/shBpBRE.jpg",
  )

  ALL_CATEGORIES = [
    tools_and_hardware,
    power_tools,
    woodworking_tools,
    drills,
    circular_saw,
    belt_sander,
    shop_cleaning,
    shop_vac,
    gardening,
    lawn_care,
    lawn_mower,
    post_hole_digger,
    moving,
    trucks_and_dollies,
    heavy_duty_dollies,
    pet_moving,
    cat_carrier,
    outdoor_recreation,
    camping,
    tents,
    four_person_tent,
    floating,
    kayaks,
    sot_kayak,
    household_items,
    cleaning,
    vaccuum_cleaner,
  ]
  LEAF_CATEGORIES = [
    drills, circular_saw, belt_sander, shop_vac,
    heavy_duty_dollies, cat_carrier,
    lawn_mower,
    four_person_tent,
    sot_kayak,
    vaccuum_cleaner,
  ]
  return ALL_CATEGORIES, LEAF_CATEGORIES


if __name__ == "__main__":
  # Drop the tables
  db.drop_all()

  # Recreate the tables
  db.create_all()

  # Create initial categories
  all_categories, leaf_categories = createInitialCategories()
  db.session.add_all(all_categories)
  db.session.commit()

  print("Categories available:")
  pprint(Category.query.all())
  print("-"*80)

