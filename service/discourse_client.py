import requests
from utils import _validate_url

class DiscourseClientService():

    def __init__(self, timeout = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def _get_json(self, path):
        response = self.session.get(path, timeout = self.timeout)
        response.raise_for_status()
        return response.json()

    def get_latest_topics(self, url):
        base_url = _validate_url(url)
        get_latest_topics_url = f"{base_url}/latest.json"
        raw_data = self._get_json(get_latest_topics_url)
        return raw_data.get("topic_list", {}).get("topics",[])

    def get_topic_details(self, url, topic_id :int):
        base_url = _validate_url(url)  
        return self._get_json(f"{base_url}/t/{topic_id}.json")
        
