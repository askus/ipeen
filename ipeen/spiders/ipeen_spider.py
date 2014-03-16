#encoding=utf8
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor  
from scrapy.http import Request
from urlparse import urljoin 
from scrapy.selector import Selector 

from ipeen.items import *
import re 

class IpeenSpider( CrawlSpider ):
	name ="ipeen"
	allowed_domains = ["http://www.ipeen.com.tw"]
	start_urls = [  "http://www.ipeen.com.tw/shop/%d" % i for i in range( 1000 ) ]
	rules =[Rule( SgmlLinkExtractor( allow=('\/shop\/',), deny=('msg\.php',) ), callback='parse') ]

	def parse( self, response ):
			sel = Selector( response )
			store_item = StoreItem()

			# extract id 
			tmp = re.search( r"\/(\d+)-?.*$" , response.url )
			if tmp == None:
				return None 
			store_item['store_id'] = int( tmp.group(1) )

			# extract summary 
			store_item['summary'] = sel.css("div.summary::text")[0].extract().strip()

			# extract score 
			score_table_title2index = {"美味度": "deliciousness_score", "服務品質":"service_score", "環境設備":"environment_score","環境氣氛":"environment_score", "交通便利":"traffic_score"}
			score_table = zip( sel.css("dl.rating dt::text").extract(), map( int, sel.css("dl.rating dd .score-bar i").re(r'width: (\d+)%') ) )
			for raw_title , score in score_table:
				index =  score_table_title2index[ raw_title.strip().encode("utf8","ignore") ]
				store_item[index] = score 

			# extract top menu 
			top_menu_title2index= { "本店均消":"average_spend", "分享文數":"shared_number","收藏數":"collected_number","瀏覽數":"viewed_number" }
			top_menu = zip( sel.css("#shop-metainfo dl.info dt::text").extract() , sel.css("#shop-metainfo dl.info dd::text").extract() )
			for raw_title, raw_value in top_menu:
				raw_title =raw_title.strip().encode("utf8","ignore") 
				if not raw_title in  top_menu_title2index :
					continue
				index = top_menu_title2index[ raw_title  ]
				if( index in [ "average_spend", "shared_number", "collected_number","viewed_number"] ):
					tmp = re.search("(\d+) ", raw_value )
					if tmp != None:
						store_item[index] = int( tmp.group(1) )

			# extract from the table below 
			detail_table = sel.css("#shop-details tr");
			title2index = { "商家名稱":"name", "場所名稱":"name", "商家分類":"category", "標的分類":"category", 
			"電話":"telephone", "客服電話":"telephone", 
			 "地址":"address", "捷運資訊":"mrt", "公休日":"official_holiday","營業時間":"business_hours",
			 "媒體情報":"media_source","媒體推薦":"media_recommendations", "更新時間":"update_time"
			}

			for row in detail_table:
				index = title2index[ row.css("th::text")[0].extract().strip().encode("utf8","ignore") ]
				if( index =="category" or index =="media_source"):
					value = row.css("td a::text").extract()
				else:
					value = row.css("td::text")[0].extract().strip()
				store_item[index] = value 

			# extract lat and lng from "go to map" link
			lat, lng =  sel.css("a.whole-map::attr(href)")[0].re(r'\/c=([\d\.]+),([\d\.]+)\/')
			store_item['lat'] = float( lat ) 
			store_item['lng'] = float( lng ) 

			# extract recommendations
			store_item['recommendations'] = [] 
			raw_recommendation_table = sel.css( "div.recommend li a::text").re(r"([^)]+)\((\d+)\)")
			recommendation_table = zip( raw_recommendation_table[::2], map( int , raw_recommendation_table[1::2] ) )
			for title, count  in recommendation_table:
				recommendation = Recommendation()
				recommendation['title'] = title 
				recommendation['count'] = count 
				store_item['recommendations'].append( recommendation )
			
			# extract tags 
			store_item['tags'] = []
			raw_tag_table = sel.css("div.tags li a::text").re(r"([^)]+)\((\d+)\)")
			tag_table = zip( raw_tag_table[::2], map( int, raw_tag_table[1::2]  ) )
			for title, count in tag_table:
				tag = Tag()
				tag['title'] = title 
				tag['count'] = count 
				store_item['tags'].append( tag )

			return store_item  
	
