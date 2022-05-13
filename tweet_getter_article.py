import datetime
import os
import sys
import time

import pandas as pd
import requests

# Bearer token
BT = "AAAAAAAAAAAAAAAAAAAAAD%2FJPQEAAAAA7%2BNdrLam%2FkVdRcU3%2B6I5tA6I8Ic%3DljqTXJKdge7Uid3JlwgKsalU2xFBXlrq9Wzpe09xF2azv0rKvB"


def waitUntilReset(reset):
    """
    reset 時刻まで sleep
    """
    seconds = reset - time.mktime(datetime.detetime.now().timetuple())
    seconds = max(seconds, 0)
    print("\n     =====================")
    print("     == waiting %d sec ==" % seconds)
    print("     =====================")
    sys.stdout.flush()
    time.sleep(seconds + 30)  # 念のため + 10 秒


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


id_list = {
    "c_hocknews": "905699646256721921",
    "chuspo": "131455845",
    "danketsu_rentai": "1083251991424323584",
    "hamemen": "68571425",
    "hiranok": "94513095",
    "hirox": "3920121",
    "hokuchu_komatsu": "1068110633495814144",
    "ISOKO_MOCHIZUKI": "119363202",
    "KadotaRyusho": "1128981340848656384",
    "katsuyatakasu": "362401254",
    "kenminfukui": "1210084732999876609",
    "kimi_aya_": "4598644933",
    "koseiHENTAIbot": "1056927836286574592",
    "MagnoliaAliceF": "1084229219138252800",
    "MatsumotohaJimu": "148659115",
    "ogi_fuji_npo": "60241834",
    "Narodovlastiye": "1161797133424455680",
    "news_zoo": "243244921",
    "NOSUKE": "35356894",
    "ozawa_jimusho": "188620283",
    "pioneertaku": "98793189",
    "RibbonChieko": "2264718120",
    "RyuichiYoneyama": "84782143",
    "SatoMasahisa": "112551613",
    "SaYoNaRaKiNo": "1128311464391991296",
    "shima_keishi": "1263839615560978432",
    "sibakendona": "313229089",
    "skyteam": "42802981",
    "ssimtok": "3140359753",
    "takedasatetsu": "2758783248",
    "TJO_datasci": "1320611023",
    "tsuda": "4171231",
    "yohei_tsushima": "36673871",
    "yonecyoko": "163426680",
}  # "screenname": "user_id"

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
