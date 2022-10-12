import os
import time

import pandas as pd
import requests

from twitter_api_connect import waitUntilReset

# Bearer token
BT = ""

def connect_to_endpoint(bearer_token, user_id, next_token=None):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)

    # replace appropriate start and end times below
    if next_token is not None:
        params = {
            "tweet.fields": "author_id,created_at,public_metrics,text",
            "expansions": "author_id",
            "user.fields": "description,created_at,public_metrics",
            "max_results": "100",
            "exclude": "retweets",
            "pagination_token": str(next_token),
        }

    else:
        params = {
            "tweet.fields": "author_id,created_at,public_metrics,text",
            "expansions": "author_id",
            "user.fields": "description,created_at,public_metrics",
            "max_results": "100",
            "exclude": "retweets",
        }

    response = requests.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response, response.json()


id_list = {}  # "screenname": "user_id"

remove_user_list = []

for i__, (user_, id_) in enumerate(id_list.items()):
    if i__ < 50:
        print("+++++", i__, "+++++")
        print("+++++", i__, "+++++")
        print("+++++", i__, "+++++")
        print("+++++", i__, "+++++")
        print("+++++", i__, "+++++")
        print("+++++", i__, "+++++")

        os.makedirs(
            "/home/tmasukawa/tweet-analysis/data/yamada_2/tweets_data/{}".format(
                str(user_)
            ),
            exist_ok=True,
        )

        os.makedirs(
            "/home/tmasukawa/tweet-analysis/data/yamada_2/user's_info",
            exist_ok=True,
        )

        flag = True
        json_count = 0
        count = 0

        while flag:
            print(user_)
            # Replace the count below with the number of Tweetsyou want to stop at.
            # Note: running without the count check will result in getting more Tweets
            # that will count towards the Tweet cap

            # if count >= 10:
            #     break
            if json_count == 0:
                response_, json_response = connect_to_endpoint(BT, id_)

                print("----------------------")
                print(
                    "x-rate-limit-remaining",
                    response_.headers["x-rate-limit-remaining"],
                )
                print("x-rate-limit-reset", response_.headers["x-rate-limit-reset"])
                print("----------------------")

                # time.sleep(3)

                df = pd.json_normalize(json_response["data"])
                df.to_csv(
                    "/home/tmasukawa/tweet-analysis/data/yamada_2/tweets_data/{}/{}_{}.csv".format(
                        user_, user_, json_count
                    ),
                    encoding="utf-8-sig",
                    index=False,
                )

                df2 = pd.json_normalize(json_response["includes"]["users"])
                df2.to_csv(
                    "/home/tmasukawa/tweet-analysis/data/yamada_2/user's_info/{}_info.csv".format(
                        user_
                    ),
                    encoding="utf-8-sig",
                    index=False,
                )

                json_count += 1

                if int(response_.headers["x-rate-limit-remaining"]) == 0:
                    waitUntilReset(response_.headers["x-rate-limit-reset"])

            # print(json_response)
            # sys.exit()
            """
            for tweet_ in json_response['includes']['users']:
                # Replace with your path below
                # print(tweet_['username'])
                screenname_set = screenname_set.union([tweet_['username']])
            """

            try:
                result_count = json_response["meta"]["result_count"]

            except Exception:
                # private account
                remove_user_list.append(user_)
                break

            if "next_token" in json_response["meta"]:
                next_token = json_response["meta"]["next_token"]

                if (
                    result_count is not None
                    and result_count > 0
                    and next_token is not None
                ):
                    count += result_count
                    print(count)
                    response__, json_response = connect_to_endpoint(BT, id_, next_token)

                    print("-----------------------")
                    print(
                        "x-rate-limit-remaining",
                        response__.headers["x-rate-limit-remaining"],
                    )
                    print("x-rate-limit-rest", response__.headers["x-rate-limit-reset"])
                    print("-----------------------")

                    time.sleep(3)

                    df = pd.json_normalize(json_response["data"])
                    df.to_csv(
                        "/home/tmasukawa/tweet-analysis/data/yamada_2/tweets_data/{}/{}_{}.csv".format(
                            user_, user_, json_count
                        ),
                        encoding="utf-8-sig",
                        index=False,
                    )

                    df2 = pd.json_normalize(json_response["includes"]["users"])
                    df2.to_csv(
                        "/home/tmasukawa/tweet-analysis/data/yamada_2/user's_info/{}_info.csv".format(
                            user_
                        ),
                        mode="w",
                        encoding="utf-8-sig",
                        index=False,
                    )

                    json_count += 1

                    if int(response__.headers["x-rate-limit-remaining"]) == 0:
                        waitUntilReset(response__.headers["x-rate-limit-reset"])

                    # print(screenname_set)
            else:
                remove_user_list.append(user_)
                flag = False

        print("Total Tweet IDs saved: {}".format(count))
# print('screen_name', screenname_set)

# with open('/content/drive/My Drive/depression_data/screenname_1month.txt', 'a', encoding = 'utf_8_sig') as aaa:
#     aaa.write(str(screenname_set))
