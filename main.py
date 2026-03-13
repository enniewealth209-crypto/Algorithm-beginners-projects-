import csv

def load_countries(filename):
    country_names = []
    country_data = {}

    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Skip completely empty rows
            if not row or row['Country'] is None:
                continue

            # Safely get values
            name = (row.get('Country') or "").strip()
            capital = (row.get('Capital') or "").strip()
            continent = (row.get('Continent') or "").strip()
            population = (row.get('Population') or "").strip()

            # Skip rows with no country name
            if name == "":
                continue

            country_names.append(name)

            country_data[name] = {
                'Capital': capital,
                'Continent': continent,
                'Population': population
            }

    # Binary search requires sorted list
    country_names.sort()

    return country_names, country_data


def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = arr[mid]

        if mid_val == target:
            return True

        elif mid_val < target:
            low = mid + 1

        else:
            high = mid - 1

    return False


def main():
    filename = 'countries.csv'   # Make sure this matches your file name
    country_list, country_info = load_countries(filename)

    while True:
        country_input = input("Enter country name (or 'exit' to quit): ").strip().title()

        if country_input.lower() == "exit":
            print("Goodbye!")
            break

        if binary_search(country_list, country_input):
            info = country_info[country_input]

            print("\nCountry:", country_input)
            print("Capital:", info['Capital'])
            print("Continent:", info['Continent'])
            print("Population:", info['Population'])
            print()

        else:
            print(f"\nCountry '{country_input}' not found!, misspelled or does not exit.\n")


if __name__ == '__main__':
    main()