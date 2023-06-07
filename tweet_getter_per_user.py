# import json
import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from name2id import get_id
from twitter_api_connect import waitUntilReset


def connect_to_endpoint(bearer_token, screenname, next_token=None):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/all"

    # replace appropriate start and end times below
    if next_token is not None:
        params = {
            "query": "from:{} -is:retweet lang:ja".format(screenname),
            "tweet.fields": "author_id,conversation_id,created_at,geo,id,in_reply_to_user_id,public_metrics,text",
            "expansions": "referenced_tweets.id.author_id",
            "user.fields": "created_at,description,id,location,name,public_metrics,username",
            "max_results": "500",
            "start_time": "2006-03-21T00:00:00Z",
            "end_time": "2022-10-31T23:59:59Z",
            "pagination_token": str(next_token),
        }

    else:
        params = {
            "query": "from:{} -is:retweet lang:ja".format(screenname),
            "tweet.fields": "author_id,conversation_id,created_at,geo,id,in_reply_to_user_id,public_metrics,text",
            "expansions": "referenced_tweets.id.author_id",
            "user.fields": "created_at,description,id,location,name,public_metrics,username",
            "max_results": "500",
            "start_time": "2006-03-21T00:00:00Z",
            "end_time": "2022-10-31T23:59:59Z",
        }

    response = requests.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response, response.json()


# Bearer token
BT = ""

csv = pd.read_csv("", encoding="utf-8-sig", sep=",")

user_list = []

for i in range(len(csv)):
    user_list.append(csv[""][i])


error_list = []

t_delta = timedelta(hours=9)
JST = timezone(t_delta, "JST")
now = datetime.now(JST)

json_response = ""
num_requests = 0

for username in user_list:
    
    flag = True
    json_count = 0
    count = 0
    
    while flag:
        if json_count == 0:
            if num_requests >= 180:
                time.sleep(30)
                num_requests = 0
            
            response_, json_response = connect_to_endpoint(BT, username)
            num_requests += 1
            
            # print(json_response)

            print("+++++", username, "+++++")
            print("+++++", username, "+++++")
            print("+++++", username, "+++++")
            print("--------------------------------")
            print(
                "x-rate-limit-remaining",
                response_.headers["x-rate-limit-remaining"],
            )
            print("x-rate-limit-reset", response_.headers["x-rate-limit-reset"])
            print("--------------------------------")

            time.sleep(5)

            try:
                if 'data' in json_response:
                    df = pd.json_normalize(json_response["data"])
                else:
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
                        "public_metrics.impression_count",
                        "public_metrics.bookmark_count",
                        "created_at",
                        "conversation_id",
                        "in_reply_to_user_id",
                        "geo.place_id",
                    ]
                )
                df_re.to_csv(
                    "", #保存先
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
                        "location",
                        "description",
                        "public_metrics.followers_count",
                        "public_metrics.following_count",
                        "public_metrics.tweet_count",
                        "public_metrics.listed_count",
                    ]
                )
                df_reindex2.to_csv(
                    "", #保存先
                    encoding="utf-8-sig",
                    index=False,
                )

                json_count += 1

                if int(response_.headers["x-rate-limit-remaining"]) == 0:
                    waitUntilReset(int(response_.headers["x-rate-limit-reset"]))
                    
            except:
                error_list.append(username)
                break

        try:
            result_count = json_response["meta"]["result_count"]

        except Exception:
            result_count = None
            break

        if "next_token" in json_response["meta"]:
            next_token = json_response["meta"]["next_token"]

            if result_count is not None and result_count > 0 and next_token is not None:
                count += result_count
                print("     {} tweets saved now...\n".format(count))

                response__, json_response = connect_to_endpoint(BT, username, next_token)
                num_requests += 1
                
                # print(json_response)

                print("+++++", username, "+++++")
                print("+++++", username, "+++++")
                print("+++++", username, "+++++")
                print("--------------------------------")
                print(
                    "x-rate-limit-remaining",
                    response__.headers["x-rate-limit-remaining"],
                )
                print("x-rate-limit-rest", response__.headers["x-rate-limit-reset"])
                print("--------------------------------")

                time.sleep(5)

                try:
                    if "data" in json_response:
                        df_next = pd.json_normalize(json_response["data"])
                    else:
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
                            "public_metrics.impression_count",
                            "public_metrics.bookmark_count",
                            "created_at",
                            "conversation_id",
                            "in_reply_to_user_id",
                            "geo.place_id",
                        ]
                    )
                    df_reindex_next.to_csv(
                        "", #保存先
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
                            "location",
                            "description",
                            "public_metrics.followers_count",
                            "public_metrics.following_count",
                            "public_metrics.tweet_count",
                            "public_metrics.listed_count",
                        ]
                    )
                    df_reindex_next2.to_csv(
                        "", #保存先
                        encoding="utf-8-sig",
                        mode="a",
                        index=False,
                        header=False
                    )

                    json_count += 1

                    if int(response__.headers["x-rate-limit-remaining"]) == 0:
                        waitUntilReset((int(response__.headers["x-rate-limit-reset"])))
                        
                except:
                    break

        else:
            flag = False

    print("\n{} Total Tweets: {}\n".format(username, count))

print(error_list)
