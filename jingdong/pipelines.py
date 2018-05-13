# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
import pickle
import re
import os
import gevent
from gevent import monkey
from scrapy.exporters import CsvItemExporter
from scrapy.exceptions import DropItem
gevent.monkey.patch_all()


# from jingdong.log import logger


class JingdongPipeline(object):
    def open_spider(self, spider):
        self.f = open('jd_phone.csv', 'w')
        # 创建csv读写对象
        self.csv_exporter = CsvItemExporter(self.f)
        self.csv_exporter.start_exporting()


    def process_item(self, item, spider):
        image_name = re.search(r'\w+\.(jp(e)?g|png)', item['image_link']).group()
        image_data = requests.get('https:' + item['image_link'])
        # 保存图片至文件夹
        get_img = gevent.spawn(self.save_image_in_dir, image_name, image_data)
        get_img.join()
        print ('*******item*******', image_name)

        # 删除广告信息
        if item['ad']:
            raise DropItem(item)

        # item数据处理
        comment = item['comment_num']
        if comment.encode('utf-8').find('万') != -1:
            num = comment[:-2]
            item['comment_num'] = str(float(num) * 10000)[:-2]
        elif comment.encode('utf-8').find('+') != -1:
            item['comment_num'] = comment[:-1]

        item['image'] = image_name
        item['title'] = ''.join(item['title'])
        item['image_link'] = 'https:' + item['image_link']

        if item['second_link']:
            item['second_link'] = 'https' + item['second_link']

        self.csv_exporter.export_item(item)

        return item

    def close_spider(self, spider):
        self.csv_exporter.finish_exporting()
        self.f.close()

    def save_image_in_dir(self, image_name, image_data):
        """
        保存图片文件至./images/中
        :param image_name:
        :param image_data:
        :return:
        """
        # 创建文件
        if 'images' not in os.listdir('./'):
            os.makedirs('./images')
        with open('./images/' + image_name, 'wb') as f:
            f.write(image_data.content)
