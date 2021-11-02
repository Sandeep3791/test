import requests

url = "https://api.barcodelookup.com/v3/products?barcode=8901262072052&formatted=y&key=2ppq23rl3qiilkkc0k315y1ft3ytxw"

headers = {
    'x-rapidapi-host': "barcode-lookup.p.rapidapi.com",
    # 'x-rapidapi-key': "2ppq23rl3qiilkkc0k315y1ft3ytxw"
}

response = requests.request("GET", url, headers=headers)

print(response.text)
