from bs4 import BeautifulSoup
import requests

def crawl_dois(url):
  """
  Crawls the given ACM page URL and retrieves DOIs from search results.

  Args:
      url (str): The URL of the ACM page to crawl.

  Returns:
      list: A list of DOIs found on the page.
  """
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

# Example usage
url = "https://dl.acm.org/action/doSearch?ConceptID=2034&target=ccs-topics&startPage=0&pageSize=50"  # Replace with your desired ACM search query
dois = crawl_dois(url)
print("Count: " + str(len(dois)))
if dois:
  print("Found DOIs:")
  for doi in dois:
    print(doi)
else:
  print("No DOIs found on this page.")
