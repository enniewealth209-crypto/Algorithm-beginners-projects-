# 🌍 Country Information Lookup System

## 📌 Project Description
This is a Python project that allows users to search for countries and retrieve important information such as:

- Capital city
- Continent
- Population

The system uses a CSV file as a database and implements a **Binary Search Algorithm** for fast searching.

---

## 🚀 Features
- Search for any country
- Displays:
  - Capital
  - Continent
  - Population
- Handles invalid or non-existing countries
- Uses efficient **binary search**
- Reads data from a CSV file

---

## 🛠️ Technologies Used
- Python 🐍
- CSV module (built-in)
- Binary Search Algorithm

---

## 📂 Project Structure
project/
│── main.py
│── countries.csv
│── README.md

---

## ▶️ How to Run the Project

1. Make sure Python is installed
2. Open your project folder in VS Code
3. Run the program: python main.py

4. Enter a country name when prompted

---

## 💡 Example Usage
Enter country name (or exit to quit): Nigeria

Country: Nigeria
Capital: Abuja
Continent: Africa
Population: 242431832

---

## ⚠️ Notes
- Country names must be spelled correctly
- The search is case-insensitive (thanks to `.title()`)

---

## 🧠 How It Works

1. Loads data from `countries.csv`
2. Stores:
   - Country names in a sorted list
   - Country details in a dictionary
3. Uses **Binary Search** to check if the country exists
4. Retrieves and displays the country's data

---

## 📈 Future Improvements
- Add GUI (Graphical User Interface)
- Add fuzzy search (handle misspellings)
- Connect to an API for real-time data
- Add flags and languages

---

## 👨‍💻 Author
Eniola (Harid_joy)

---

## ⭐ Acknowledgment
This project was built as part of learning:
- Data Structures
- Algorithms (Binary Search)
- File Handling in Python


