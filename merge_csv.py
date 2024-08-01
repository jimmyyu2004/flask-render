import csv

def main():
    def remove_duplicates(list_of_lists):
        seen = set()
        unique_lists = []

        for lst in list_of_lists:
            tuple_lst = tuple(lst)
            if tuple_lst not in seen:
                unique_lists.append(lst)
                seen.add(tuple_lst)

        return unique_lists
    
    with open('/Users/jimmyyu/results_2_500.csv', 'r') as file_1:
        contacts_file_ex = list(csv.reader(file_1))
        contacts_file = remove_duplicates(contacts_file_ex)

    
    with open('/Users/jimmyyu/complete.csv', 'r') as file_2:
        places_file = list(csv.reader(file_2))

    merged_list = []
    for place in places_file:
        for contact in contacts_file:
            merged_row = [place[0], place[1], place[2], place[3], place[4], place[5]]
            if (place[0] == contact[0]):
                merged_row.append(contact[1])
                merged_row.append(contact[2])
                merged_list.append(merged_row)

    headers = ["Company Name", "Type", "Address", "Phone", "Website", "Wifi", "Contact", "Link"]

    with open('merged_csv_2_500.csv', 'w') as file_3:
        writer = csv.writer(file_3)
        writer.writerow(headers)
        writer.writerows(merged_list)
                
main()

