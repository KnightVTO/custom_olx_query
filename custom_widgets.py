from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QFrame, QSizePolicy, QScrollArea)


class LabelTextPair(QHBoxLayout):
    def __init__(self, label, text_widget):
        super().__init__()
        self.addWidget(QLabel(label))
        self.addWidget(text_widget)
        self.addStretch()

class FilterGroup(QWidget):
    def __init__(self, group_id, parent=None):
        super().__init__(parent)
 
        self.main_layout = QVBoxLayout(self)
        self.group_id = group_id

        self.brand_combo = QComboBox()
        self.brand_combo.addItems([
            "", "Aprilia", "Yamaha", "Honda", "Suzuki", "Kawasaki", "Ducati", "BMW"
        ])
        self.brand_combo.setCurrentIndex(3)
        self.brand_layout = LabelTextPair("Brand:", self.brand_combo)

        self.county_combo = QComboBox()
        self.county_combo.addItems([
            "", "Alba", "Arad", "Arges", "Bacau", "Bihor", "Bistrita-Nasaud",
            "Botosani", "Braila", "Brasov", "Bucuresti", "Buzau", "Calarasi",
            "Caras-Severin", "Cluj", "Constanta", "Covasna", "Dambovita",
            "Dolj", "Galati", "Giurgiu", "Gorj", "Harghita", "Hunedoara",
            "Ialomita", "Iasi", "Ilfov", "Maramures", "Mehedinti",
            "Mures", "Neamt", "Olt", "Prahova", "Salaj", "Satu Mare",
            "Sibiu", "Suceava", "Teleorman", "Timis", "Tulcea",
            "Valcea", "Vaslui", "Vrancea"
        ])
        self.county_combo.setCurrentIndex(1)
        self.county_layout = LabelTextPair("Judet:", self.county_combo)

        # Filters section
        self.filter_form = QVBoxLayout()

        self.price_from_edit = QLineEdit(); self.price_from_edit.setFixedHeight(30)
        self.price_from_edit.setText("1500")
        self.price_from_pair = LabelTextPair("Price From:", self.price_from_edit)

        self.price_to_edit = QLineEdit(); self.price_to_edit.setFixedHeight(30)
        self.price_to_edit.setText("3100")
        self.price_to_pair = LabelTextPair("Price To:", self.price_to_edit)
        
        self.year_from_edit = QLineEdit(); self.year_from_edit.setFixedHeight(30)
        self.year_from_edit.setText("2006")
        self.year_from_pair = LabelTextPair("Year From:", self.year_from_edit)
        
        self.year_to_edit = QLineEdit(); self.year_to_edit.setFixedHeight(30)
        self.year_to_edit.setText("2025")
        self.year_to_pair = LabelTextPair("Year To:", self.year_to_edit)

        self.mileage_to_edit = QLineEdit(); self.mileage_to_edit.setFixedHeight(30)
        self.mileage_to_edit.setText("50000")
        self.mileage_to_pair = LabelTextPair("Max Mileage:", self.mileage_to_edit)

        self.engine_cc_from_edit = QLineEdit(); self.engine_cc_from_edit.setFixedHeight(30)
        self.engine_cc_from_edit.setText("250")
        self.engine_cc_from_pair = LabelTextPair("Engine CC From:", self.engine_cc_from_edit)

        self.engine_cc_to_edit = QLineEdit(); self.engine_cc_to_edit.setFixedHeight(30)
        self.engine_cc_to_edit.setText("700")
        self.engine_cc_to_pair = LabelTextPair("Engine CC To:", self.engine_cc_to_edit)

        self.types_edit = QLineEdit(); self.types_edit.setFixedHeight(30)
        self.types_edit.setText("tip-naked,tip-sport,sport-touring")
        self.types_pair = LabelTextPair("Types (comma-separated):", self.types_edit)

        self.features_edit = QLineEdit(); self.features_edit.setFixedHeight(30)
        self.features_edit.setText("ABS")
        self.features_pair = LabelTextPair("Features (comma-separated):", self.features_edit)

        self.filter_form.addLayout(self.brand_layout)
        self.filter_form.addLayout(self.county_layout)
        self.filter_form.addLayout(self.price_from_pair)
        self.filter_form.addLayout(self.price_to_pair)
        self.filter_form.addLayout(self.year_from_pair)
        self.filter_form.addLayout(self.year_to_pair)
        self.filter_form.addLayout(self.mileage_to_pair)
        self.filter_form.addLayout(self.engine_cc_from_pair)
        self.filter_form.addLayout(self.engine_cc_to_pair)
        self.filter_form.addLayout(self.types_pair)
        self.filter_form.addLayout(self.features_pair)
        self.filter_form.addStretch()

        # Add scroll area for filters (optional for many filters)
        self.filter_frame = QFrame()
        self.filter_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.filter_frame.setLayout(self.filter_form)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.filter_frame)
        self.main_layout.addWidget(self.scrollArea)
