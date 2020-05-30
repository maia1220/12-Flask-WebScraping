from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd




def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():

    # create surf_data dict that we can insert into mongo
    mars_data = {} 

    # Element 1: NASA Mars News
    url="https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    response= requests.get(url)
    soup=bs(response.text, 'html.parser')
    result=soup.find('div', class_='image_and_description_container')
    news_p=result.find('div', class_='rollover_description_inner').text.replace('\n','')
    news_title=soup.find('div', class_='content_title').text.replace('\n', '')
    
    # Add data to mars data with a key of p and title
    mars_data["p"] = news_p
    mars_data["title"] = news_title

    # Start with splinter
    browser = init_browser()

    # Element 2: JPL Mars Space Images - Featured Image
    url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    html=browser.html
    soup=bs(html, 'html.parser')
    items=soup.find('div', class_='carousel_container')

    image=items.find('a')
    image_link=image['data-fancybox-href']
    website='https://www.jpl.nasa.gov'
    featured_image_url = website + image_link
    
    # add the feature image url to mars data with a key of src
    mars_data["src"] = featured_image_url

    browser.quit()

    # Element 3: Mars Weather
    url2 = (
        "https://twitter.com/marswxreport?lang=en"
    )
    response2= requests.get(url2)
    soup2=bs(response2.text, 'html.parser')
    result2=soup2.find_all('div', class_='js-tweet-text-container')
    weather_list=[]

    for result in result2:
        post= result.find('p', class_='js-tweet-text').text
        if 'InSight sol' in post:        
            post1=post.split('InSight')[1]
            weather=post1.split('pic.twitter')[0]
            weather_list.append(weather)
        else:
            pass
    mars_weather=weather_list[0].lstrip()
    mars_weather=mars_weather.replace('sol', 'Sol')

    # Add the mars weather to mars data with a key of weather
    mars_data['weather'] = mars_weather

    # Element 4: Mars Facts
    url3='https://space-facts.com/mars/'
    tables=pd.read_html(url3)
    mar_df=tables[0]
    mar_df.columns=['Fact', 'Metric']
    mar_df.set_index('Fact', inplace=True)
    html_table=mar_df.to_html()
    html_tabledata=html_table.replace('\n', '').replace('"', '')

     # Add the mars facts as a html table to mars data with a key of table
    mars_data['table']=html_tabledata


    # Element 5: Mars Hemispheres Images Urls
    # Start with splinter
    browser = init_browser()

    url4='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url4)
    html4=browser.html
    soup4=bs(html4,'html.parser')
    views=soup4.find_all('div', class_='description')

    # Finding the image urls for all 4 views

    title_list=[]
    url_list=[]

    for view in views:
        title=view.find('h3').text
        title1=title.replace('Enhanced', '')
        title_list.append(title1)
        try:
            browser = init_browser()
            browser.visit(url4)
            # browser.click_link_by_partial_text(title)
            browser.links.find_by_partial_text(title).first.click()
            html5=browser.html
            soup5=bs(html5, 'html.parser')
            images=soup5.find_all('div', class_='wide-image-wrapper')
            for image in images:
                image_url= image.find('li').find('a')['href']
                url_list.append(image_url)
            browser.quit()      
        except:
            print('Error')

    hemisphere_image_urls = [
    {'title': title_list[0], 'image_url': url_list[0]},
    {'title': title_list[1], 'image_url': url_list[1]},
    {'title': title_list[2], 'image_url': url_list[2]},
    {'title': title_list[3], 'image_url': url_list[3]}]

    # Add the mars hemisphere image urls dict list to mars data with a key of hemi_urls

    mars_data['hemi_urls']=hemisphere_image_urls


    # return our surf data dict
    browser.quit()
    
    
    return mars_data





