import requests
import json

from credentials import access_token as TOKEN
from constants import ALL_ACTS_JSON, LATLNG_ACTS_JSON
from clean import get_ids

import progressbar


class StravaRequestor():

    def __init__(self, access_token):
        self.params = {}
        self.params['access_token'] = access_token
        self.base_url = 'https://www.strava.com/api/v3/'

    def get_activity(self, activity_id):
        """
        Gets activity JSON from API
        """
        r = requests.get('{}{}{}'.format(self.base_url, 'activities/', activity_id),
                        params=self.params)
        data = r.json()
        return {'polyline': data['map']['polyline'],
                'distance': data['distance'] / 1609,
                'date': data['start_date_local']}

    def get_latlng(self, activity_id):
        """
        Get latitude-longitude data from activity
        """
        r = requests.get('{}activities/{}/streams/latlng'.format(self.base_url, activity_id),
                         params=self.params)
        try:
            data = r.json()
        except:
            return {}
        return data

    def get_activities(self, limit=20):
        """
        Gets the short activity details and dumps to file
        """
        params = self.params.copy()  # we're editing this so make a copy
        #params['per_page'] = min(limit, 200)  # 200 is max number of activities we can load in a page
        #params['page'] = 0
        total = 0
        activities = []
        while total < limit:
            #params['page'] += 1
            #total += params['per_page']
            total+=300
            try:
                r = requests.get('https://www.strava.com/api/v3/athlete', params=params)
                #r = requests.get('{}activities'.format(self.base_url), params=params)
                activities += r.json()
            except:
                print("Reached Limit Number of activites")
                break

        return activities


def scrape_activities(access_token):

    client = StravaRequestor(access_token)

    print("Obtaining activity data...")

    activities = client.get_activities(limit=200)
    with open(ALL_ACTS_JSON, 'w') as f:
        f.write(json.dumps(activities, indent=4))


if __name__ == '__main__':
    client = StravaRequestor(TOKEN)

    print("Obtaining activity data...")

    activities = client.get_activities(limit=200)
    with open(ALL_ACTS_JSON, 'w') as f:
        f.write(json.dumps(activities, indent=4))

    # ids = get_ids()
    # all_activites = []
    #
    # print("Obtaining Lat-Long data...")
    # for a_id in ids:
    #     a = client.get_latlng(a_id)
    #     all_activites.append(a)
    # with open(LATLNG_ACTS_JSON, 'w') as f:
    #     f.write(json.dumps(all_activites, indent=4))