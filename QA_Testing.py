import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Function to check if the website is reachable
def check_website_status(url):
    response = requests.get(url)
    if response.status_code == 200:
        print(f"[INFO] Website {url} is reachable.")
    else:
        print(f"[ERROR] Website {url} returned status code {response.status_code}.")

# Function to check page load time
def check_page_load_time(url):
    start_time = time.time()
    response = requests.get(url)
    load_time = time.time() - start_time
    print(f"[INFO] Page load time for {url} is {load_time:.2f} seconds.")
    
# Function to check basic SEO tags
def check_seo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    title_tag = soup.find("title")
    meta_description = soup.find("meta", attrs={"name": "description"})
    
    print(f"[INFO] SEO Check for {url}:")
    if title_tag:
        print(f"Title: {title_tag.text}")
    else:
        print("[WARNING] No title tag found.")
    
    if meta_description:
        print(f"Meta Description: {meta_description.get('content')}")
    else:
        print("[WARNING] No meta description found.")
        
# Function to check accessibility using Selenium for dynamic elements
def check_accessibility(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    
    # Wait until the page is fully loaded
    time.sleep(5)
    
    # Check for WCAG violations (this can be enhanced using specific accessibility tools like axe-core)
    try:
        # Sample check: if any image is missing alt attribute
        images = driver.find_elements(By.TAG_NAME, 'img')
        for img in images:
            if not img.get_attribute("alt"):
                print(f"[WARNING] Image with src {img.get_attribute('src')} has no alt text.")
            else:
                print(f"[INFO] Image with src {img.get_attribute('src')} has alt text.")
    except Exception as e:
        print(f"[ERROR] Error during accessibility check: {e}")
    finally:
        driver.quit()

# Function to run Lighthouse for performance metrics (Requires Node.js and Lighthouse installation)
def run_lighthouse(url):
    print("[INFO] Running Lighthouse audit...")
    # You can execute the lighthouse audit command using subprocess if you have Lighthouse installed via Node.js.
    # Example (you can modify this part based on your OS and Lighthouse setup):
    command = f"lighthouse {url} --output html --output-path ./lighthouse-report.html"
    # Run the command and save the output to a file
    import os
    os.system(command)
    print(f"[INFO] Lighthouse report saved to ./lighthouse-report.html")

if __name__ == "__main__":
    website_url = "https://www.tiaapa.info"

    print(f"Starting QA checks for {website_url}...\n")

    # Check website status
    check_website_status(website_url)
    
    # Check page load time
    check_page_load_time(website_url)
    
    # Check basic SEO
    check_seo(website_url)
    
    # Check accessibility
    check_accessibility(website_url)
    
    # Run performance analysis using Lighthouse
    run_lighthouse(website_url)

    print("\nQA checks completed.")
