import requests
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re

page_urls = ['https://www.imdb.com/title/tt7631058/reviews?sort=totalVotes&dir=desc&ratingFilter=0',
				'https://www.imdb.com/title/tt6443346/reviews?sort=totalVotes&dir=desc&ratingFilter=0',
				'https://www.imdb.com/title/tt12593682/reviews?sort=totalVotes&dir=desc&ratingFilter=0',
				'https://www.imdb.com/title/tt9253284/reviews?sort=totalVotes&dir=desc&ratingFilter=0',
				'https://www.imdb.com/title/tt0107688/reviews?sort=totalVotes&dir=desc&ratingFilter=0']

def getReviews(page_urls, driver, num_reviews):
	
	reviews = []
	for url in page_urls:
		driver.get(url)
		sleep(2)
		
		for _ in range(num_reviews//25 - 1):
			driver.find_element(By.CSS_SELECTOR, 'div.load-more-data').click()
			sleep(2)
		
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		show_title = soup.select('h3[itemprop=name] a')[0].get_text().strip()

		lister = soup.select('div.lister-list div.imdb-user-review')

		pattern = re.compile(r'(.+) out of (.+) found this helpful.')
			
		for rev in lister:
			title, reviewer, rating, date, review, helpful, votes = (None,)*7

			if rev_title := rev.select('a.title'):
				title = rev_title[0].get_text().strip()

			if rev_reviewer := rev.select('span.display-name-link a'):
				reviewer = rev_reviewer[0].get_text().strip()

			if len(rev_rating := rev.select('span.rating-other-user-rating span')) == 2:
				rating = rev_rating[0].get_text().strip()

			if rev_date := rev.select('span.review-date'):
				date = rev_date[0].get_text().strip()

			if rev_review := rev.select('div.text'):
				review = rev_review[0].get_text().strip()

			if rev_helpful := rev.select('div.actions'):
				m = re.fullmatch(pattern, rev_helpful[0].find(text=True).strip())
				helpful, votes = int(m.group(1).replace(',', '')), int(m.group(2).replace(',', ''))

			reviews.append((title, reviewer, rating, date, review, helpful, votes, show_title))

		df = pd.DataFrame(reviews, columns=['title', 'reviewer', 'rating', 'date', 'review',
			'helpful', 'total_votes', 'show_title'])

	return df
	

driver = webdriver.Safari()
reviews = getReviews(page_urls, driver, 400)
driver.quit()

reviews.to_csv('data.csv', index=False)
	