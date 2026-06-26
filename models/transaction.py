class Transaction:
    def __init__(self, id_txn=None, description=None, amount=None, type_txn=None,
                 id_user=None, id_category=None, dcompdate=None):
        
        self.id_txn = id_txn
        self.description = description
        self.amount = amount
        self.type_txn = type_txn  # ingreso o gasto
        self.id_user = id_user
        self.id_category = id_category
        self.dcompdate = dcompdate

    def __str__(self):
        return f"Transaction({self.id_txn}, {self.description}, {self.amount}, {self.type_txn}, Cat: {self.id_category})"

    def is_income(self):
        return self.type_txn == 'ingreso'

    def is_expense(self):
        return self.type_txn == 'gasto'

    def to_dict(self):
        return {
            "id_txn": self.id_txn,
            "description": self.description,
            "amount": self.amount,
            "type_txn": self.type_txn,
            "id_user": self.id_user,
            "id_category": self.id_category
        }