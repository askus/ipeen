from ipeen.spiders.ipeen_spider import IpeenSpider

class IpeenCuisineSpider( IpeenSpider ):
	name ="ipeen_cuisine"
	start_urls = [ "http://www.ipeen.com.tw/search/taiwan/000/1-0-0-0/?p=%d" % i for i in range( 1, 7007 )  ]
