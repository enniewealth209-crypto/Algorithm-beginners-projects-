import csv
import os

class CountryLogic:
    """
    Handles data management and searching logic for the Country Information Lookup System.
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.country_names = []  # Sorted list of country names for binary search
        self.country_data = {}   # Dictionary mapping names to full data
        self.load_data()

    def load_data(self):
        """
        Loads country data from the CSV file and prepares it for searching.
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Country database file not found at: {self.csv_path}")

        try:
            with open(self.csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = str(row.get('Country') or '').strip()
                    if not name: continue
                    
                    # Store data with default values
                    self.country_names.append(name)
                    self.country_data[name.lower()] = {
                        'name': name,
                        'capital': str(row.get('Capital') or 'N/A').strip(),
                        'continent': str(row.get('Continent') or 'N/A').strip(),
                        'population': self._parse_population(row.get('Population')),
                        'country_code': str(row.get('Country Code') or '').strip().lower()
                    }
            
            self.country_names.sort(key=str.lower)
        except Exception as e:
            raise RuntimeError(f"Failed to process country database: {e}")

    def _parse_population(self, raw_value):
        if not raw_value: return 0
        try:
            return int(str(raw_value).replace(',', '').strip())
        except ValueError:
            return 0

    def binary_search(self, target):
        """
        Implementation of the binary search algorithm to find a country.
        Returns the country name if found (original casing), otherwise None.
        """
        low = 0
        high = len(self.country_names) - 1
        target_lower = target.lower()

        while low <= high:
            mid = (low + high) // 2
            mid_val = self.country_names[mid]
            
            # Case-insensitive comparison
            if mid_val.lower() == target_lower:
                return mid_val
            elif mid_val.lower() < target_lower:
                low = mid + 1
            else:
                high = mid - 1
        return None

    def get_country_info(self, query):
        """
        Searches for a country using binary search and returns its full info.
        """
        match = self.binary_search(query)
        if match:
            return self.country_data.get(match.lower())
        return None

    def get_suggestions(self, partial_query):
        """
        Returns a list of country names that start with the partial query.
        Useful for the autocomplete feature.
        """
        if not partial_query:
            return []
            
        query = partial_query.lower()
        # Find all names that start with the query
        return [name for name in self.country_names if name.lower().startswith(query)]
