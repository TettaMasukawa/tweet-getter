import pandas as pd

from twitter_api_connect import connect_to_endpoint, waitUntilReset


def get_id(BT, username):
    url = "https://api.twitter.com/2/users/by"
    params1 = {"usernames": "{}".format(username), "user.fields": "id"}
    headers = {"Authorization": "Bearer {}".format(BT)}
    response, json_response = connect_to_endpoint(url, params1, headers)

    if int(response.headers["x-rate-limit-remaining"]) == 0:
        waitUntilReset(response.headers["x-rate-limit-reset"])
        
    try:
        id = json_response["data"][0]["id"]
    except:
        return False

    return id

if __name__ == "__main__":
    BT = ""
    csv = pd.read_csv("", encoding="utf-8-sig")
    
    id_list = []
    
    for n in range(len(csv)):
        id = get_id(BT, csv["account"][n])
        id_list.append(id)
        
    csv["id"] = id_list
    
    csv.to_csv("", encoding="utf-8-sig", mode="w")
