import requests
import csv


overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
    [out:json];
    (
      node["amenity"="restaurant"](around:100,51.5074,-0.1278);
      way["amenity"="restaurant"](around:100,51.5074,-0.1278);
      relation["amenity"="restaurant"](around:100,51.5074,-0.1278);

      node["amenity"="cafe"](around:100,51.5074,-0.1278);
      way["amenity"="cafe"](around:100,51.5074,-0.1278);
      relation["amenity"="cafe"](around:100,51.5074,-0.1278);

      node["amenity"="pub"](around:100,51.5074,-0.1278);
      way["amenity"="pub"](around:100,51.5074,-0.1278);
      relation["amenity"="pub"](around:100,51.5074,-0.1278);
    );
    out body;
    >;
    out skel qt;
"""

response = requests.get(overpass_url, params={'data': overpass_query})

if response.status_code == 200:
    data = response.json()
    places_with_wifi = []

    for element in data['elements']:
        if 'tags' in element:
            name = element['tags'].get('name', 'Unknown')
            type = element['tags'].get('amenity', 'Unknown')
            house_num = element['tags'].get('addr:housenumber', '')
            street = element['tags'].get('addr:street', '')
            postcode = element['tags'].get('addr:postcode', '')
            phone = element['tags'].get('phone', 'Phone Unknown')
            website = element['tags'].get('website', 'Website Unknown')
            wifi = "false"
            
            if element['tags'].get('internet_access', '') == 'wlan':
                wifi = "true"

            address = house_num + ' ' + street + ' ' + postcode

            places_with_wifi.append([name, type, address, phone, website, wifi])

    # Separate places with wifi into complete and incomplete
    places_with_wifi_complete = []
    places_with_wifi_incomplete = []
    for place in places_with_wifi:
        if place[0] != 'Unknown' and place[1] != 'Unknown' and place[2] != '  ' and place[3] != 'Phone Unknown' and place[4] != 'Website Unknown':
            places_with_wifi_complete.append(place)
        elif place[0] != 'Unknown' and place[2] != '  ':
            places_with_wifi_incomplete.append(place)

    file_complete_csv = 'complete.csv'
    with open(file_complete_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(places_with_wifi_complete)
    
    
    file_incomplete_csv = 'incomplete.csv'
    with open(file_incomplete_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(places_with_wifi_incomplete)

else:
    print(f"Error fetching data: {response.status_code} - {response.reason}")