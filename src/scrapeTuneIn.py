from bs4 import BeautifulSoup
import urllib
import sys

tunein_base_url="http://tunein.com"

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
                 
                print("  <channel>\n    <name>"+channel_name+"</name>")  
                
                # Channel Thumbnail
                thumb_url=None
                thumb_tag=result.find('img','logo')
                if thumb_tag is not None:
                    thumb_url=thumb_tag['src']
                else:
                    sys.stderr.write("No logo for Channel: "+channel_name+"\n")
                
                if thumb_url is not None:
                    print("    <thumbnail>"+thumb_url+"</thumbnail>")  
                
                print("    <items>\n      <item>")
                print("        <title>"+channel_name+"</title>")
                
                # Generate Streams
                print("        <link>blah</link>")
                print("        <link>blah2</link>")
                
                # Close Channel Definition
                print("    </items>\n  </channel>")
            
            break
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