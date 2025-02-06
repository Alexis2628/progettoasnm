import json
import requests
import re


class RetrieveDataByQuery:

    def __init__(self, sessionid):
        super().__init__()
        self.url = "https://www.threads.net/graphql/query"
        self.sessionid = sessionid
        self.headers_for_html_fetching = {
            "Authority": "www.threads.net",
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                "q=0.8,application/signed-exchange;v=b3;q=0.7"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.threads.net",
            "Pragma": "no-cache",
            "Referer": "https://www.instagram.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"
            ),
        }
        self.api_token = self._generate_api_token()
        self.default_headers = {
            "Authority": "www.threads.net",
            "Accept": "*/*",
            "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.threads.net",
            "Pragma": "no-cache",
            "Sec-Fetch-Site": "same-origin",
            "X-ASBD-ID": "129477",
            "X-FB-LSD": self.api_token,
            "X-IG-App-ID": "238260118697367",
        }

    def _generate_api_token(self) -> str:
        """
        Generate a token for the Threads.

        The token, called `lsd` internally, is required for any request.
        For anonymous users, it is just generated automatically from the back-end and passed to the front-end.

        Returns:
            The token for the Threads as a string.
        """
        response = requests.get(
            url="https://www.instagram.com/instagram",
            headers=self.headers_for_html_fetching,
        )

        token_key_value = re.search(
            'LSD",\\[\\],{"token":"(.*?)"},\\d+\\]', response.text
        ).group()
        token_key_value = token_key_value.replace('LSD",[],{"token":"', "")
        token = token_key_value.split('"')[0]

        return token

    def retrieve_thread_by_query(self, query: str) -> dict:

        data = {
            "_comet_req": "29",
            "lsd": self.api_token,
            "_spin_r": "101964087",
            "_spin_b": "trunk",
            "_spin_t": "1738088890",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaSearchResultsQuery",
            "variables": json.dumps(
                {
                    "meta_place_id": None,
                    "pinned_ids": None,
                    "power_search_info": None,
                    "query": query,
                    "recent": 0,
                    "search_surface": "default",
                    "tagID": None,
                    "trend_fbid": None,
                    "__relay_internal__pv__BarcelonaHasSERPHeaderrelayprovider": False,
                    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
                    "__relay_internal__pv__BarcelonaShareableListsrelayprovider": True,
                    "__relay_internal__pv__BarcelonaIsSearchDiscoveryEnabledrelayprovider": False,
                    "__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider": True,
                    "__relay_internal__pv__BarcelonaQuotedPostUFIEnabledrelayprovider": False,
                    "__relay_internal__pv__BarcelonaIsCrawlerrelayprovider": False,
                    "__relay_internal__pv__BarcelonaHasDisplayNamesrelayprovider": False,
                    "__relay_internal__pv__BarcelonaCanSeeSponsoredContentrelayprovider": False,
                    "__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider": False,
                    "__relay_internal__pv__BarcelonaIsInternalUserrelayprovider": False,
                }
            ),
            "server_timestamps": "true",
            "doc_id": "9592290460783575",
        }
        cookies = {
            # "sessionid": "65955050144%3ARAdn9XAbejZtkT%3A18%3AAYfUVsLYHT3qqek503Ujj_V51BvBPSsxR3MtaSAndQ",
            "sessionid": self.sessionid,
            # "sessionid": "65955050144%3AS1xuKkl6W1kKqB%3A23%3AAYcjBamMFOs7TY1uYVsrP-gAou7-TriJJsp8l1NgLA",
            # "sessionid": "71441509544%3AbPWmQfLc5vQhzF%3A7%3AAYfgsFzvtyS88WCjLlPNxUHfxAyfSs-PMk0cunbBMA"
            # "sessionid":"1653774166%3A9uDdOCkxtjfjYr%3A25%3AAYf2jGK4vIx5W_dkE5m8a7PpoN4LA2D5CxUpR4C7BA"
        }
        response = requests.post(
            self.url, headers=self.default_headers, data=data, cookies=cookies
        )
        return response.json()

    def retrieve_thread_by_query_after(self, query: str, after: str) -> dict:

        data = {
            "_comet_req": "29",
            "lsd": self.api_token,
            "_spin_r": "101964087",
            "_spin_b": "trunk",
            "_spin_t": "1738088890",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaSearchResultsRefetchableQuery",
            "variables": json.dumps(
                {
                    "after": after,
                    "before": None,
                    "first": 100,
                    "has_serp_header": False,
                    "last": None,
                    "meta_place_id": None,
                    "pinned_ids": None,
                    "power_search_info": None,
                    "query": query,
                    "recent": 0,
                    "search_surface": "default",
                    "tagID": None,
                    "trend_fbid": None,
                    "__relay_internal__pv__BarcelonaHasSERPHeaderrelayprovider": False,
                    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
                    "__relay_internal__pv__BarcelonaShareableListsrelayprovider": True,
                    "__relay_internal__pv__BarcelonaIsSearchDiscoveryEnabledrelayprovider": False,
                    "__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider": True,
                    "__relay_internal__pv__BarcelonaQuotedPostUFIEnabledrelayprovider": False,
                    "__relay_internal__pv__BarcelonaIsCrawlerrelayprovider": False,
                    "__relay_internal__pv__BarcelonaHasDisplayNamesrelayprovider": False,
                    "__relay_internal__pv__BarcelonaCanSeeSponsoredContentrelayprovider": False,
                    "__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider": False,
                    "__relay_internal__pv__BarcelonaIsInternalUserrelayprovider": False,
                }
            ),
            "server_timestamps": "true",
            "doc_id": "9041360669265964",
        }
        cookies = {
            "sessionid": self.sessionid,
        }
        response = requests.post(
            self.url, headers=self.default_headers, data=data, cookies=cookies
        )
        return response.json()

    def retrieve_follower_by_userid(self, userid: str) -> dict:

        data = {
            "_comet_req": "29",
            "lsd": self.api_token,
            "_spin_r": "101964087",
            "_spin_b": "trunk",
            "_spin_t": "1738088890",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaFriendshipsFollowersTabQuery",
            "variables": json.dumps(
                {
                    "first": 25,
                    "userID": userid,
                    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
                    "__relay_internal__pv__BarcelonaIsCrawlerrelayprovider": False,
                    "__relay_internal__pv__BarcelonaHasDisplayNamesrelayprovider": False,
                    "__relay_internal__pv__BarcelonaShouldShowFediverseListsrelayprovider": False,
                }
            ),
            "server_timestamps": "true",
            "doc_id": "9523819394337000",
        }
        cookies = 'cb=1_1970_01_01_2-3; mid=Z6O-5AALAAFwri_hZd_yj-u2-2EC; ig_did=6A6269B0-9F68-4E7C-9CEA-53AD0784C3B1; dpr=1; csrftoken=UgpugvagTtbii6zdkqFUduvZ1EVh1ezX; ds_user_id=65955050144; sessionid=65955050144%3A6hS26w11VRkHbU%3A24%3AAYeTigtAMpGXCp8sOwNzqCe29YQYygcEAfegg7eTjg'
        # {
        #     "sessionid": self.sessionid,
        # }
        
        response = requests.post(
            self.url, headers=self.default_headers, data=data, cookies=cookies
        )
        return response.json()

    def retrieve_follower_by_userid_after(self, userid: str, after: str) -> dict:
        data = {
            "_comet_req": "29",
            "lsd": self.api_token,
            "_spin_r": "101964087",
            "_spin_b": "trunk",
            "_spin_t": "1738088890",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaFriendshipsFollowersTabRefetchableQuery",
            "variables": json.dumps(
                {
                    "after": after,
                    "first": 25,
                    "id": userid,
                    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
                    "__relay_internal__pv__BarcelonaIsCrawlerrelayprovider": True,
                    "__relay_internal__pv__BarcelonaHasDisplayNamesrelayprovider": False,
                }
            ),
            "server_timestamps": "true",
            "doc_id": "9226067564176291",
        }
        cookies ={
            "sessionid": self.sessionid,
        }
        response = requests.post(
            self.url, headers=self.default_headers, data=data, cookies=cookies
        )
        return response.json()
