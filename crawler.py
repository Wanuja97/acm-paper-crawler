from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os
import re

category='ai'
first_layer = 'Natural language processing'
second_layer = 'Knowledge representation and reasoning'
third_layer = 'Probabilistic reasoning'

def attach_to_csv(item, csv_string):
    if item is not None:
        csv_string += "\"" + item.text.strip() + "\""
    csv_string += ','
    return csv_string
def download_pdf(doi, title):
    file_name = None
    pdf = requests.get('https://dl.acm.org/doi/pdf/' + doi, allow_redirects=True)
    
    if pdf.headers.get('Content-Type').startswith('application/pdf'):
        #file_name = "\"" + title.strip() + '.pdf' + "\""
        print('PDF found in ACM Digital Library')
        file_name = create_pdf_file(title, pdf)
        return file_name
    else:
        print('PDF not found in ACM Digital Library, trying Sci-Hub...')
        sci_hub_page = requests.get('https://sci-hub.se/' + doi)
        soup = BeautifulSoup(sci_hub_page.content, 'html.parser')
        sci_hub_page_title = soup.find('title')
        if sci_hub_page_title.text == 'Sci-Hub: article not found':
            print('PDF not found in Sci-Hub')
            print('----------------------------------------------------')
            return None
        else:
            pdf_link = soup.find('button')
            download_link = pdf_link['onclick'].replace('location.href=\'', '')
            pdf = requests.get('https://sci-hub.se/' + download_link)
            #create_pdf_file(title, pdf)
            file_name = create_pdf_file(title, pdf)
            return file_name

def create_pdf_file(title, pdf):
    directory = 'papers/Probabilistic_reasoning'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Replace special characters with '_' in the title
    file_name = re.sub(r'[\\/*?:"<>|\'‘’]', '_', title.strip()) + '.pdf'
    file_path = os.path.join(directory, file_name)
    
    open(file_path, 'wb').write(pdf.content)
    print('PDF downloaded')
    return file_name

def crawl_dois(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the relevant unordered list
    results_list = soup.find("ul", class_="search-result__xsl-body items-results rlist--inline")

    # Extract DOIs from each list item
    dois = []
    if results_list:
        for item in results_list.find_all("div", class_="issue-item-checkbox-container"):
            label = item.find("label", class_="checkbox--primary")
            if label:
                # Extract DOI from input tag's name attribute
                doi = label.find("input")["name"]
                dois.append(doi)

    return dois
    
# usage
url = input('Enter ACM URL: ')
dois = crawl_dois(url)
timeoutTime = 60
downloadedFiles = 0
paperCount = 0
for doi in dois:
    
    url = 'https://dl.acm.org/doi/' + doi
    page = requests.get(url,timeout=timeoutTime)

    if (page.status_code != 200):
        print('DOI:', doi, 'not found')
        continue
    paperCount +=1
    print("Request No: " + str(paperCount))
    print('Crawling data from ACM Digital Library for DOI:', doi)

    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find('h1', class_='citation__title')
    pdfDownload = str(download_pdf(doi, title.text))

    if(pdfDownload != 'None'):
        csv_string = doi + ','
        
        #date_str looks like this 30 July 2022
        date_str = soup.find('span',class_='CitationCoverDate')
        #Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str.text, "%d %B %Y")
        #Format the datetime object into the 2022-02-30 format 
        publisheddate = date_obj.strftime("%Y-%m-%d")
        
        csv_string += "\"" + str(publisheddate) + "\"" + ',' 
        csv_string = attach_to_csv(title, csv_string)
        csv_string += "\"" + pdfDownload + "\"" + ','
        csv_string += category + ',' + "\"" + first_layer + "\"" + ',' + "\""+ second_layer + "\"" +',' + "\""+ third_layer + "\"" +','

        # Add additional data extraction and CSV writing logic here (similar to your original code)
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if (keywords is not None):
            csv_string += "\"" + keywords['content'].replace(' ', '') + "\""
        csv_string += ','
        abstract = soup.find('div', class_='abstractSection abstractInFull')
        if(abstract == "No abstract available."):
            abstract = "null"
        csv_string = attach_to_csv(abstract, csv_string)
        csv_string = csv_string[:-1]
        
        file = open('papers/Probabilistic_reasoning.csv', 'a', encoding='utf-8')
        file.write(csv_string + '\n')
        file.close()
        downloadedFiles+=1
        print('Data saved to dataset.csv')
        print('----------------------------------------------------')
print("Total Downloads: " + str(downloadedFiles))


