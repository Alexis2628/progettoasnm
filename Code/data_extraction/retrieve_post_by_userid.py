import json
import requests
import re


class RetrievePostByUserId:

    def __init__(self, sessionid):
        super().__init__()
        self.sessionid = sessionid
        self.url = "https://www.threads.net/graphql/query"
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

    def retrieve_thread_by_userid(self, userid: str) -> dict:

        data = {
            "_comet_req": "29",
            "lsd": self.api_token,
            "_spin_b": "trunk",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaProfileThreadsTabDirectQuery",
            "variables": json.dumps(
                {
                    "userID": userid,
                    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": False,
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
            "doc_id": "28295274853452500",
        }
        if self.sessionid == "":
            response = requests.post(self.url, headers=self.default_headers, data=data)
            return response.json()

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

    def retrieve_thread_by_userid_after(self, userid: str, after: str) -> dict:

        data = {
            "_comet_req": "29",
            "lsd": self.api_token,
            "_spin_r": "1019765868",
            "_spin_b": "trunk",
            "_spin_t": "1738418567",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaProfileThreadsTabRefetchableDirectQuery",
            "variables": json.dumps(
                {
                    "after": after,
                    "before": None,
                    "first": 100,
                    "last": None,
                    "userID": userid,
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
            "doc_id": "9461898383840322",
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
