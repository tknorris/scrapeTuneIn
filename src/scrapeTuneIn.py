from bs4 import BeautifulSoup
import urllib
import sys
import re

tunein_base_url="http://tunein.com"
m3u_base_url="http://wunderradio.wunderground.com/support/wunderradio/m3u/m3umaker.m3u?action=m3u&wuiId=rt:"

def get_streams_method1(station_num):
    m3u_url=m3u_base_url+station_num
    
    try:
        file=urllib.urlopen(m3u_url)
        lines=file.readlines()
        file.close()
        return lines
    except IOError as e:
        print "Unable to open url ({0}) - (Error #{1}): {2}".format(m3u_url,e.errno, e.strerror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise    
        
def main():
    try:
        url='file:../data/RDU_radio.html'
        #url="http://tunein.com/search/?id=r100046&so=0"
    
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
                        sys.stderr.write("(Skipping) No call sign for Channel: "+channel_name+"\n")
                        continue
                
                stream_urls=get_streams_method1(station_num)
                if stream_urls is None:
                    sys.stderr.write("(Skipping) No stream URLs for Channel: "+channel_name+"\n")
                    continue
                
                print("  <channel>\n    <name>"+channel_name+"</name>")  
                
                if thumb_url is not None:
                    print("    <thumbnail>"+thumb_url+"</thumbnail>")  

                print("    <items>")
                
                for url in stream_urls:
                    print("      <item>")
                    print("        <title>"+channel_name+"</title>")
                    print("        <link>"+url.rstrip()+"</link>")
                    if thumb_url is not None:
                        print("        <thumbnail>"+thumb_url+"</thumbnail>")
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
        print "Unable to open url ({0}) - (Error #{1}): {2}".format(url,e.errno, e.strerror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise    
    

if __name__ == '__main__':
    main()