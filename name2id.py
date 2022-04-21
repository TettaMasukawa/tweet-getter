import requests


def create_url(usernames, user_fields):
    if any(usernames):
        formatted_user_names = "usernames=" + ",".join(usernames)
    else:
        formatted_user_names = ""

    if any(user_fields):
        formatted_user_fields = "user.fields=" + ",".join(user_fields)
    else:
        formatted_user_fields = "user_fields=id,name,username"

    url = "https://api.twitter.com/2/users/by?{}&{}".format(
        formatted_user_names, formatted_user_fields
    )
    return url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    BT = "AAAAAAAAAAAAAAAAAAAAAC%2FlQgEAAAAAi9yH0D1YnXy%2F4tKDFNd4Jw%2B9GyQ%3DukHqkVzZWJQX48nwMVys5VglneLIRW3CG566Z0ZY8SUCBkGPsa"
    usernames = [
        "poke_mopu",  # screenname here!
    ]
    user_fields = ["id"]

    url = create_url(usernames, user_fields)
    headers = create_headers(BT)
    json_response = connect_to_endpoint(url, headers)
    data = json_response["data"]

    print(data)


if __name__ == "__main__":
    main()
