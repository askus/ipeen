# Scrapy settings for ipeen project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ipeen'

SPIDER_MODULES = ['ipeen.spiders']
NEWSPIDER_MODULE = 'ipeen.spiders'

DOWNLOAD_DELAY = 2
DOWNLOAD_TIMEOUT = 30
#USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22 AlexaToolbar/alxg-3.1"

"""
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': 123,
}
"""
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ipeen (+http://www.yourdomain.com)'
