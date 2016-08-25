#coding:utf8
import scrapy
import json
import logging
import re
from baike.items import baikeItem


logger = logging.getLogger(__name__)

class baikeSpider(scrapy.Spider):
    name = "baike"
    allowed_domains = ["baike.baidu.com"]
##    start_urls = [
##        "http://baike.baidu.com/renwu"
##    ]

    def start_requests(self):
        payload = {"contentLength":"40",
                    "fromLemma":"false",
                    "limit":"24",
                    "page":"1",
                    "tagId":"68031",
                    "timeout":"3000",
                    }
        return [scrapy.http.FormRequest(url="http://baike.baidu.com/wikitag/api/getlemmas",
                    formdata=payload,
                    callback=self.post_after, dont_filter=True)]

    def post_after(self, response):
        data = json.loads(response.text)
        totalPage = data["totalPage"]
        payloads = [{"contentLength":"40",
            "fromLemma":"false",
            "limit":"24",
            "page":str(page),
            "tagId":"68031",
            "timeout":"3000"} for page in range(1,totalPage + 1)]
        logger.info("totalPage:" + str(totalPage))
        yield [scrapy.http.FormRequest(url="http://baike.baidu.com/wikitag/api/getlemmas",
                    formdata=payload,
                    callback=self.parse, dont_filter=True) for payload in payloads]


    def parse(self, response):
        data = json.loads(response.text)
        logger.info("total page: %d; crawl page: %d;  "%(data["totalPage"],data["page"]))
        for info in data["lemmaList"]:
            url = info["lemmaUrl"]
            logger.info(info["lemmaTitle"] + ":\t" + url)
            if re.findall("http://baike.baidu.com/.*?view/\d+.*?", url):
                yield scrapy.Request(url, callback=self.parse_content)

    def parse_content(self, response):
        item = baikeItem()
        item["url"] = response.url
        # 名称
        if response.css("h1::text").extract_first():
            item["name"] = response.css("h1::text").extract_first()
            if response.css(".lemmaWgt-lemmaTitle-title h2::text"):
                item["subname"] = response.css(".lemmaWgt-lemmaTitle-title h2::text").extract_first()
            # 结构化信息
            info_name = [string.strip() for string in self.iter_extract(response,".name") if string.strip()]
            info_value = [string.strip() for string in self.iter_extract(response,".value") if string.strip()]
            item["info"] = dict(zip(info_name, info_value))
            # 简介
            if response.css(".lemma-summary .para::text").extract():
                item["abstract"] = "\n".join(self.iter_extract(response,".lemma-summary .para"))
            # 全文
            item["content"] = "\n".join(self.iter_extract(response,".para"))
            # 概念,前一句或两句
            sentences = item["content"].split(u"。")
            if sentences >= 4:
                item["concept"] = sentences[:2]
            else:
                item["concept"] = sentences[0]
#            # 相关术语
#            relation_name = response.css(".link-inner::text").extract()
#            relation_url = [response.urljoin(url) for url in response.css(".link-inner::attr(href)").extract()]
#            relation = dict(zip(relation_name, relation_url))
#            item["relation"] = {key:relation[key] for key in relation if re.findall("http://baike.baidu.com/.*?view/\d+.*?", relation[key])}
#            logger.debug(item["relation"].keys())
#            # 百度推荐
#            recommend_name = response.css("#zhixinWrap a::text").extract()
#            recommend_url = [response.urljoin(url) for url in response.css(".link-inner::attr(href)").extract()]
#            recommend = dict(zip(recommend_name, recommend_url))
#            item["recommend"] = {key:recommend[key] for key in recommend if re.findall("http://baike.baidu.com/.*?view/\d+.*?", recommend[key])}
#            logger.debug(item["recommend"].keys())
            # 内容解释包含的外链和词汇
            outlink_name = response.css(".para a::text").extract()
            outlink_url = [response.urljoin(url) for url in response.css(".para a::attr(href)").extract()]
            weak_relation = dict(zip(outlink_name, outlink_url))
            item["relation"] = {key:weak_relation[key] for key in weak_relation if re.findall("http://baike.baidu.com/.*?view/\d+.*?", weak_relation[key])}
            logger.debug(item["relation"].keys())
            # 标签
            item["tag"] = [string.strip() for string in self.iter_extract(response, ".taglist") if string.strip()]
            # 参考文献链接
            item["reference"] = response.css(".reference-item .text::attr(href)").extract()
            # 外链
            urls = item["relation"].values()
            for url in urls:
                yield scrapy.Request(url, callback=self.parse_content)
            yield item

    def iter_extract(self, response, css):
        # 循环迭代解析,不需要::text和extract（）
        return ["".join(element.root.itertext()) for element in response.css(css)]

    def test(self, response):
        from scrapy.shell import inspect_response
        inspect_response(response, self)
