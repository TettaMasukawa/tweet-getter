# import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from twitter_api_connect import waitUntilReset


def connect_to_endpoint(bearer_token, next_token=None):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/all"

    # replace appropriate start and end times below
    if next_token is not None:
        params = {
            "query": "-RT (あ OR い OR う OR え OR お OR か OR き OR く OR け OR こ OR さ OR し OR す OR せ OR そ OR た OR ち OR つ OR て OR と OR な OR に OR ぬ OR ね OR の OR は OR ひ OR ふ OR へ OR ほ OR ま OR み OR む OR め OR も OR や OR ゆ OR よ OR ら OR り OR る OR れ OR ろ OR わ OR を OR ん OR が OR ぎ OR ぐ OR げ OR ご OR ざ OR じ OR ず OR ぜ OR ぞ OR だ OR ぢ OR づ OR で OR ど OR ば OR び OR ぶ OR べ OR ぼ OR ぱ OR ぴ OR ぷ OR ぺ OR ぽ) -is:retweet -is:quote -has:mentions -has:media lang:ja",
            "tweet.fields": "author_id,created_at,public_metrics",
            "expansions": "author_id",
            "user.fields": "description,created_at,public_metrics",
            "max_results": "10",
            "pagination_token": str(next_token),
            "start_time": "2020-03-01T00:00:00Z",
            "end_time": "2020-04-01T00:00:00Z",
        }

    else:
        params = {
            "query": "-RT (あ OR い OR う OR え OR お OR か OR き OR く OR け OR こ OR さ OR し OR す OR せ OR そ OR た OR ち OR つ OR て OR と OR な OR に OR ぬ OR ね OR の OR は OR ひ OR ふ OR へ OR ほ OR ま OR み OR む OR め OR も OR や OR ゆ OR よ OR ら OR り OR る OR れ OR ろ OR わ OR を OR ん OR が OR ぎ OR ぐ OR げ OR ご OR ざ OR じ OR ず OR ぜ OR ぞ OR だ OR ぢ OR づ OR で OR ど OR ば OR び OR ぶ OR べ OR ぼ OR ぱ OR ぴ OR ぷ OR ぺ OR ぽ) -is:retweet -is:quote -has:mentions -has:media lang:ja",
            "tweet.fields": "author_id,created_at,public_metrics",
            "expansions": "author_id",
            "user.fields": "description,created_at,public_metrics",
            "max_results": "10",
            "start_time": "2020-03-01T00:00:00Z",
            "end_time": "2020-04-01T00:00:00Z",
        }

    response = requests.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response, response.json()


os.makedirs(
    "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original",
    exist_ok=True,
)

# Bearer token
BT = "AAAAAAAAAAAAAAAAAAAAAD%2FJPQEAAAAA7%2BNdrLam%2FkVdRcU3%2B6I5tA6I8Ic%3DljqTXJKdge7Uid3JlwgKsalU2xFBXlrq9Wzpe09xF2azv0rKvB"

LIMIT_COUNT = 10

t_delta = timedelta(hours=9)
JST = timezone(t_delta, "JST")
now = datetime.now(JST)

if (
    os.path.exists(
        "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/TweetDataRandom_{}.csv".format(
            now.strftime("%Y-%m-%d")
        )
    )
    is True
):
    os.remove(
        "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/TweetDataRandom_{}.csv".format(
            now.strftime("%Y-%m-%d")
        )
    )

if (
    os.path.exists(
        "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/UserDataRandom_{}.csv".format(
            now.strftime("%Y-%m-%d")
        )
    )
    is True
):
    os.remove(
        "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/UserDataRandom_{}.csv".format(
            now.strftime("%Y-%m-%d")
        )
    )

flag = True
json_count = 0
count = 0
json_response = ""

while flag:
    if count >= LIMIT_COUNT:
        break

    if json_count == 0:
        response_, json_response = connect_to_endpoint(BT)

        print("--------------------------------")
        print(
            "x-rate-limit-remaining",
            response_.headers["x-rate-limit-remaining"],
        )
        print("x-rate-limit-reset", response_.headers["x-rate-limit-reset"])
        print("--------------------------------")

        time.sleep(3)

        # with open(
        #     "/home/tmasukawa/tweet-analysis/data/tweet-data-random/test_{}.json".format(
        #         json_count
        #     ),
        #     "a",
        #     encoding="utf-8-sig",
        # ) as js:
        #     json.dump(json_response, js, indent=4, sort_keys=True, ensure_ascii=False)
        #     json_count += 1

        df = pd.json_normalize(json_response["data"])
        df_re = df.reindex(
            columns=[
                "id",
                "text",
                "author_id",
                "public_metrics.retweet_count",
                "public_metrics.reply_count",
                "public_metrics.like_count",
                "public_metrics.quote_count",
                "created_at",
            ]
        )
        df_re.to_csv(
            "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/TweetDataRandom_{}.csv".format(
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
            "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/UserDataRandom_{}.csv".format(
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

    if "next_token" in json_response["meta"]:
        next_token = json_response["meta"]["next_token"]

        if result_count is not None and result_count > 0 and next_token is not None:
            count += result_count
            print("     {} tweets saved now...".format(count))

            if count >= LIMIT_COUNT:
                break

            response__, json_response = connect_to_endpoint(BT, next_token)

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

            df_next = pd.json_normalize(json_response["data"])
            df_reindex_next = df_next.reindex(
                columns=[
                    "id",
                    "text",
                    "author_id",
                    "public_metrics.retweet_count",
                    "public_metrics.reply_count",
                    "public_metrics.like_count",
                    "public_metrics.quote_count",
                    "created_at",
                ]
            )
            df_reindex_next.to_csv(
                "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/TweetDataRandom_{}.csv".format(
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
                "/home/tmasukawa/tweet-analysis/data/tweet-data-random/original/UserDataRandom_{}.csv".format(
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
