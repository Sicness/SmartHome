import json
import urllib2
import cosm_config

class Cosm:

    def __init__(self, feed_id, api_key):
        self.feed_id = feed_id
        self.api_key = api_key
        self.api_url = "http://api.cosm.com/v2/feeds/%s" % (self.feed_id)
        self.headers = {"X-PachubeApiKey" : self.api_key}

    def put_data_point(self, name, value):
    
        dataPoint = {"id" : name, "current_value" : value}
        envelope = {"version" : "1.0.0", "datastreams" : [dataPoint]}
        body = json.dumps(envelope)
        
        self.send_request(self.api_url, "PUT", body, self.headers)
    
    def delete_data_point(self, feed, datastream, date):
    
        url = self.url + "/datastreams/" + datastream + "/datapoints/" + date
        print url
        
        self.send_request(url, "DELETE", "", self.headers)
        
    def send_request(self, url, method="GET", body="", headers={}):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, body, headers)
        request.get_method = lambda: method
        url = opener.open(request)
        url.close()    

if __name__ == "__main__":

    cosm = Cosm(cosm_config.FEED_ID, cosm_config.API_KEY)
    cosm.put_data_point("test", 79)
    
    pass

	#logPachube("test", 79)
	#cosmdelete_data_point(42813, "Upstairs", "2011-12-28T02:16:37.817106Z");
	#delete_data_point(42813, "Upstairs", "2011-12-28T02:18:19.370535Z");
