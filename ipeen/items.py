# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class StoreItem(Item):
    # define the fields for your item here like:
    # name = Field()

    #
    store_id = Field()
    #
    summary = Field() 

    # 
    deliciousness_score = Field()
    service_score = Field()
    environment_score = Field()
    traffic_score = Field()
    other_score_information = Field()

    # from top menu
    average_spend = Field() 
    shared_number = Field()
    collected_number=  Field() 
    viewed_number= Field()
    
    # the below table 
    name = Field()
    category = Field() 
    telephone = Field()
    address = Field()
    mrt = Field()
    official_holiday = Field()
    business_hours = Field() 
    media_source = Field()
    media_recommendations = Field()
    update_time = Field() 
    seats = Field()
    payment = Field()
    parking = Field()
    official_site = Field()
    additional_information = Field()
    author =Field()
    spend_class= Field()
    other_information = Field()


    # from the right-below coner
    recommendations = Field()
    tags = Field()

    # from the "go to map" link
    lat = Field()
    lng = Field()

    # from user review 
    user_reviews = Field()
    pass

class Tag(Item):
	title = Field()
	count = Field()

class Recommendation(Item):
	title = Field()
	count = Field() 

class UserReview( Item):
    title = Field()
    published_date= Field()
    average_score = Field()
    deliciousness_score = Field()
    service_score = Field()
    environment_score = Field()
    traffic_score = Field() 
    other_score_information = Field()
    responsed_number = Field()
    viewed_number = Field()
    user_name = Field()
    
    user_level = Field()
    user_publish_count = Field()
    description = Field()
