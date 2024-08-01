import requests
import csv

def get_places(latitude, longitude, radius, csv_file):
    latitude = str(latitude)
    longitude = str(longitude)
    radius = str(radius)
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json];
        (
        node["amenity"="restaurant"](around:{radius},{latitude},{longitude});
        way["amenity"="restaurant"](around:{radius},{latitude},{longitude});
        relation["amenity"="restaurant"](around:{radius},{latitude},{longitude});

        node["amenity"="cafe"](around:{radius},{latitude},{longitude});
        way["amenity"="cafe"](around:{radius},{latitude},{longitude});
        relation["amenity"="cafe"](around:{radius},{latitude},{longitude});

        node["amenity"="pub"](around:{radius},{latitude},{longitude});
        way["amenity"="pub"](around:{radius},{latitude},{longitude});
        relation["amenity"="pub"](around:{radius},{latitude},{longitude});
        );
        out body;
        >;
        out skel qt;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})

    if response.status_code == 200:
        data = response.json()
        places = []
        seen = set()

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

                tuple_name = tuple(name)

                if tuple_name not in seen:
                    places.append([name, type, address, phone, website, wifi])
                    seen.add(tuple_name)

        # Filtering places that don't have website and names
        places_complete = []
    
        for place in places:
            if place[0] != 'Unknown' and place[1] != 'Unknown' and place[4] != 'Website Unknown':
                places_complete.append(place)

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(places_complete)

    else:
        print(f"Error fetching data: {response.status_code} - {response.reason}")