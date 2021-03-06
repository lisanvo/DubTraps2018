import requests, http.client, urllib.request, urllib.parse, urllib.error, json, pyodbc

# Replace the subscription_key string value with your valid subscription key.
subscription_key = '0ed7b46d5b8a4e4aaa155f066e8a928a'

# Replace or verify the region.
#
# You must use the same region in your REST API call as you used to obtain your subscription keys.
# For example, if you obtained your subscription keys from the westus region, replace
# "westcentralus" in the URI below with "westus".
#
# NOTE: Free trial subscription keys are generated in the westcentralus region, so if you are using
# a free trial subscription key, you should not need to change this region.
uri_base = 'westcentralus.api.cognitive.microsoft.com'

vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze?"

analyze_url = vision_base_url + "analyze"

# SQL Stuff

server = 'dubtraps2018.database.windows.net'
database = 'DubTraps2018'
username = 'sadettan'
password = 'DubTraps2018'
driver = '{ODBC Driver 13 for SQL Server}'
# cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cnxn = pyodbc.connect('DRIVER=%s;SERVER=%s;PORT=1433;DATABASE=%s;UID=%s;PWD=%s' % (driver, server, database, username, password))

cursor = cnxn.cursor()


class ReadImage:
    # Replace the three dots below with the URL of a JPEG image of a celebrity.
    def __init__(self, url, local):
        self.parsed = self._getjson(url, local)
        if self.parsed is None:
            print("Exit")
            return 1
        self.dict = dict()
        self.name = None
        self._gettags(self.parsed)
        self._list_of_names()
        self._getdata = self._readSQL()

    def _getjson(self, url, local):
        if local:
            headers = {
                # Request headers.
                'Content-Type': 'application/octet-stream',
                'Ocp-Apim-Subscription-Key': subscription_key,
            }

            params = urllib.parse.urlencode({
                # Request parameters. All of them are optional.
                'visualFeatures': 'Tags,Color',
                'language': 'en',
            })
            image_path = open(url, "rb").read()
            try:
                # Execute the REST API call and get the response.
                response = requests.post(analyze_url, headers=headers, params=params, data=image_path)
                response.raise_for_status()

                analysis = response.json()
                print(analysis)
                # 'data' contains the JSON data. The following formats the JSON data for display.
                parsed = response.json()

                print("Response:")
                print(json.dumps(parsed, sort_keys=True, indent=2))
                return parsed

            except Exception as e:
                print('Error:')
                print(e)  # print(self.response.url
                return None

        # Not local, regular url
        else:
            headers = {
                # Request headers.
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': subscription_key,
            }

            params = urllib.parse.urlencode({
                # Request parameters. All of them are optional.
                'visualFeatures': 'Tags',
                'language': 'en',
            })

            body = "{'url': '%s'}" % url
            try:
                # Execute the REST API call and get the response.
                conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
                conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
                response = conn.getresponse()
                data = response.read()

                # 'data' contains the JSON data. The following formats the JSON data for display.
                parsed = json.loads(data)

                print("Response:")
                print(json.dumps(parsed, sort_keys=True, indent=2))
                conn.close()
                return parsed

            except Exception as e:
                print('Error:')
                print(e)  # print(self.response.url
                return None

    def _gettags(self, response):
        for x in response['tags']:
            self.dict[x['name']] = x['confidence']
            self.name = x['name']

    def _list_of_names(self):
        names = list()
        for x in self.dict:
            names.append(x)
        self.names = names

    def _readSQL(self):
        for x in self.names:
            temp = "'%s%s'" % (x, '%')
            cursor.execute("SELECT * FROM Nutrition WHERE name LIKE " + temp)
            vars = ["Name", "Calories", "Protein", "Fat", "Carbs", "Sugar",
                    "Sodium", "Cholesterol", "Sat. Fat", "Net Carbs"]
            s = "<table style='border:1px solid red'>"
            for row in cursor:
                s = s + "<tr>"
                # print(row)
                # print(vars)
                for x in range(0, len(row)):

                    s = s + "<th>" + vars[x] + "</th>"
                    s = s + "<td>" + str(row[x]) + "</td>"
            s = s + "</tr>"

            return s