import calendar
import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def getXpath(browser,tweet):
    # use JavaScript execute the code getting XPath
    xpath = browser.execute_script("""
        function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            };
            while (element) {
                comp = comps[comps.length] = {};
                switch (element.nodeType) {
                    case Node.TEXT_NODE:
                        comp.name = 'text()';
                        break;
                    case Node.ATTRIBUTE_NODE:
                        comp.name = '@' + element.nodeName;
                        break;
                    default:
                        comp.name = element.nodeName;
                }
                comp.position = getPos(element);
                element = element.parentNode;
            }
            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name;
                if (comp.position !== null) {
                    xpath += '[' + comp.position + ']';
                }
            }
            return xpath;
        }
        return absoluteXPath(arguments[0]);
    """, tweet)
    return xpath

def splitTime(sinceTime,untilTime):
    #split untilTime-sinceTime by month
    dates = []
    for year in range(sinceTime.year, untilTime.year + 1):
        for month in range(1, 13):
            first_day = datetime.datetime(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            dates.append(first_day)
            dates.append(datetime.datetime(year, month, last_day))
    s = dates[0::2]
    e = dates[1::2]
    sinceList = [str(date).split()[0] for date in s]
    untilList = [str(date).split()[0] for date in e]
    return sinceList,untilList

def scrap(browser,advSearchComand):
    key='[data-testid="tweetText"]'#locating the tweets
    wait = WebDriverWait(browser, 10)
    browser.get(advSearchComand)
    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, key)))
    collect=[]
    tweets = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, key)))
    while tweets:
        for tweet in tweets:
            if len(getXpath(browser,tweet))>=210:#过滤被转发微博，被转发微博xpath更长
                continue
            collect.append(tweet.text)
        browser.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'start' });", tweet)#跳转到最后一条贴文
        time.sleep(5)
        tempTweets = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, key)))
        tweets=tempTweets[tempTweets.index(tweet)+1:]
    return collect