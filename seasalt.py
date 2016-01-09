# Copyright 2016 such-doge

from bs4 import BeautifulSoup
from lxml import etree
from io import BytesIO
import pycurl

############
# SETTINGS #
############
season_name = "Winter 2016"
season_file = '2016_winter.xml'
user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'

mal_buffer = BytesIO()
live_buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.USERAGENT, user_agent)
c.setopt(c.URL, 'http://myanimelist.net/anime/season')
c.setopt(c.WRITEDATA, mal_buffer)
c.perform()
c.setopt(c.URL, 'http://livechart.me/')
# This is insecure but anime isn't a critical application
c.setopt(pycurl.SSL_VERIFYPEER, 0)
c.setopt(pycurl.SSL_VERIFYHOST, 0)
c.setopt(c.FOLLOWLOCATION, True)
c.setopt(c.WRITEDATA, live_buffer)
c.perform()
c.close()

mal_html = mal_buffer.getvalue().decode('utf-8')
live_html = live_buffer.getvalue().decode('utf-8')
malsoup = BeautifulSoup(mal_html, 'html.parser')
livesoup = BeautifulSoup(live_html, 'html.parser')
mal_sections = malsoup.select("div.seasonal-anime-list.js-seasonal-anime-list")
show_types = []
# 0 is not a valid value for type so we'll insert an empty item at the zeroth index.
show_types.append(None)
tv_new = mal_sections[0].find_all("div", class_="seasonal-anime js-seasonal-anime")
tv_old = mal_sections[1].find_all("div", class_="seasonal-anime js-seasonal-anime")
# ONA is appended last to match MAL's type numbering scheme.
show_types.append(tv_new + tv_old)                                                            # TV
show_types.append(mal_sections[3].find_all("div", class_="seasonal-anime js-seasonal-anime")) # OVA
show_types.append(mal_sections[4].find_all("div", class_="seasonal-anime js-seasonal-anime")) # Movie
show_types.append(mal_sections[5].find_all("div", class_="seasonal-anime js-seasonal-anime")) # Special
show_types.append(mal_sections[2].find_all("div", class_="seasonal-anime js-seasonal-anime")) # ONA
#unknown_cat = categories[6]

# Create and initialize the XML tree.
root = etree.Element('season')
print("Created root")
info = etree.SubElement(root, 'info')
print("Created info child")
name_tag = etree.SubElement(info, 'name')
print("Created name child")
name_tag.text = season_name
print("Set name")
modified = etree.SubElement(info, 'modified')
print("Created modified child")
modified.text = '1447533358'
print("Set modified")

#

for show_type in range(1,6):
    for show in show_types[show_type]:
        anime = etree.SubElement(root, 'anime')
        print("Created anime")
        type_tag = etree.SubElement(anime, 'type')
        type_tag.text = str(show_type)
        # Type indicates whether it is tv/ova/etc
        print("Set type to " + str(show_type))
        mal_id = show.select("div.genres.js-genre")[0]['id']
        print("Found mal id " + mal_id)
        mal_id_tag = etree.SubElement(anime, 'id')
        mal_id_tag.set('name', 'myanimelist')
        mal_id_tag.text = mal_id
        print("Set mal id")
        mal_url = "http://myanimelist.net/anime/" + str(mal_id)
        mal_link = livesoup.find_all("a", href=mal_url)
        # Only set the tag if the link exists
        try:
            hummingbird_tag = mal_link[0].parent.parent.find_all("a", class_="hummingbird-icon")
        except IndexError:
            pass
        try:
            # If the link doesn't exist, this will automatically fail and move on
            hummingbird_slug = hummingbird_tag[0]['href'][29:]
            print("Found hb " + hummingbird_slug)
            hummingbird_id_tag = etree.SubElement(anime, 'id')
            hummingbird_id_tag.set('name', 'hummingbird')
            hummingbird_id_tag.text = hummingbird_slug
            print("Set hummingbird")
        except IndexError:
            # Blank Hummingbird ID
            hummingbird_id_tag = etree.SubElement(anime, 'id')
            hummingbird_id_tag.set('name', 'hummingbird')
            hummingbird_id_tag.text = ''
            print("No hummingbird")
        producers = ''
        for subtext in show.find_all("span", class_="producer")[0].contents:
            producers += subtext.string
        # Check if blank
        if producers.replace(' ', '') == '-':
            producers = ''
            print("No producers.")
        else:
            producers = producers.replace('&amp;', '&')
            print("Found producers " + producers)
        producers_tag = etree.SubElement(anime, 'producers')
        producers_tag.text = producers
        print("set producers")
        image = show.find_all("div", class_="image")[0]['style'][21:-2]
        print("Found image " + image)
        image_tag = etree.SubElement(anime, 'image')
        image_tag.text = image
        title = show.find_all("a", class_="link-title")[0].string
        title_tag = etree.SubElement(anime, 'title')
        title_tag.text = title
        print("set title " + title)

#Write XML file
xmlfile = open(season_file, mode='wb')
xmldoc = etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)
xmlfile.write(xmldoc)
xmlfile.close()

