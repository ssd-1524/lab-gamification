from sqlalchemy import Enum

role_names = Enum("Viewer", "Operator", "Executive", "Manager",name = "role_names",create_type=False)

question_types = Enum("Sugarcane", "Role", "Plan",name = "question_types",create_type=False )

rank_types = Enum("Bronze", "Silver", "Gold", "Platinum", "Diamond",name = "rank_types",create_type=False )

point_types = Enum("Quiz", "Streak", "Manual", "Badges",name = "point_types",create_type=False )

plan_types = Enum("Basic", "Prime", "Nexus",name = "plan_types",create_type=False )

location_names = Enum("Gautemala", "Nicaragua", "Mexico Panuco", "Mexico El Mante",name = "location_names" ,create_type=False )