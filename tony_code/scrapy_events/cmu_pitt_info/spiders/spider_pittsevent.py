import scrapy
import re
from scrapy.http import FormRequest

class ScheduleSpider(scrapy.Spider):
    name = 'pitt_events'
    mons = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    #start_urls_prefix = ['https://pittsburgh.events/'] 
    start_urls = []
    for mon in mons:
        start_urls.append(f'https://pittsburgh.events/{mon}/')
    
    # for each month, we record the current page number
    current_page = [1 for _ in mons]
    def parse(self, response):
        print("current_page: ", self.current_page)
        month = response.url.split('/')[-2]
        if response.css('.date-row'):
            # Extract schedule data from the first page
            data = self.parse_schedule(response)
            
            yield from data
            url = response.url.split('?')[0]
            self.current_page[self.mons.index(month)] += 1
            next_page_url = f'{url}?pagenum={self.current_page[self.mons.index(month)]}'
            print("next_page_url: ", next_page_url)
            yield response.follow(next_page_url, callback=self.parse)


    def tag_remover(self, text):
        text = re.sub(r'<a.*?>', '', text)
        # remove all tags
        text = re.sub(r'<.*?>', '', text)
        return text

    def parse_schedule(self, response):
        # Extract each date-row from the response
        for date in response.css('.date-row'):
            # Example of extracting specific data (modify based on site structure)
            venue = date.css('.venue')
            event_name = venue.css('div:first-of-type').get()
            event_name = self.tag_remover(event_name)
            # strip leading/trailing whitespace
            event_name = event_name.strip()
            #venue_link_text = venue.css('a::text').get()
            #event_name = venue_link_text + ' ' + venue_text if venue_link_text else venue_text
            
            date_info = {
                'event_name': event_name,
                'month': date.css('.month::text').get(),
                'day': date.css('.day::text').get(),
                'year': date.css('.year::text').get(),
                'time': date.css('.time::text').get().strip(),
                'venue': self.tag_remover(venue.css('.date-desc').get()).strip(),
                'location': self.tag_remover(venue.css('.location').get()).strip(),
                'starting price': re.findall(r'\d+', date.css('.from-price::text').get())[0],
            }

            # Yield the data for storage
            yield date_info
