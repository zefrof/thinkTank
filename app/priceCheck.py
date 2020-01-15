import json, requests, time, json

def main():

    #Get auth token from TCGPlayer
        bearer = requests.post("https://api.tcgplayer.com/token",
            data = {
                "grant_type": "client_credentials",
                "client_id": "A7A184B3-923E-49EC-900F-204016D37EE2",
                "client_secret": "646E7BEC-556B-45EF-8746-3ADCF32FAB49",
            })
        token = bearer.json()

        try:
            tcgplayerId = '125843'

            url = "https://api.tcgplayer.com/v1.27.0/pricing/product/" + tcgplayerId
            r = requests.get(url, headers = {'Authorization' : "Bearer " + token['access_token'],})
            priceData = json.loads(r.text)

            #print(r.text)

            print(priceData)

        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()
