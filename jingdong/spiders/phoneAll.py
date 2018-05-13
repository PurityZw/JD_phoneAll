# -*- coding: utf-8 -*-
import scrapy
from jingdong.items import JingdongItem
from scrapy.http.request import Request
from utils.log import logger
from scrapy_redis.spiders import RedisSpider


class PhoneAllSpider(RedisSpider):
    name = 'phoneAll'
    allowed_domains = ['jd.com']

    page = 1
    search_page = 0
    show_items = ''
    base_url = 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&page={}'
    next_url = 'https://search.jd.com/s_new.php?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page={}&s=27&scrolling=y&log_id=1526030906.11309&tpl=3_M&show_items={}'

    redis_key = 'phoneallspider:start_urls'
    # def start_requests(self):
    #     start_url = self.base_url.format(self.page)
    #     yield Request(start_url, callback=self.parse)

    def parse(self, response):
        # 用来存放所有的pid, 拼接ajax时需要使用
        pid_list = []
        i = 1
        phone_list = response.xpath('//li[@data-sku]')
        # 最终页页码
        end_page = response.xpath("//span[@class='p-skip']//b/text()").extract()

        for item in phone_list:
            jd = JingdongItem()
            # 获取item内容

            # PID
            jd['pid'] = item.xpath('./@data-pid').extract_first()
            # 商品图片链接
            jd['image_link'] = self._get_phone_image(item)
            # 价格
            jd['price'] = item.xpath(".//div[@class='p-price']//i/text()").extract_first()
            # 名称
            jd['title'] = item.xpath(".//div[@class='p-name p-name-type-2']//em/text()").extract()
            # 评论数
            jd['comment_num'] = item.xpath(".//div[@class='p-commit']/strong/a/text()").extract_first()
            # 商铺名称(存在店铺为None, 这些商品为广告)
            jd['shop_name'] = item.xpath(".//div[@class='p-shop']/span/a/text()").extract_first()
            # 商铺链接
            jd['shop_link'] = item.xpath(".//div[@class='p-shop']/span/a/@href").extract_first()
            print '*'*30, jd['shop_link']
            # 二手链接(存在返回链接, 否则返回None)
            jd['second_link'] = item.xpath(".//div[@class='p-commit']/a/@href").extract_first()
            # 广告
            jd['ad'] = item.xpath('.//span[@class="p-promo-flag"]/text()').extract_first()

            # 拼接前30pid,用来ajax请求发送
            pid_list.append(jd['pid'])
            self.show_items = ','.join(pid_list)[:-1]
            logger.info(i)
            yield jd
            i += 1

            # 当拼接数为30时, 直接请求当前页剩余30条信息
            if len(pid_list) == 30:
                self.search_page = self.page + 1
                yield scrapy.Request(self.next_url.format(self.search_page, self.show_items),
                                     callback=self.parse_other_info, meta={'end_page': end_page})

    def parse_other_info(self, response):
        # 对查询页数进行判断, 如果是第100页则直接返回
        # end_page = response.meta['end_page']
        end_page = 200
        # print (type(end_page), end_page)
        if end_page == 2 * self.search_page:
            return

        logger.info('page:>>>>>>>>>> page:{}  search_page:{}'.format(self.page, self.search_page))
        self.page = self.search_page + 1
        # 偶数页请求奇数页内容
        if self.search_page % 2 == 0:
            print "-------------"
            yield scrapy.Request(self.base_url.format(str(self.page)), callback=self.parse, dont_filter=True)

    def _get_phone_image(self, li):
        """
        京东商城的图片已加载的图片有 scr 属性,
        未加载的图片地址为 data-lazy-img 属性
        :param li: 为每个li的选择器对象
        :return: image_link
        """
        image_link = li.xpath(".//div[@class='p-img']//img/@src").extract_first()
        if not image_link:
            image_link = li.xpath(".//div[@class='p-img']//img/@data-lazy-img").extract_first()
        return image_link
