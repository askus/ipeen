#encoding=utf8

from ipeen.spiders.ipeen_spider import IpeenSpider

class IpeenAllSpider( IpeenSpider):
	name ="ipeen_all"
	start_urls= [ "http://www.ipeen.com.tw/search/taiwan/000/0-100-0-0/?p=%d" % i for i in range( 1, 17478)]

