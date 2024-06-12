from selenium import webdriver
import time
import pandas as pd
import os

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


#This code below opens a chrome window in the referenced url
# Setting WebDriver with Options. These reduce the chances of getting detected by the anti-bot LinkedIn's systems. 
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless for less detection (remove this if you want to see the browser)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")

# Add a random user-agent. Every time we launch Chrome, it will use a random fake user out of those 5. There is more  efficient ways of doing this. But this was enough. 
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
]
chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

service = Service(executable_path=r'D:\\DATA\\Projects\\Linkedin-Jobs-Scrapping\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)


#The url we want to open. Later in the process we will make this url dynamic. 
url1 = 'https://www.linkedin.com/jobs/search/?keywords=Data&location=Spain&geoId=105646813&f_TPR=&f_E=1&position=1'
driver.get(url1) #open the job search page
driver.implicitly_wait(10) #for safety, wait 10 segs to give time to load completely 

# Scroll down and load all jobs. 
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait for new jobs to load

    try:
        # Click the "See more jobs" button if it exists
        see_more_button = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/button')
        see_more_button.click()
        time.sleep(2)  # wait for jobs to load after clicking the button
    except:
        pass

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# In the same way, we had to find a dynamic way to set the range in which to loop our function. 
# Let's find how many job cards there are loaded.
job_list = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list')
job_cards = job_list.find_elements(By.TAG_NAME, 'li')

len(job_cards)

#Let's initiate some lists
CompanyName = []
JobTitle= []
place = []
posted_date = []
urlPost = []
# Let's iterate through all the cards to extract some data: 
j = 0
for job_card in job_cards:
    try:
        company = job_card.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text
        title = job_card.find_element(By.CLASS_NAME, 'base-search-card__title').text
        location = job_card.find_element(By.CLASS_NAME, 'job-search-card__location').text
        date = job_card.find_element(By.XPATH, './/time[contains(@class, "job-search-card__listdate")]').get_attribute('datetime')
        linkPost = job_card.find_element(By.CLASS_NAME, 'base-card__full-link').get_attribute('href')
        
        CompanyName.append(company)
        JobTitle.append(title)
        place.append(location)
        urlPost.append(linkPost)
        posted_date.append(date)
        
        j = j+1
        print('Jobs extracted: ', j,linkPost)

    except Exception as e:
        print(f"Error extracting data from a job card: {e}")
        pass

# Print extracted data
data = {
    'Company Name': CompanyName,
    'Job Title': JobTitle,
    'location': place,
    'Job URL': urlPost,
    'Date' : posted_date
}
jobs_df = pd.DataFrame(data)

#Now, we need to use our list of url to access them one by one and fetch the job description, and some other info
# Initialize lists to store the extracted data
applicants = []
experience = []
typeEmploy = []
description = []
sector = []


j=1

for link in jobs_df['Job URL']:
    driver.get(link)  # open the job page
    time.sleep(random.uniform(2, 3))  # wait for the page to load completely with a random delay

    try:
        # Click the "See more jobs" button if it exists
        show_more_button = driver.find_element(By.CLASS_NAME, 'show-more-less-html__button')
        show_more_button.click()
        time.sleep(random.uniform(2, 4))  # wait for the additional content to load with a random delay
    except:
        pass

    try:
        num_applicants = driver.find_element(By.CLASS_NAME, 'num-applicants__caption').text.replace(' applicants', '').strip()
    except:
        num_applicants = 'N/A'
        
    try:
        experience_level = driver.find_element(By.XPATH, './/ul[contains(@class, "description__job-criteria-list")]/li[1]/span').text
    except:
        experience_level = 'N/A'
    
    try:
        employment_type = driver.find_element(By.XPATH, './/ul[contains(@class, "description__job-criteria-list")]/li[2]/span').text
    except:
        employment_type = 'N/A'
    
    try:
        sector_type = driver.find_element(By.XPATH, './/ul[contains(@class, "description__job-criteria-list")]/li[4]/span').text
    except:
        sector_type = 'N/A'
    
    try:
        desc = driver.find_element(By.CLASS_NAME, 'description__text').text
    except:
        desc = 'N/A'

    applicants.append(num_applicants)
    experience.append(experience_level)
    typeEmploy.append(employment_type)
    sector.append(sector_type)
    description.append(desc)

    print(j, ": ", desc[:15])
    j = j+1

    # Random sleep to mimic human behavior
    time.sleep(random.uniform(1, 3))

# Close the WebDriver
driver.quit()

# Create a DataFrame from the lists
data_plus = {
    'Company Name': jobs_df['Company Name'],
    'Job Title': jobs_df['Job Title'],
    'location': jobs_df['location'],
    'Job URL': jobs_df['Job URL'],
    'Date': jobs_df['Date'],
    'Applicants': applicants,
    'Experience': experience,
    'Employment Type': typeEmploy,
    'Sector': sector,
    'Description': description
}
detailed_jobs_df = pd.DataFrame(data_plus)

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'

detailed_jobs_df['language'] = detailed_jobs_df['Description'].apply(detect_language)

detailed_jobs_df['language'].value_counts()

#deep_translator was the only free and working library. It had to inconvenient of having a max 5k characters translation, but I built a simple method to Circumvent that issue. 
from deep_translator import GoogleTranslator 

# Initialize Google Translator
translator = GoogleTranslator(source='auto', target='en')
c = 1
def translate_to_english(text, lang):
    max_chunk_size = 4900
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    translated_chunks = []
    
    
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            raise ValueError(f"Chunk length {len(chunk)} exceeds the maximum limit of {max_chunk_size} characters.")
        if lang != 'en':
            translated_chunk = translator.translate(chunk)
            print(f'Description {c} translated')
        else:
            translated_chunk = chunk
            print(f'Description {c} in English')
        translated_chunks.append(translated_chunk)
    c += 1

    # Join the translated chunks back together
    translated_text = ''.join(translated_chunks)
    
    return translated_text

detailed_jobs_df['Description_en'] = detailed_jobs_df.apply(lambda row: translate_to_english(row['Description'], row['language']), axis=1)

#Extracting keywords
import spacy
from spacy.tokens import Doc
from spacy.matcher import PhraseMatcher

# Initialize spaCy model
nlp = spacy.load("en_core_web_md")

# List of key skills
with open("DataSkills.txt", 'r') as file:
    skills = file.readlines()
key_skills = [skill.strip() for skill in skills]
key_skills_set = set([skill.lower() for skill in key_skills])

# Register custom extension attributes
Doc.set_extension("key_skills", default=[], force=True)

# Initialize PhraseMatcher with the shared vocabulary
matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(skill) for skill in key_skills]
matcher.add("KEY_SKILLS", patterns)

# Define the custom component for keyword extraction
@spacy.Language.component("key_skill_extractor")
def key_skill_extractor(doc):
    matches = matcher(doc)
    matched_skills = [doc[start:end].text.lower() for match_id, start, end in matches]
    doc._.key_skills = list(set(matched_skills))
    return doc

# Add the custom component to the pipeline
nlp.add_pipe("key_skill_extractor", last=True)

# Modified extract_keywords function to include translation
def extract_keywords(description):
    doc = nlp(description)
    return doc._.key_skills

detailed_jobs_df['keywords'] = detailed_jobs_df['Description_en'].apply(extract_keywords)

#exploding the jobs dataframe
keywords_df = detailed_jobs_df.explode('keywords').rename(columns={'keywords':'keyword'})

import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

keywords_df['keyword'] = keywords_df['keyword'].astype(str)
flat_df = keywords_df.dropna(subset=['keyword'])

keyword_counts = Counter(keywords_df['keyword'])
# Ensure all keywords are strings and drop NaN values

cmap = LinearSegmentedColormap.from_list("mycmap", ["#FF5733", "#33FF57"])

wordcloud = WordCloud(width=800, height=400, background_color='white', colormap=cmap).generate_from_frequencies(keyword_counts)
# Plot the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()