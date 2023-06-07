# import json
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from twitter_api_connect import waitUntilReset


def connect_to_endpoint(bearer_token, user_id, next_token=None):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/users/{}/tweets/".format(user_id)

    # replace appropriate start and end times below
    if next_token is not None:
        params = {
            "tweet.fields": "author_id,created_at,public_metrics,organic_metrics,promoted_metrics",
            "expansions": "referenced_tweets.id.author_id",
            "user.fields": "description,created_at,public_metrics",
            "max_results": "100",
            "pagination_token": str(next_token),
        }

    else:
        params = {
            "tweet.fields": "author_id,created_at,public_metrics",
            "expansions": "referenced_tweets.id.author_id",
            "user.fields": "description,created_at,public_metrics",
            "max_results": "100",
        }

    response = requests.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response, response.json()


# Bearer token
BT = ""

# {username: id}
ID_LIST = {}

t_delta = timedelta(hours=9)
JST = timezone(t_delta, "JST")
now = datetime.now(JST)


count = 0
json_response = ""

for user_, id_ in ID_LIST.items():

    flag = True
    json_count = 0

    while flag:
        if json_count == 0:
            response_, json_response = connect_to_endpoint(BT, id_)

            print("+++++", user_, "+++++")
            print("+++++", user_, "+++++")
            print("+++++", user_, "+++++")
            print("--------------------------------")
            print(
                "x-rate-limit-remaining",
                response_.headers["x-rate-limit-remaining"],
            )
            print("x-rate-limit-reset", response_.headers["x-rate-limit-reset"])
            print("--------------------------------")

            time.sleep(3)

            df = pd.json_normalize(json_response["includes"]["tweets"])
            df_re = df.reindex(
                columns=[
                    "id",
                    "text",
                    "author_id",
                    "public_metrics.retweet_count",
                    "public_metrics.reply_count",
                    "public_metrics.like_count",
                    "public_metrics.quote_count",
                    "public_metrics.bookmark_count",
                    "public_metrics.impression_count",
                    "created_at",
                ]
            )
            df_re.to_csv(
                "BuzzTweetData_{}.csv".format(
                    now.strftime("%Y-%m-%d")
                ),
                encoding="utf-8-sig",
                mode="a",
                index=False,
            )

            df2 = pd.json_normalize(json_response["includes"]["users"])
            df_reindex2 = df2.reindex(
                columns=[
                    "username",
                    "name",
                    "id",
                    "created_at",
                    "description",
                    "public_metrics.followers_count",
                    "public_metrics.following_count",
                    "public_metrics.tweet_count",
                    "public_metrics.listed_count",
                ]
            )
            df_reindex2.to_csv(
                "BuzzUserData_{}.csv".format(
                    now.strftime("%Y-%m-%d")
                ),
                encoding="utf-8-sig",
                mode="a",
                index=False,
            )

            json_count += 1

            if int(response_.headers["x-rate-limit-remaining"]) == 0:
                waitUntilReset(response_.headers["x-ratelimit-reset"])

        try:
            result_count = json_response["meta"]["result_count"]

        except Exception:
            result_count = None
            break

        if "next_token" in json_response["meta"]:
            next_token = json_response["meta"]["next_token"]

            if result_count is not None and result_count > 0 and next_token is not None:
                count += result_count
                print("     {} tweets saved now...".format(count))

                response__, json_response = connect_to_endpoint(BT, id_, next_token)

                print("+++++", user_, "+++++")
                print("+++++", user_, "+++++")
                print("+++++", user_, "+++++")
                print("--------------------------------")
                print(
                    "x-rate-limit-remaining",
                    response__.headers["x-rate-limit-remaining"],
                )
                print("x-rate-limit-rest", response__.headers["x-rate-limit-reset"])
                print("--------------------------------")

                time.sleep(3)

                # with open(
                #     "/home/tmasukawa/tweet-analysis/data/tweet-data-random/test_{}.json".format(
                #         json_count
                #     ),
                #     "a",
                #     encoding="utf-8-sig",
                # ) as js:
                #     json.dump(
                #         json_response, js, indent=4, sort_keys=True, ensure_ascii=False
                #     )
                #     json_count += 1

                df_next = pd.json_normalize(json_response["includes"]["tweets"])
                df_reindex_next = df_next.reindex(
                    columns=[
                        "id",
                        "text",
                        "author_id",
                        "public_metrics.retweet_count",
                        "public_metrics.reply_count",
                        "public_metrics.like_count",
                        "public_metrics.quote_count",
                        "public_metrics.bookmark_count",
                        "public_metrics.impression_count",
                        "created_at",
                    ]
                )
                df_reindex_next.to_csv(
                    "BuzzTweetData_{}.csv".format(
                        now.strftime("%Y-%m-%d")
                    ),
                    encoding="utf-8-sig",
                    mode="a",
                    header=False,
                    index=False,
                )

                df_next2 = pd.json_normalize(json_response["includes"]["users"])
                df_reindex_next2 = df_next2.reindex(
                    columns=[
                        "username",
                        "name",
                        "id",
                        "created_at",
                        "description",
                        "public_metrics.followers_count",
                        "public_metrics.following_count",
                        "public_metrics.tweet_count",
                        "public_metrics.listed_count",
                    ]
                )
                df_reindex_next2.to_csv(
                    "BuzzUserData_{}.csv".format(
                        now.strftime("%Y-%m-%d")
                    ),
                    encoding="utf-8-sig",
                    mode="a",
                    header=False,
                    index=False,
                )

                json_count += 1

                if int(response__.headers["x-rate-limit-remaining"]) == 0:
                    waitUntilReset((response__.headers["x-rate-limit-reset"]))

        else:
            flag = False

print("\nTotal Tweet IDs saved: {}\n".format(count))
