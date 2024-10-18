import scrapy
import re
from scrapy.http import FormRequest
from ..items import EventItem
import logging
from scrapy.utils.log import configure_logging

class PdpSpider(scrapy.Spider):
    name = 'pdp'
    mons = ['10', '11', '12']
    # configure logging
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    # scrap 2024 oct~dec, 2025 jan
    #start_urls_prefix = ['https://pittsburgh.events/'] 
    start_urls = ['https://downtownpittsburgh.com/events/?n=1&y=2025&cat=0', # JAN 2025
                  'https://downtownpittsburgh.com/events/?n=10&y=2024&cat=0',
                  'https://downtownpittsburgh.com/events/?n=11&y=2024&cat=0',
                  'https://downtownpittsburgh.com/events/?n=12&y=2024&cat=0']
    
    def parse(self, response):
        data = self.parse_schedule(response)
        yield from data
 


    def tag_remover(self, text):
        text = re.sub(r'<a.*?>', '', text)
        # remove all tags
        text = re.sub(r'<.*?>', '', text)
        return text
    
    def split_date_and_time(self, text):

        # Regular expression pattern to match the date and time format
        pattern1 = r"(\w+ \d+, \d+) - (\w+ \d+, \d+)\s*\|\s* (\d+:\d+ \w+ - \d+:\d+ \w+)"
        pattern2 = r"(\w+ \d+, \d+)\s+\|\s* (\d+:\d+ \w+ - \d+:\d+ \w+)"
        pattern3 = r"(\w+ \d+, \d+) - (\w+ \d+, \d+)"
        
        # Find the match in the text using pattern1
        match = re.search(pattern1, text)
        if match:
            # Extract the date and time components
            date_str, time_str = match.groups()

            # Split the date string
            month, day, year = date_str
            day = day.replace(',', '')  

            # Split the time string
            start_time, end_time = time_str.split(' - ')
            start_month, start_day, start_year = month, day, year
            end_month, end_day, end_year = month, day, year
            print("match pattern1")
            return start_month, start_day, start_year, end_month, end_day, end_year, start_time, end_time
        match = re.search(pattern2, text)
        if match:
            # Extract the date and time components
            date_str, time_str = match.groups()
            # Split the date string
            month, day, year = date_str.split()
            day = day.replace(',', '')
            # Split the time string
            start_time, end_time = time_str.split(' - ')
            
            start_month, start_day, start_year = month, day, year
            end_month, end_day, end_year = month, day, year
            print("match pattern2")
            return start_month, start_day, start_year, end_month, end_day, end_year, start_time, end_time


        # Find the match in the text using pattern3
        match = re.search(pattern3, text)
        if match:

            # Extract the date components
            start_date_str, end_date_str = match.groups()
            # Split the start date string
            start_month, start_day, start_year = start_date_str.split()
            # Split the end date string
            end_month, end_day, end_year = end_date_str.split()
            start_day = start_day.replace(',', '')
            end_day = end_day.replace(',', '')
            # Set the start time and end time to None
            start_time = None
            end_time = None
            print("match pattern3")
            return start_month, start_day, start_year, end_month, end_day, end_year, start_time, end_time
        
        print("Date and time format not found in the text.")
        return None
    def parse_schedule(self, response):
        # Extract each date-row from the response
        for item in response.css('.eventitem'):
            category = None
            event_name = None
            date_time = None
            start_time = None
            end_time = None
            if item.css('.term'):    
                category = self.tag_remover(item.css('.term').get()).strip()

            if item.css('.copyContent h1'):
                event_name = self.tag_remover(item.css('.copyContent h1').get()).strip()
            if item.css('.eventdate'):
                date_time = self.tag_remover(item.css('.eventdate').get()).strip()

            try:
                start_month, start_day, start_year, end_month, end_day, end_year, start_time, end_time = self.split_date_and_time(date_time)
            except:
                print("Error parsing date and time for event: ", event_name)
                print("date_time: ", date_time)
                continue
                

            content = self.tag_remover(''.join(item.css('.copyContent::text').getall())).strip()
            id = item.css('.eventitem::attr(id)')
            id = re.findall(r'\d+', id.get())[0]
            url = "https://downtownpittsburgh.com/events/event/?id=" + id
            revenue, location = None, None
            # save data to EventItem
            item = EventItem()
            item['id'] = id
            item['category'] = category
            item['event_name'] = event_name
            item['start_month'] = start_month
            item['start_day'] = start_day
            item['start_year'] = start_year
            item['end_month'] = end_month
            item['end_day'] = end_day
            item['end_year'] = end_year
            item['start_time'] = start_time
            item['end_time'] = end_time
            item['content'] = content


            yield scrapy.Request(url, callback=self.parse_event, meta={'item': item})
    def parse_event(self, response):
        revenue = None
        location = None
        if response.css('.eventlocation'):
            location = ", ".join(response.css('.eventlocation::text').getall()[1:]).strip().replace("\t", "")
            revenue = response.css('.eventlocation strong::text').get().strip() 

        item = response.meta['item']
        item['location'] = location
        item['revenue'] = revenue

        yield item