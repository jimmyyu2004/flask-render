import csv

def merge_files_func(places_file, contacts_file, output_path):
    def remove_duplicates(list_of_lists):
        seen = set()
        unique_lists = []

        for lst in list_of_lists:
            tuple_lst = tuple(lst)
            if tuple_lst not in seen:
                unique_lists.append(lst)
                seen.add(tuple_lst)

        return unique_lists

    places_file = remove_duplicates(places_file)

    merged_list = []
    for place in places_file:
        for contact in contacts_file:
            merged_row = [place[0], place[1], place[2], place[3], place[4], place[5]]
            if (place[0] == contact[0]):
                merged_row.append(contact[1])
                merged_row.append(contact[2])
                merged_list.append(merged_row)

    headers = ["Company Name", "Type", "Address", "Phone", "Website", "Wifi", "Contact", "Link"]

    with open(output_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(merged_list)

