"""Google Maps scraper module for Lead Scraper project."""
from typing import Dict, List, Optional
import argparse
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import setup_logger
from utils.decorators import retry_with_backoff
from utils.web import setup_chrome_driver

# Initialize logger
logger = setup_logger(__name__)

# Selector constants for easy testing override
SEARCH_BOX = 'input#searchboxinput'
SEARCH_BUTTON = 'button#searchbox-searchbutton'
RESULT_LIST = 'div[role="feed"], div.section-result-content'
RESULT_ITEMS = 'div.Nv2PK, a[href^="https://www.google.com/maps/place"], div.bfdHYd'
TITLE_IN_LIST = 'div.qBF1Pd, span.fontHeadlineSmall'
RATING_IN_LIST = 'span.MW4etd, span[aria-label*="rating"]'
ADDRESS_IN_LIST = 'div.W4Efsd:last-child, span[jstcache*="address"]'
SCROLL_PANE = 'div[role="feed"], div.section-scrollbox'
MODAL_CLOSE_BTN = 'button[aria-label="Close"], button[jsaction*="modal.close"]'

# User agent list for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def random_sleep(min_seconds=1, max_seconds=3):
    """Sleep for a random amount of time within range."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def wait_and_find_element(driver, selector: str, timeout: int = 10, retry_on_stale=True):
    """Wait for and return an element with stale element handling."""
    max_retries = 3 if retry_on_stale else 1
    
    for attempt in range(max_retries):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            # Try to ensure element is ready for interaction
            WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            return element
        except StaleElementReferenceException:
            if attempt == max_retries - 1:
                logger.warning(f"Element went stale after {max_retries} attempts: {selector}")
                return None
            random_sleep(0.5, 1.5)
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return None

def wait_and_find_elements(driver, selector: str, timeout: int = 10):
    """Wait for and return multiple elements."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return driver.find_elements(By.CSS_SELECTOR, selector)
    except TimeoutException:
        logger.warning(f"Timeout waiting for elements: {selector}")
        return []

def safe_click(driver, element, retries: int = 3, js_click_fallback=True):
    """
    Safely click an element with retries and JavaScript fallback.
    
    Args:
        driver: Selenium WebDriver instance
        element: WebElement or CSS selector string
        retries: Number of attempts
        js_click_fallback: Whether to try JavaScript click as fallback
    
    Returns:
        bool: True if clicked successfully
    """
    for i in range(retries):
        try:
            if isinstance(element, str):
                element = wait_and_find_element(driver, element)
            
            if not element:
                return False
                
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            random_sleep(0.5, 1.5)  # Let the page settle
            
            # Try regular click
            element.click()
            return True
            
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            logger.warning(f"Click attempt {i+1} failed: {str(e)}")
            
            # Check for and close any modals that might be in the way
            try:
                modal_close = driver.find_element(By.CSS_SELECTOR, MODAL_CLOSE_BTN)
                modal_close.click()
                random_sleep(1, 2)
            except NoSuchElementException:
                pass
            
            # Try JavaScript click on last attempt or if fallback is enabled
            if js_click_fallback and i >= retries - 2:
                try:
                    driver.execute_script("arguments[0].click();", element)
                    return True
                except WebDriverException as js_e:
                    logger.warning(f"JavaScript click failed: {str(js_e)}")
                    
            random_sleep(1, 2)  # Wait before retry
            
        except StaleElementReferenceException:
            if i == retries - 1:
                logger.warning(f"Element went stale after {retries} attempts")
                return False
            random_sleep(1, 1.5)
        
        except Exception as e:
            logger.error(f"Click error: {str(e)}")
            if i == retries - 1:
                return False
            random_sleep(1, 2)
            
    return False

def wait_for_results(driver, timeout: int = 20) -> bool:
    """Wait for and verify that results are loaded."""
    try:
        # Wait for either the feed container or older-style results
        scroll_pane_present = False
        for selector in [SCROLL_PANE, 'div.section-result']:
            try:
                WebDriverWait(driver, timeout/2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                scroll_pane_present = True
                break
            except TimeoutException:
                continue
                
        if not scroll_pane_present:
            logger.warning("Could not find results container")
            return False
            
        # Wait for actual results to appear
        result_present = False
        for selector in [RESULT_ITEMS, RESULT_LIST + ' > *', 'div.section-result']:
            try:
                WebDriverWait(driver, timeout/2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                result_present = True
                break
            except TimeoutException:
                continue
                
        if not result_present:
            logger.warning("No results found in container")
            return False
            
        # Additional check for "No results found" message
        try:
            no_results = driver.find_element(By.CSS_SELECTOR, 'div[role="status"]')
            if "No results found" in no_results.text:
                logger.warning("'No results found' message displayed")
                return False
        except NoSuchElementException:
            pass
        
        return True
        
    except Exception as e:
        logger.error(f"Error waiting for results: {str(e)}")
        return False

def get_results(driver) -> List:
    """Get all result elements, handling different possible layouts."""
    results = []
    
    # Try different possible selectors for results, from most specific to most general
    selectors = [
        RESULT_ITEMS,
        RESULT_LIST + ' > *', 
        'div.section-result',
        'a[href^="https://www.google.com/maps/place"]'
    ]
    
    for selector in selectors:
        try:
            results = driver.find_elements(By.CSS_SELECTOR, selector)
            if results:
                logger.info(f"Found {len(results)} results with selector: {selector}")
                return results
        except Exception as e:
            logger.debug(f"Error finding results with selector {selector}: {str(e)}")
    
    return []

def extract_info_from_result(result, driver) -> Dict:
    """Extract business information directly from the result element without clicking."""
    lead = {
        "business_name": "",
        "phone": "",
        "website": "",
        "address": "",
        "rating": "",
        "notes": ""
    }
    
    # Try to get all information with stale element protection
    for attempt in range(3):  # Try up to 3 times if the element goes stale
        try:
            # Try to extract business name
            try:
                for selector in [TITLE_IN_LIST, 'div.qBF1Pd', 'span.fontHeadlineSmall', 'div.fontHeadlineSmall', 'h3']:
                    try:
                        name_elem = result.find_element(By.CSS_SELECTOR, selector)
                        if name_elem and name_elem.text.strip():
                            lead["business_name"] = name_elem.text.strip()
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
            except Exception:
                pass
            
            # Try to extract address
            try:
                for selector in [ADDRESS_IN_LIST, 'div.W4Efsd:last-child', 'span[jstcache*="address"]', 'div[aria-label*="Address"]']:
                    try:
                        address_elem = result.find_element(By.CSS_SELECTOR, selector)
                        if address_elem and address_elem.text.strip():
                            lead["address"] = address_elem.text.strip()
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
            except Exception:
                pass
            
            # Try to extract rating
            try:
                for selector in [RATING_IN_LIST, 'span.MW4etd', 'span[aria-label*="rating"]', 'span[aria-label*="stars"]']:
                    try:
                        rating_elem = result.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_elem.text.strip() or rating_elem.get_attribute("aria-label")
                        if rating_text:
                            # Try to extract the numeric rating using regex
                            rating_match = re.search(r'(\d+(\.\d+)?)(?:\s*stars?)?', rating_text)
                            if rating_match:
                                rating_value = rating_match.group(1)
                                # Try to find review count nearby
                                try:
                                    # Try multiple selectors for review count
                                    for review_selector in ['span.UY7F9', 'span[aria-label*="review"]']:
                                        try:
                                            reviews_elem = result.find_element(By.CSS_SELECTOR, review_selector)
                                            reviews_count = reviews_elem.text.strip()
                                            if reviews_count:
                                                lead["rating"] = f"{rating_value} stars {reviews_count}"
                                                break
                                        except (NoSuchElementException, StaleElementReferenceException):
                                            continue
                                    # If no review count was found, just use stars
                                    if not lead["rating"]:
                                        lead["rating"] = f"{rating_value} stars"
                                except Exception:
                                    lead["rating"] = f"{rating_value} stars"
                            else:
                                lead["rating"] = rating_text
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
            except Exception:
                pass
            
            # Extract the place URL for potential deep linking later
            try:
                for selector in ['a', 'a[href*="maps/place"]', 'a[data-item-id*="place"]']:
                    try:
                        anchor_elem = result.find_element(By.CSS_SELECTOR, selector)
                        place_url = anchor_elem.get_attribute('href')
                        if place_url and 'maps/place' in place_url:
                            lead["notes"] = f"Google Maps URL: {place_url}"
                            
                            # Sometimes websites are directly shown in the listing
                            if not lead.get("website") and 'website' not in place_url:
                                # Check if we can find a website link directly in the result
                                try:
                                    website_link = result.find_element(By.CSS_SELECTOR, 'a[href^="http"]:not([href*="google"])')
                                    lead["website"] = website_link.get_attribute('href')
                                except:
                                    pass
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
            except Exception:
                pass
            
            # If we got here without a StaleElementReferenceException, break out of retry loop
            break
            
        except StaleElementReferenceException:
            if attempt < 2:  # If this is not the last attempt
                logger.warning(f"Element went stale during extraction, retrying... (attempt {attempt + 1})")
                random_sleep(0.5, 1.0)
            else:
                logger.warning("Element went stale during extraction, giving up")
                
    return lead

def scroll_results_pane(driver, wait_time=3):
    """Scroll the results pane to load more results."""
    for attempt in range(3):
        try:
            # Try multiple possible scroll container selectors
            for scroll_selector in [SCROLL_PANE, 'div[role="feed"]', 'div.section-scrollbox', '.section-layout']:
                try:
                    scroll_pane = wait_and_find_element(driver, scroll_selector, timeout=5)
                    if scroll_pane:
                        # Get current scroll position and total height
                        current_height = driver.execute_script("return arguments[0].scrollTop", scroll_pane)
                        scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
                        client_height = driver.execute_script("return arguments[0].clientHeight", scroll_pane)
                        
                        # If we're already at the bottom, no need to scroll further
                        if current_height + client_height >= scroll_height:
                            logger.info("Already at the bottom of the scroll pane")
                            return False
                        
                        # Scroll down incrementally for smoother loading
                        target_height = current_height + min(500, client_height)
                        
                        # Smooth scroll with JavaScript
                        driver.execute_script(
                            "arguments[0].scrollTo({top: arguments[1], behavior: 'smooth'});", 
                            scroll_pane, 
                            target_height
                        )
                        
                        logger.info(f"Scrolled down results pane from {current_height} to {target_height}")
                        
                        # Wait for new results to load with progressive waiting
                        for i in range(3):
                            time.sleep(wait_time / 3)
                            # Check if new content has loaded by comparing heights
                            new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
                            if new_scroll_height > scroll_height:
                                logger.info(f"New content loaded, scroll height increased from {scroll_height} to {new_scroll_height}")
                                return True
                        
                        # Even if height didn't change, consider it successful since we scrolled
                        return True
                except (StaleElementReferenceException, NoSuchElementException) as e:
                    if attempt == 2:  # Last attempt
                        logger.debug(f"Scroll container not found with selector {scroll_selector}: {str(e)}")
                    continue
            
            # If we get here, none of the selectors worked - fallback to body scroll
            try:
                logger.info("Falling back to body scroll")
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(wait_time)
                return True
            except Exception as body_e:
                logger.debug(f"Body scroll fallback failed: {body_e}")
                
        except StaleElementReferenceException:
            if attempt < 2:
                logger.warning(f"Scroll pane went stale, retrying... (attempt {attempt + 1})")
                time.sleep(1)
            else:
                logger.warning("Scroll pane went stale after multiple attempts")
        except Exception as e:
            logger.error(f"Failed to scroll results pane: {e}")
            if attempt < 2:
                time.sleep(1)
            
    return False

# New generic extractor function
def generic_parse_details(driver) -> Dict:
    """
    After clicking a listing and waiting for its details pane to load,
    this function will scrape:
      • business_name
      • rating (if present)
      • EVERY element carrying a `data-item-id` attribute
    It returns a dict mapping item_ids → their text or href (if link).
    """
    data = {}

    # 1. Business name (always inside the <h1> span)
    try:
        name_el = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf span, h1.DUwDvf.lfPIob span, h1.fontHeadlineLarge')
        data['business_name'] = name_el.text.strip()
    except NoSuchElementException:
        # Try alternate selectors for business name
        try:
            name_el = driver.find_element(By.CSS_SELECTOR, 'h1, h1.fontHeadlineLarge, h2.fontHeadlineLarge, div.fontHeadlineLarge')
            data['business_name'] = name_el.text.strip()
        except NoSuchElementException:
            data['business_name'] = ''
            logger.warning("Could not find business name")

    # 2. Rating (if present)
    try:
        rating_el = driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"]')
        data['rating'] = rating_el.text.strip()
        
        # Try to get review count if available
        try:
            reviews_el = driver.find_element(By.CSS_SELECTOR, 'span.UY7F9, button.fontTitleSmall span')
            reviews_count = reviews_el.text.strip()
            if reviews_count:
                data['rating'] = f"{data['rating']} stars ({reviews_count})"
        except NoSuchElementException:
            pass
            
    except NoSuchElementException:
        data['rating'] = ''

    # 3. All data-item-id entries
    elems = driver.find_elements(By.CSS_SELECTOR, '[data-item-id]')
    for el in elems:
        item_id = el.get_attribute('data-item-id')  # e.g. "address", "phone:tel:09823...", "authority"
        key = item_id

        # Try to pull an href if it's a link
        if el.tag_name.lower() == 'a':
            href = el.get_attribute('href')
            data[key] = href.strip() if href else el.text.strip()
        else:
            # Many are buttons; their visible value often lives in a child <div class="Io6YTe">
            try:
                val = el.find_element(By.CSS_SELECTOR, 'div.Io6YTe').text.strip()
            except NoSuchElementException:
                # fallback to the element's own text
                val = el.text.strip()
            data[key] = val

    logger.info(f"Extracted data using generic parser: {data}")
    return data

def normalize_lead_data(lead: Dict) -> Dict:
    """
    Normalize the keys in the raw data dictionary into standardized lead format.
    
    Args:
        lead: Raw data dictionary with data-item-id keys
        
    Returns:
        Normalized lead dictionary with standard keys
    """
    normalized = {
        'business_name': lead.get('business_name', ''),
        'rating': lead.get('rating', '')
    }
    
    # Extract phone
    phone_keys = [k for k in lead if k.startswith('phone:tel')]
    if phone_keys:
        normalized['phone'] = lead.get(phone_keys[0], '')
    else:
        normalized['phone'] = ''
        
    # Extract address
    normalized['address'] = lead.get('address', '')
    
    # Extract website
    normalized['website'] = lead.get('authority', '')
    
    # Add any additional information as notes
    other_info = []
    for k, v in lead.items():
        if k not in ['business_name', 'rating', 'address'] and not k.startswith('phone:tel') and k != 'authority':
            if v:  # Only include non-empty values
                other_info.append(f"{k}: {v}")
    
    notes = "; ".join(other_info)
    if 'notes' in lead and lead['notes']:
        if notes:
            notes = f"{lead['notes']}; {notes}"
        else:
            notes = lead['notes']
            
    normalized['notes'] = notes
    
    return normalized

def extract_data_from_side_panel(driver) -> Dict:
    """Extract detailed business information from the side panel."""
    # Use the generic parser for extraction
    raw_data = generic_parse_details(driver)
    
    # Normalize the data into our lead format
    lead = normalize_lead_data(raw_data)
    
    logger.info(f"Extracted detailed lead information: {lead}")
    return lead

def is_duplicate_lead(leads, new_lead):
    """
    Check if a lead is a duplicate of an existing lead based on business name and address.
    
    Args:
        leads: List of existing leads
        new_lead: New lead to check
    
    Returns:
        True if the lead is a duplicate, False otherwise
    """
    # If we don't have enough info to compare, treat as not duplicate
    if not new_lead.get('business_name') and not new_lead.get('address'):
        return False
    
    for lead in leads:
        # If both business names exist and match
        if (new_lead.get('business_name') and lead.get('business_name') and 
            new_lead['business_name'].lower() == lead['business_name'].lower()):
            return True
        
        # If both addresses exist and match substantially (allow for minor differences)
        if (new_lead.get('address') and lead.get('address') and
            # Check if at least 70% of the words match between addresses
            len(set(new_lead['address'].lower().split()) & 
                set(lead['address'].lower().split())) / 
            max(len(new_lead['address'].split()), len(lead['address'].split())) > 0.7):
            return True
            
        # If phone numbers match
        if (new_lead.get('phone') and lead.get('phone') and
            ''.join(filter(str.isdigit, new_lead['phone'])) == 
            ''.join(filter(str.isdigit, lead['phone']))):
            return True
    
    return False

@retry_with_backoff
def scrape(
    keyword: str,
    location: str,
    max_results: int = 15,
    on_lead_callback = None
) -> List[Dict[str, str]]:
    leads: List[Dict[str, str]] = []
    driver = None
    processed_urls = set()
    backoff_time = 1
    consecutive_scroll_failures = 0
    max_scroll_failures = 3

    try:
        # Initialize Chrome with a visible window for better interaction
        driver = setup_chrome_driver(headless=False)
        driver.set_window_size(1920, 1080)
        
        # Navigate to Google Maps and wait for it to load
        logger.info(f"Navigating to Google Maps to search for {keyword} in {location}")
        driver.get("https://www.google.com/maps")
        random_sleep(3, 5)  # Increased initial wait time
        
        # Handle cookie consent if present
        try:
            cookie_buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
            for button in cookie_buttons:
                button_text = button.text.lower()
                if any(text in button_text for text in ['accept', 'agree', 'consent']):
                    try:
                        button.click()
                        random_sleep(1, 2)
                        break
                    except Exception as click_err:
                        logger.debug(f"Could not click consent button: {click_err}")
        except Exception as e:
            logger.debug(f"Cookie handling error: {str(e)}")

        # Wait for and find search box with retry
        search_box = None
        for attempt in range(3):
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_BOX))
                )
                break
            except Exception as e:
                logger.warning(f"Search box not found on attempt {attempt + 1}: {str(e)}")
                if attempt < 2:
                    random_sleep(2, 3)
                    driver.refresh()

        if not search_box:
            raise Exception("Could not find search box after multiple attempts")

        # Clear and fill search box
        search_box.clear()
        random_sleep(0.5, 1)
        search_box.send_keys(f"{keyword} in {location}")
        random_sleep(1, 2)

        # Try clicking search button first
        search_clicked = False
        try:
            search_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_BUTTON))
            )
            if search_button:
                search_button.click()
                search_clicked = True
                logger.info("Clicked search button")
        except Exception as e:
            logger.debug(f"Could not click search button: {str(e)}")

        # If button click failed, use Enter key
        if not search_clicked:
            search_box.send_keys(Keys.RETURN)
            logger.info("Used Enter key for search")

        # Wait longer for initial results with multiple checks
        random_sleep(3, 5)
        results_found = False
        for attempt in range(3):
            if wait_for_results(driver, timeout=10):
                results_found = True
                break
            else:
                logger.warning(f"Results not found on attempt {attempt + 1}, retrying...")
                random_sleep(2, 3)
                # Try refreshing if results don't load
                if attempt < 2:
                    driver.refresh()
                    random_sleep(2, 3)

        if not results_found:
            logger.warning("No results found after multiple attempts")
            return leads

        # Main scraping loop - continue until we have enough leads or can't find more
        while len(leads) < max_results and consecutive_scroll_failures < max_scroll_failures:
            logger.info(f"Current leads: {len(leads)}/{max_results}")
            
            # Get current results
            results = get_results(driver)
            if not results:
                consecutive_scroll_failures += 1
                logger.warning(f"No results found. Failures: {consecutive_scroll_failures}/{max_scroll_failures}")
                continue

            # Process each result in the current view
            for idx, result in enumerate(results):
                try:
                    # Check for duplicate URLs
                    place_url = None
                    try:
                        anchor_elems = result.find_elements(By.CSS_SELECTOR, 'a[href*="maps/place"]')
                        if anchor_elems:
                            place_url = anchor_elems[0].get_attribute('href')
                    except Exception as e:
                        logger.debug(f"Error getting URL: {str(e)}")

                    if place_url and place_url in processed_urls:
                        continue
                    if place_url:
                        processed_urls.add(place_url)

                    # Extract initial data from listing
                    lead = extract_info_from_result(result, driver)
                    
                    # Get detailed info by clicking if this is every 3rd result
                    if idx % 3 == 0:
                        if safe_click(driver, result):
                            random_sleep(2, 3)
                            detailed_lead = extract_data_from_side_panel(driver)
                            
                            # Merge data, preferring detailed info
                            for key, value in detailed_lead.items():
                                if value:
                                    lead[key] = value
                            
                            # Return to results list
                            try:
                                back_button = wait_and_find_element(driver, 'button[jsaction*="back"]')
                                if back_button and safe_click(driver, back_button):
                                    random_sleep(1, 2)
                                else:
                                    driver.execute_script("window.history.go(-1)")
                                    random_sleep(2, 3)
                            except Exception:
                                driver.execute_script("window.history.go(-1)")
                                random_sleep(2, 3)

                    # Only add lead if it has useful information and isn't a duplicate
                    if (lead.get("business_name") or lead.get("phone") or 
                        lead.get("website") or lead.get("address")):
                        if not is_duplicate_lead(leads, lead):
                            leads.append(lead)
                            logger.info(f"Added lead #{len(leads)}: {lead.get('business_name') or 'Unnamed business'}")
                            
                            # Call callback if provided
                            if on_lead_callback:
                                try:
                                    on_lead_callback(lead)
                                except Exception as cb_err:
                                    logger.error(f"Callback error: {cb_err}")
                            
                            # Only check max_results after successfully adding a lead
                            if len(leads) >= max_results:
                                logger.info(f"Reached target of {max_results} leads")
                                return leads[:max_results]

                except Exception as result_err:
                    logger.error(f"Error processing result: {result_err}")
                    continue

            # Scroll for more results if we haven't reached our target
            if len(leads) < max_results:
                if scroll_results_pane(driver, wait_time=backoff_time):
                    consecutive_scroll_failures = 0
                    random_sleep(backoff_time, backoff_time + 1)
                    backoff_time = min(backoff_time * 1.5, 5)
                else:
                    consecutive_scroll_failures += 1
                    logger.warning(f"Scroll failed. Failures: {consecutive_scroll_failures}/{max_scroll_failures}")

    except Exception as e:
        logger.error(f"Fatal error during scraping: {str(e)}", exc_info=True)
    finally:
        if driver:
            driver.quit()

    # Return exactly max_results leads if we have them
    return leads[:max_results]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Google Maps for business leads")
    parser.add_argument("keyword", help="Type of business to search for")
    parser.add_argument("location", help="Location to search in")
    parser.add_argument("--max_results", type=int, default=15, help="Maximum number of results to return")
    args = parser.parse_args()
    
    def print_lead(lead):
        print(f"\n{lead.get('business_name', 'Unnamed business')}")
        print(f"   Phone: {lead.get('phone', 'N/A')}")
        print(f"   Website: {lead.get('website', 'N/A')}")
        print(f"   Address: {lead.get('address', 'N/A')}")
        print(f"   Rating: {lead.get('rating', 'N/A')}")
    
    results = scrape(args.keyword, args.location, max_results=args.max_results, on_lead_callback=print_lead)
    print(f"\nFound {len(results)} results")