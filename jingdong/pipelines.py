# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from pymongo import MongoClient

class JingdongPipeline(object):

    collection_name = 'jd_nike_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        ## how to handle each post
        self.db[self.collection_name].insert(dict(item))
        logging.debug("Item added to MongoDB")
        return item







    # def __init__(self):
    #     self.conn = pymysql.connect(host='127.0.0.1',port=3306,user ='root',passwd='root',db='jingdong',charset='utf8')
    #     self.cursor = self.conn.cursor()

    # def process_item(self, item, spider):
    #     try:#有些标题会重复，所以添加异常
    #         title = item['title']
    #         comment_count = item['comment_count']  # 评论数
    #         shop_url = item['shop_url'] # 店铺链接
    #         price = item['price']
    #         goods_url = item['goods_url']
    #         shops_id = item['shops_id']
    #         goods_id =int(item['goods_id'])
    #         #sql = 'insert into jingdong_goods(title,comment_count,shop_url,price,goods_url,shops_id) VALUES (%(title)s,%(comment_count)s,%(shop_url)s,%(price)s,%(goods_url)s,%(shops_id)s,)'
    #         try:
    #             self.cursor.execute("insert into jingdong_goods(title,comment_count,shop_url,price,goods_url,shops_id,goods_id)values(%s,%s,%s,%s,%s,%s,%s)", (title,comment_count,shop_url,price,goods_url,shops_id,goods_id))

    #             self.conn.commit()
    #         except Exception as e:
    #             pass

    #     except Exception as e:
    #         pass

    # def close_spider(self):
    #     self.conn.close()