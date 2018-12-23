from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import BodyPart, Base, Workout, User

engine = create_engine('sqlite:///weightlifting.db')

"""Binds variable engine to the metadata of the Base class so that
the declarative statements can be acessed through a DBSession"""

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Populates User table with dummy record


User1 = User(name="Guest User", email="anthonym.cordova@gmail.com",
             picture=("https://www.tenforums.com/geek/gars/images/2/types/"
                      "thumb_14400082930User.png"))

session.add(User1)
session.commit()

# Populates first BodyPart record: Chest


bodypart1 = BodyPart(user_id=1, name="Chest")
session.add(bodypart1)
session.commit()

""" Populates 2 records for the Workout table that have
a relationship with bodypart1"""


workout1 = Workout(user_id=1, name="Lying Bench Press",
                   description=("Person lies on a bench "
                                "and raises a weight with both arms."),
                   difficulty="high", bodypartrel=bodypart1)

session.add(workout1)
session.commit()

workout2 = Workout(user_id=1, name="Seated Machine Press",
                   description=("Upright version of the "
                                "standard lying bench press"),
                   difficulty="low", bodypartrel=bodypart1)

session.add(workout2)
session.commit()


# Populates second BodyPart record: Back


bodypart2 = BodyPart(user_id=1, name="Back")
session.add(bodypart2)
session.commit()

"""Populates 2 records for the Workout table that
have a relationship with bodypart2"""


workout1 = Workout(user_id=1, name="Deadlift",
                   description=("Barbell is lifted off the ground to "
                                "the level of the hips, then "
                                "lowered to the ground."),
                   difficulty="high", bodypartrel=bodypart2)

session.add(workout1)
session.commit()

workout2 = Workout(user_id=1, name="Pull Up",
                   description="Hold on to a bar and pull up to your neck.",
                   difficulty="low", bodypartrel=bodypart2)

session.add(workout2)
session.commit()


# Populates third BodyPart record: Legs


bodypart3 = BodyPart(user_id=1, name="Legs")
session.add(bodypart3)
session.commit()

""" Populates 2 records for the Workout table that
have a relationship with bodypart3"""


workout1 = Workout(user_id=1, name="Squat",
                   description=("Barbell is placed on shoulders and person "
                                "squats down and pushes up away from "
                                "the floor."),
                   difficulty="high", bodypartrel=bodypart3)

session.add(workout1)
session.commit()

workout2 = Workout(user_id=1, name="Leg Press",
                   description=("Person pushes a weight or resistance "
                                "away from them using their legs."),
                   difficulty="low", bodypartrel=bodypart3)

session.add(workout2)
session.commit()

# Prints the below to console


print "Populated the Weightlifting DB!!!"
