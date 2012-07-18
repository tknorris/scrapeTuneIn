from bs4 import BeautifulSoup
import urllib
import sys
import re

tunein_base_url="http://tunein.com"
m3u_base_url="http://wunderradio.wunderground.com/support/wunderradio/m3u/m3umaker.m3u?action=m3u&wuiId=rt:"
restricted_base_url="http://www.surfmusic.de/media/"

def get_tunein_streams(station_num):
    m3u_url=m3u_base_url+station_num
    return get_streams(m3u_url)

def get_restricted_streams(call_sign):
    if len(call_sign)==4:
        # Try FM band first
        restricted_url=restricted_base_url+call_sign.lower()+'-fm.m3u'
        streams=get_streams(restricted_url)

        # If an html page was returned, then no streams were found
        if streams[0].find('<html>')>=0:
            # Then try AM band if the band was unspecified
            restricted_url=restricted_base_url+call_sign.lower()+'-am.m3u'
            streams=get_streams(restricted_url)
    else:
        restricted_url=restricted_base_url+call_sign.lower()+'.m3u'
        streams=get_streams(restricted_url)

    # If an html page was returned, then no streams were found
    if streams[0].find('<html>')>=0:
        streams=None
    
    return streams

def get_streams(url):
    #sys.stderr.write("Pulling Streams from URL: "+url+"\n")
    
    try:
        handle=urllib.urlopen(url)
        lines=handle.readlines()
        handle.close()
        return lines
    except IOError as e:
        sys.stderr.write("Unable to open url ({0}) - (Error #{1}): {2}".format(url,e.errno, e.strerror))
    except:
        sys.stderr.write("Unexpected error:", sys.exc_info()[0])
        raise    
        
            
def main():
    try:
        url='file:../data/RDU_radio.html'
    
        soup = BeautifulSoup(urllib.urlopen(url))
        print('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<channels>')
    
        while True:    
            # Build XML from page
            results=soup.find_all('tr','result')
            
            for result in results:
                
                # Channel Name
                channel_name = "Unknown"
                name_tag=result.find('td','show')
                if name_tag is not None:
                    channel_name=name_tag.h3.a.string
                    channel_name=channel_name.replace("&","&amp")
                else:
                    sys.stderr.write('Unable to locate Channel Name: \n'+str(result.prettify())+'\n')
                
                # Channel Thumbnail
                thumb_url=None
                thumb_tag=result.find('img','logo')
                if thumb_tag is not None:
                    thumb_url=thumb_tag['src']
                else:
                    sys.stderr.write("No logo for Channel: "+channel_name+"\n")
                
                # Get Station TuneIn ID
                play_link=result.find('a',attrs=['play','play_ext'])
                if play_link is not None:
                    play_href=play_link['href']
                    match=re.compile('\((\d+),').search(play_href)
                    if match:
                        station_num=match.group(1)
                    else:
                        sys.stderr.write("(Skipping) No Station Num for channel: "+channel_name+"\n")
                        continue
                else:
                    sys.stderr.write("(Skipping) No play link for Channel: "+channel_name+"\n")
                    continue
                
                # Get station call sign
                match=re.compile('\(((W|K)[A-Z]{3}(-(FM|AM))*)\)').search(channel_name)
                if match:
                    call_sign=match.group(1)
                else:
                    match=re.compile('(W|K)[A-Z]{3}(-(FM|AM))*').search(channel_name)
                    if match:
                        call_sign=match.group(0)
                    else:
                        sys.stderr.write("No call sign for Channel: "+channel_name+"\n")
                
                stream_urls=get_tunein_streams(station_num)
                if stream_urls[0].find("restricted")>=0 and call_sign is not None:
                    stream_urls=None
                    stream_urls=get_restricted_streams(call_sign)
                    
                if stream_urls is None:
                    sys.stderr.write("(Skipping) No stream URLs for Channel: "+channel_name+"\n")
                    continue
                
                print("  <channel>\n    <name>"+channel_name+"</name>")  
                
                if thumb_url is not None:
                    print("    <thumbnail>"+thumb_url+"</thumbnail>")  

                print("    <items>")
                print("      <item>")
                print("        <title>"+channel_name+"</title>")
                if thumb_url is not None:
                    print("        <thumbnail>"+thumb_url+"</thumbnail>")

                for url in stream_urls:
                    print("        <link>"+url.rstrip()+"</link>")

                print("      </item>")
                print("    </items>\n  </channel>")
            
            # Get the next search result page URL
            next_tag=soup.find('a',id='A2')

            # If there is no A2 tag, then this is the last result
            if next_tag is None:
                break
            
            next_url = next_tag['onclick']
            next_url = next_url.replace("location.href='","",1)
            next_url = next_url.rstrip("'")
            next_url = tunein_base_url+next_url
            sys.stderr.write("Next Url:"+next_url+"\n")

            soup = BeautifulSoup(urllib.urlopen(next_url))
        
        print("</channels>")

    except IOError as e:
        sys.stderr.write("Unable to open url ({0}) - (Error #{1}): {2}".format(url,e.errno, e.strerror))
    except:
        sys.stderr.write("Unexpected error:", sys.exc_info()[0])
        raise    
    

if __name__ == '__main__':
    main()