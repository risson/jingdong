# -*- coding: utf-8 -*-
import scrapy
import re

from jingdong.items import JingdongItem

class JdSpider(scrapy.Spider):
    name = "nike"
    allowed_domains = ["www.jd.com"]
    start_urls = ['http://www.jd.com/']


    search_url1 = 'https://search.jd.com/Search?keyword={key}&enc=utf-8&cid3={category}&page={page}'

    search_url2= 'https://search.jd.com/s_new.php?keyword={key}&enc=utf-8&cid3={category}&page={page}&s=26&scrolling=y&pos=30&tpl=3_L&show_items={goods_items}'
    

    def start_requests(self):
        key = 'nike'
        categories = [9754,9757,9756,12100,9758] #部分鞋子类别
        for category in categories:

            for num in range(1,100):
                page1 = str(2*num-1)#构造页数
                page2 = str(2*num)
                yield scrapy.Request(url=self.search_url1.format(key=key,category=category,page=page1),callback=self.parse,dont_filter = True)
                yield scrapy.Request(url=self.search_url1.format(key=key,category=category,page=page1),callback=self.get_next_half,meta={'page2':page2, 'category':category, 'key':key},dont_filter = True)
                #这里一定要加dont_filter = True，不然scrapy会自动忽略掉这个重复URL的访问

    def get_next_half(self,response):
        try:
            items = response.xpath('//*[@id="J_goodsList"]/ul/li/@data-pid').extract()
            key = response.meta['key']
            category = response.meta['category']
            page2 =response.meta['page2']
            goods_items=','.join(items)
            yield scrapy.Request(url=self.search_url2.format(key=key, category=category, page=page2, goods_items=goods_items),
                                 callback=self.next_parse,dont_filter=True)#这里不加这个的话scrapy会报错dont_filter，官方是说跟allowed_domains冲突，可是第一个请求也是这个域名，实在无法理解

        except Exception as e:
            print('没有数据')



    def parse(self, response):
        all_goods = response.xpath('//div[@id="J_goodsList"]/ul/li')
        for one_good in all_goods:
            item = JingdongItem()

            try:
                data = one_good.xpath('div/div/a/em')
                item['title'] = data.xpath('string(.)').extract()[0]#提取出该标签所有文字内容
                item['comment_count'] = one_good.xpath('div/div[@class="p-commit"]/strong/a/text()').extract()[0]#评论数
                item['goods_url'] = 'http:'+one_good.xpath('div/div[4]/a/@href').extract()[0]#商品链接
                item['shop_url'] = 'http:'+one_good.xpath('div/div[7]/span/a/@href').extract()[0]#店铺链接
                item['shops_id']=self.find_shop_id(item['shop_url'])#店铺ID
                goods_id=one_good.xpath('div/div[2]/div/ul/li[1]/a/img/@data-sku').extract()[0]
                if goods_id:
                    item['goods_id'] =goods_id
                price=one_good.xpath('div/div[3]/strong/i/text()').extract()#价格
                if price:#有写商品评论数是0，价格也不再源代码里面，应该是暂时上首页的促销商品，每页有三四件，我们忽略掉
                    item['price'] =float(price[0])


                yield item
            except Exception as e:
                pass


    def next_parse(self,response):
        all_goods=response.xpath('/html/body/li')
        for one_good in all_goods:
            item = JingdongItem()
            try:
                data = one_good.xpath('div/div/a/em')
                item['title'] = data.xpath('string(.)').extract()[0]  # 提取出该标签所有文字内容
                item['comment_count'] = one_good.xpath('div/div[@class="p-commit"]/strong/a/text()').extract()[0]  # 评论数
                item['goods_url'] = 'http:' + one_good.xpath('div/div[4]/a/@href').extract()[0]  # 商品链接
                item['shop_url'] = 'http:'+one_good.xpath('div/div[7]/span/a/@href').extract()[0]#店铺链接
                item['shops_id']=self.find_shop_id(item['shop_url'])#店铺ID
                goods_id = one_good.xpath('div/div[2]/div/ul/li[1]/a/img/@data-sku').extract()[0]
                if goods_id:
                    item['goods_id'] = goods_id
                price = one_good.xpath('div/div[3]/strong/i/text()').extract()  # 价格
                if price:  # 有写商品评论数是0，价格也不再源代码里面，应该是暂时上首页的促销商品，每页有三四件，我们忽略掉
                    item['price'] = float(price[0])

                yield item
            except Exception as e:
                pass


    def find_shop_id(self,url):
        pattern = re.compile(r'\d+')
        results = pattern.findall(url)
        return results[0]