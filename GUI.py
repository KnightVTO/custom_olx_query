import sys
import time
import requests
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QTreeWidget,
    QTreeWidgetItem, QScrollArea, QFrame, QSizePolicy,
    QProgressBar
)
from PyQt5.QtCore import Qt, QObject
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from custom_widgets import *


def build_olx_url(
    brand=None,
    county=None,
    page=1,
    types=None,
    price_from=None,
    price_to=None,
    year_from=None,
    year_to=None,
    mileage_to=None,
    engine_cc_from=None,
    engine_cc_to=None,
    currency="EUR",
    features=None
):
    base_url = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/motociclete/"
    if brand:
        base_url += f"{brand.lower().strip()}/"

    if county:
        base_url += f"{county.lower().strip()}/"

    params = {"currency": currency, "page": page}

    if price_from:
        params["search[filter_float_price:from]"] = price_from
    if price_to:
        params["search[filter_float_price:to]"] = price_to
    if year_from:
        params["search[filter_float_year:from]"] = year_from
    if year_to:
        params["search[filter_float_year:to]"] = year_to
    if mileage_to:
        params["search[filter_float_rulaj_pana:to]"] = mileage_to
    if engine_cc_from:
        params["search[filter_float_enginesize:from]"] = engine_cc_from
    if engine_cc_to:
        params["search[filter_float_enginesize:to]"] = engine_cc_to
    if types:
        for i, t in enumerate(types):
            params[f"search[filter_enum_car_body][{i}]"] = t
    if features:
        for i, t in enumerate(features):
            params[f"search[filter_enum_features][{i}]"] = t

    return base_url + "?" + urlencode(params, doseq=True)

def scrape_olx_motorcycles(
    brand=None,
    county=None,
    types=None,
    price_from=None,
    price_to=None,
    year_from=None,
    year_to=None,
    mileage_to=None,
    engine_cc_from=None,
    engine_cc_to=None,
    features=None,
    max_results=50
):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    page = 1
    duplicate = False

    while len(results) < max_results:
        url = build_olx_url(
            brand=brand,
            county=county,
            page=page,
            types=types,
            price_from=price_from,
            price_to=price_to,
            year_from=year_from,
            year_to=year_to,
            mileage_to=mileage_to,
            engine_cc_from=engine_cc_from,
            engine_cc_to=engine_cc_to,
            features=features
        )
        print(f"Fetching: {url}\n")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        results_exist = soup.select_one("span[data-testid='total-count']")
        if results_exist.text.strip() == "Am găsit  0 rezultate pentru tine":
            return []

        listings = soup.select('div[data-cy="l-card"]')
        if not listings:
            break

        result_counter = 0

        for listing in listings:
            result_counter += 1
            if len(results) >= max_results:
                break
            title_elem = listing.select_one("h4")
            price_elem = listing.select_one("p[data-testid='ad-price']")
            link_elem = listing.select_one("a")["href"]

            title = str(result_counter) + ". " + title_elem.text.strip() if title_elem else "No title"
            price = price_elem.text.strip() if price_elem else "No price"

            if "autovit" not in link_elem:
                link = "https://olx.ro"+link_elem if link_elem else "No link"
            else:
                link = link_elem if link_elem else "No link"


            item = (title, price, link)
            if item not in results:
                results.append((title, price, link))
            else:
                duplicate = True
                break

        page += 1
        if page > 5 or duplicate:  # Limit to 5 pages for testing
            break
        time.sleep(1)

    return results

class Worker(QObject):
    pass

class OLXScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motorcycle OLX Scraper")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.filters_groups_layout = QHBoxLayout()
        self.filters_groups_counter = 0

        with open("style.css", "r") as style_file:
            style = style_file.read()
            self.setStyleSheet(style)

        # Brand selection
        self.filter_group_0 = FilterGroup(self.filters_groups_counter)
        self.filter_group_0.remove_filter_button.clicked.connect(lambda: self.remove_filter_group(self.filter_group_0.group_id))
        self.all_filter_groups = [self.filter_group_0]
        self.filters_groups_layout.addWidget(self.filter_group_0)
        self.filters_groups_counter += 1

        self.add_new_filter_group_button = QPushButton("Add new filters")
        self.add_new_filter_group_button.clicked.connect(self.add_new_filter_group)
        self.filters_groups_layout.addWidget(self.add_new_filter_group_button)

        self.filters_groups_layout.setStretch(0, 1)
        self.filters_groups_layout.setStretch(1, 1)
        
        self.main_layout.addLayout(self.filters_groups_layout)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("Search")
        self.search_button.clicked.connect(self.run_search)

        self.search_progress = 0
        self.search_progress_bar = QProgressBar()
        self.search_progress_bar.setTextVisible(True)
        self.search_progress_bar.setRange(0, 100)
        self.search_progress_bar.setStyleSheet('''
                                               QProgressBar {
                                                    text-align: center;
                                                    text-color: black
                                               }''')

        self.search_button_layout = QHBoxLayout()
        self.search_button_layout.addWidget(self.search_button,        1)
        self.search_button_layout.addWidget(self.search_progress_bar, 10)

        self.main_layout.addLayout(self.search_button_layout)

        # Table for results
        self.results_table = QTreeWidget()
        self.results_table.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.results_table.setColumnCount(5)
        self.results_table.setHeaderLabels(["Result", "Price", "URL", "Browser button", ""])
        self.results_table.setColumnWidth(0, 300)
        self.results_table.setColumnWidth(1, 100)
        self.results_table.setColumnWidth(2, 550)
        self.main_layout.addWidget(QLabel("Results:"))
        self.main_layout.addWidget(self.results_table)

        self.setLayout(self.main_layout)

        self.results_table.itemDoubleClicked.connect(self.open_in_browser_double_click)

    def add_new_filter_group(self):        
        new_filter_group_name = "filter_group_"+str(self.filters_groups_counter)
        setattr(self, new_filter_group_name, FilterGroup(self.filters_groups_counter))
        new_filter_group = getattr(self, new_filter_group_name)

        self.filters_groups_layout.removeWidget(self.add_new_filter_group_button)
        self.add_new_filter_group_button.setParent(None)

        self.filters_groups_layout.addWidget(new_filter_group)
        self.all_filter_groups.append(new_filter_group)
        new_filter_group.remove_filter_button.clicked.connect(lambda: self.remove_filter_group(new_filter_group.group_id))

        self.filters_groups_counter += 1

        for i in range(self.filters_groups_counter):
            self.filters_groups_layout.setStretch(i, 1)

        if self.filters_groups_counter != 5:
            self.filters_groups_layout.addWidget(self.add_new_filter_group_button)
            self.filters_groups_layout.setStretch(self.filters_groups_counter, 1)

    def remove_filter_group(self, group_id):
        # Visually remove the filter group
        self.filters_groups_layout.removeWidget(self.all_filter_groups[group_id])
        self.all_filter_groups[group_id].setParent(None)
        self.filters_groups_counter -= 1

        # Rearrange groups in list
        self.all_filter_groups.pop(group_id)

        # Reassign group IDs
        for group in self.all_filter_groups:
            if group_id < group.group_id:
                group.group_id -= 1
        
        if self.filters_groups_counter == 4:
            self.filters_groups_layout.addWidget(self.add_new_filter_group_button)
            self.filters_groups_layout.setStretch(self.filters_groups_counter, 1)

    def run_search(self):
        self.results_table.clear()
        self.search_progress_bar.setValue(0)

        for filter_group in self.all_filter_groups:
            brand = filter_group.brand_combo.currentText().strip()

            # Extract filters from fields
            filters = {
                "county": filter_group.county_combo.currentText().strip() or None,
                "price_from": filter_group.price_from_edit.text().strip() or None,
                "price_to": filter_group.price_to_edit.text().strip() or None,
                "year_from": filter_group.year_from_edit.text().strip() or None,
                "year_to": filter_group.year_to_edit.text().strip() or None,
                "mileage_to": filter_group.mileage_to_edit.text().strip() or None,
                "engine_cc_from": filter_group.engine_cc_from_edit.text().strip() or None,
                "engine_cc_to": filter_group.engine_cc_to_edit.text().strip() or None,
                "types": [t.strip().lower() for t in filter_group.types_edit.text().split(",") if t.strip()],
                "features": [f.strip().lower() for f in filter_group.features_edit.text().split(",") if f.strip()]
            }

            if not filters["types"]:
                filters["types"] = None
            try:
                results = scrape_olx_motorcycles(
                    brand=brand,
                    county=filters["county"],
                    types=filters["types"],
                    price_from=filters["price_from"],
                    price_to=filters["price_to"],
                    year_from=filters["year_from"],
                    year_to=filters["year_to"],
                    mileage_to=filters["mileage_to"],
                    engine_cc_from=filters["engine_cc_from"],
                    engine_cc_to=filters["engine_cc_to"],
                    features=filters["features"],
                    max_results=50
                )
            except Exception as e:
                QMessageBox.critical(filter_group, "Error", f"Failed to fetch results:\n{e}")
                return

            # filter_group.results_table.setRowCount(len(results))
            if len(results) == 0:
                results = scrape_olx_motorcycles(
                    brand=brand,
                    county=filters["county"]+"-judet",
                    types=filters["types"],
                    price_from=filters["price_from"],
                    price_to=filters["price_to"],
                    year_from=filters["year_from"],
                    year_to=filters["year_to"],
                    mileage_to=filters["mileage_to"],
                    engine_cc_from=filters["engine_cc_from"],
                    engine_cc_to=filters["engine_cc_to"],
                    features=filters["features"],
                    max_results=50
                )
                if len(results) == 0:
                    tree_item = QTreeWidgetItem(self.results_table)
                    tree_item.setText(0, brand + " " + filters["county"] + " - no results")
                    continue

            parent_item = QTreeWidgetItem(self.results_table)

            if filters["county"] != None:
                parent_item.setText(0, brand + " - " + filters["county"])
            else:
                parent_item.setText(0, brand)

            for brand, (title, price, link) in enumerate(results):
                current_item = QTreeWidgetItem(parent_item)
                current_item.setText(0, title)
                current_item.setText(1, price)
                current_item.setText(2, link)
                self.results_table.setItemWidget(current_item, 3, self.create_browser_button(link))

        self.search_progress_bar.setValue(100)

    def create_browser_button(self, link):
        button = QPushButton("Open in Browser")
        button.clicked.connect(lambda: self.open_in_browser(link))

        return button

    def open_in_browser(self, link):
        webbrowser.open(link)

    def open_in_browser_double_click(self):
        link = self.results_table.currentItem().text(2)
        self.open_in_browser(link)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OLXScraperApp()
    window.show()
    sys.exit(app.exec_())
