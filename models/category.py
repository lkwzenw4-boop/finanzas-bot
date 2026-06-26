class Category:
    def __init__(self, id_category=None, description=None, id_subcategory=None, type_category=None, dcompdate=None):
        self.id_category = id_category
        self.description = description
        self.id_subcategory = id_subcategory # Si es None, es categoría padre; si tiene valor, es subcategoría
        self.type_category = type_category
        self.dcompdate = dcompdate

    def __str__(self):
        return f"Category({self.id_category}, {self.description}, Type: {self.type_category})"

    def is_parent(self):
        return self.id_subcategory is None

    def to_dict(self):
        return {
            "id_category": self.id_category,
            "description": self.description,
            "id_subcategory": self.id_subcategory,
            "type_category": self.type_category
        }