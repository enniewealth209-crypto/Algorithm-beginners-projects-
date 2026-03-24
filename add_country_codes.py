import csv
import pycountry

input_file = 'data/countries.csv'
output_file = 'data/countries_with_codes.csv'

def get_country_code(country_name):
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_2.lower()
    except LookupError:
        return ''

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', encoding='utf-8', newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header + ['Country Code'])

    for row in reader:
        country_name = row[0]
        country_code = get_country_code(country_name)
        writer.writerow(row + [country_code])

print(f'Successfully updated {input_file} and saved to {output_file}')
