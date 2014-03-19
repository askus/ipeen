#encoding=utf8
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor  
from scrapy.http import Request
from urlparse import urljoin 
from scrapy.selector import Selector 
import urlparse


from ipeen.items import *
import re 
from scrapy.exceptions import IgnoreRequest

class IpeenSpider( CrawlSpider ):
	name ="ipeen"
	allowed_domains = ["www.ipeen.com.tw"]
	# start_urls = [ "http://www.ipeen.com.tw/shop/632396"]
	#start_urls = [ "http://www.ipeen.com.tw/shop/632%03d" % i for i in range( 1000) ]
	
	start_urls = [ "http://www.ipeen.com.tw/search/taiwan/000/1-0-0-0/?p=%d" % i for i in range( 1, 7007 )  ]
	#start_urls = [ "http://www.ipeen.com.tw/search/taiwan/000/1-0-0-0/?p=%d" % i for i in range( 1, 10 )  ]


#	rules = [ 
#		Rule( SgmlLinkExtractor( allow=(r'\/shop\/\d+-?[\/]*',), deny=('msg\.php','discount') ), callback='parse_store'),
#		Rule( SgmlLinkExtractor( allow=(r'\/search\/taiwan\/000\/1-0-0-0/\?p',)), )
#	]

	#rules = [ 
	#	Rule( SgmlLinkExtractor( allow=(r'\/search\/taiwan\/000\/1-0-0-0/\?p',)), callback='parse_start_url' )
	#]

	download_delay = .25
	#start_urls =["http://www.ipeen.com.tw/shop/632004"]
	#start_urls = [  "http://www.ipeen.com.tw/shop/%d" % i for i in range( 1000 ) ]
	#rules =[ Rule( SgmlLinkExtractor( allow=('\/shop\/\d+-?[\/]*',), deny=('msg\.php',) ), callback='parse_start_url') ]

	def parse_start_url( self, response ):
		sel = Selector( response )
		partial_store_links = sel.css("article.serItem div.serShop h3 a::attr(href)").extract()
		print "[%s] item: %d" %( response.url , len( partial_store_links ) )
		for partial_store_link in partial_store_links :
			user_store_link = urlparse.urljoin( response.url, partial_store_link  )
			request = Request( user_store_link,  callback =self.parse_store )
			yield request 


	def parse_store( self, response ):
			sel = Selector( response )
			store_item = StoreItem()

			# extract id 
			tmp = re.search( r"\/(\d+)-?.*$" , response.url )

			if tmp == None:
				raise IgnoreRequest("Error: %s is not valid." % response.url )
				yield None 
			store_item['store_id'] = int( tmp.group(1) )

			# extract summary 
			#print sel.css("div.summary::text")
			store_item['summary'] = sel.css("div.summary::text")[0].extract().strip()

			# extract score 
			score_table_title2index = {"美味度": "deliciousness_score", "服務品質":"service_score", "環境設備":"environment_score","環境氣氛":"environment_score", "交通便利":"traffic_score"}
			score_table = zip( sel.css("dl.rating dt::text").extract(), map( int, sel.css("dl.rating dd .score-bar i").re(r'width: (\d+)%') ) )
			other_score_information = {}
			for raw_title , score in score_table:
				title = raw_title.strip().encode("utf8","ignore") 
				if( not title in score_table_title2index ):
					other_score_information[title] = score 
					continue 
				index =  score_table_title2index[ title ]
				store_item[index] = score 
			store_item['other_score_information'] = other_score_information

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
			 "媒體情報":"media_source","媒體推薦":"media_recommendations", "更新時間":"update_time",
			 "席       位":"seats", "付款方式":"payment", "停車資訊":"parking","官方網站":"official_site",
			 "營業資訊":"additional_information","建立者":"author","消費價位":"spend_class"
			}

			other_information = {}
			for row in detail_table:
				title = row.css("th::text")[0].extract().strip().encode("utf8","ignore")
				if not title in title2index:
					try: 
						value = row.css("td::text")[0].extract()
						other_information[title] = value 
						continue 
					except:
						continue

				index = title2index[ row.css("th::text")[0].extract().strip().encode("utf8","ignore") ]
				if( index in  ["category","media_source"]):
					value = row.css("td a::text").extract()
				elif( index in ["author"]):
					value = row.css("a::text")[0].extract()
				elif( index in ["official_site"] ):
					value = row.css("a::attr(href)")[0].extract()
				elif( index in ["spend_class"]):
					value = int( row.css("td::text")[0].re("(\d+)")[0] )
				else:
					value = row.css("td::text")[0].extract().strip()
				store_item[index] = value 
			store_item[ 'other_information' ] = other_information

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

			# extract user review 
			store_item['user_reviews'] = []
			for partial_user_review_link in sel.css("section.review-list article h2 a.ga_tracking::attr(href)").extract():
				user_review_link = urlparse.urljoin( response.url,partial_user_review_link  )
				request = Request( user_review_link, meta={"store_item":store_item}, callback = self.parse_review )
				yield request 
			if( len( sel.css("section.review-list article h2 a.ga_tracking::attr(href)").extract() )  == 0 ):
				yield store_item


	def parse_review( self, response ):
		store_item = response.request.meta['store_item']

		sel = Selector( response )
		
		user_review = UserReview()
		# 
		user_review['title'] = sel.css("div.info h1::text")[0].extract().strip()
		user_review['published_date'] = sel.css("div.brief p.date span::text")[0].extract()
		user_review['average_score'] = int( sel.css("span.large-heart i::attr(class)")[0].re("s-(\d+)")[0] )

		score_title2index = { "美味度：":"deliciousness_score", "服務品質：":"service_score","環境氣氛：":"environment_score","交通便利：":"traffic_score"}
		score_titles = sel.css("dl.rating dt::text").extract() 
		score_values = sel.css("dl.rating dd::text").extract()

		other_score_information = {}
		for title, value in zip( score_titles, score_values ):
			title = title.encode("utf8")
			if not title in score_title2index :
				other_score_information[ title ] = value 
				continue 
			user_review[ score_title2index[title] ] = value 
		user_review['other_score_information'] = other_score_information

		tmp = sel.css("div.actions span")
		user_review['responsed_number'] = int( tmp[0].css("a.ga_tracking span::text")[0].extract() )	

		user_review['viewed_number']= int( tmp[2].re(" (\d+) ")[0] )
		user_review['user_name'] = sel.css("figcaption h3 a.ga_tracking::text")[0].extract().strip()
		user_review['user_level'] = sel.css("figcaption p span::text")[0].extract()
		user_review['user_publish_count'] = int( sel.css("figcaption p span::text")[1].re(r'(\d+)')[0] )
		user_review['description'] = "\n".join( [ l.strip() for l in sel.xpath('//div[@class="description"]//text()').extract() if len( l.strip() ) > 0 ] ) 
		store_item['user_reviews'].append( user_review)
		yield store_item


