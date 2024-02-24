from datetime import datetime
from apify_client import ApifyClient

import bittensor as bt


class ApifyTwitterCrawler:
    def __init__(self, api_key, timeout_secs=60):
        self.client = ApifyClient(api_key)

        self.timeout_secs = timeout_secs

        # microworlds actor id
        # users may use any other actor id that can crawl twitter data
        self.actor_id = "microworlds/twitter-scraper"

    def get_tweets_by_urls(self, urls: list):
        """
        Get tweets by urls.

        Args:
            urls (list): The list of urls to get tweets from.

        Returns:
            list: The list of tweets.
        """
        bt.logging.debug(f"Getting tweets by urls: {urls}")
        params = {
            "maxRequestRetries": 3,
            "searchMode": "live",
            "scrapeTweetReplies": False,
            "urls": urls,
            "maxTweets": len(urls),
        }

        run = self.client.actor(self.actor_id).call(
            run_input=params, timeout_secs=self.timeout_secs
        )
        results = [
            item
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()
        ]

        return results

    def search(self, query: str, max_length: int):
        """
        Searches for the given query on the crawled data.

        Args:
            query (str): The query to search for.
            length (int): The number of results to return.

        Returns:
            list: The list of results.
        """
        bt.logging.debug(f"Crawling for query: '{query}' with length {max_length}")
        params = {
            "maxRequestRetries": 3,
            "searchMode": "live",
            "scrapeTweetReplies": True,
            "searchTerms": [query],
            "maxTweets": max_length,
        }

        run = self.client.actor(self.actor_id).call(
            run_input=params, timeout_secs=self.timeout_secs
        )
        bt.logging.debug(f"Apify Actor Run: {run}")

        results = [
            item
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()
        ]
        bt.logging.trace(f"Apify Results: {results}")

        return results

    def process(self, results):
        """
        Process the results from the search.

        Args:
            results (list): The list of results to process.

        Returns:
            list: The list of processed results.
        """

        time_format = "%a %b %d %H:%M:%S %z %Y"
        results = [
            {
                "id": result["id_str"],
                "url": result["url"],
                "username": result["user"]["screen_name"],
                "text": result.get("full_text"),
                "created_at": datetime.strptime(
                    result.get("created_at"), time_format
                ).isoformat(),
                "quote_count": result.get("quote_count"),
                "reply_count": result.get("reply_count"),
                "retweet_count": result.get("retweet_count"),
                "favorite_count": result.get("favorite_count"),
            }
            for result in results
        ]
        bt.logging.debug(f"Processed results: {results}")
        return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    crawler = ApifyTwitterCrawler(os.environ["APIFY_API_KEY"])

    # r = crawler.search("BTC", 5)
    # print(crawler.process(r))

    r = crawler.get_tweets_by_urls(
        [
            "https://twitter.com/VitalikButerin/status/1759369749887332577",
            "https://twitter.com/elonmusk/status/1760504129485705598",
        ]
    )
    print(crawler.process(r))
