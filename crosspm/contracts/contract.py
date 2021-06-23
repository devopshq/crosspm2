class Contract:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __hash__(self):
        return hash((self.name, self.values))

    def __str__(self):
        return "{}{}".format(self.name, self.values)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name and (set(self.values) & set(other.values))

    def __ne__(self, other):
        return not (self == other)


class PackageContracts:
    def __init__(self, contracts):
        self._contracts = contracts

    def __getitem__(self, key):
        for c in self._contracts:
            if c.name == key.name:
                return c

        return None

    def is_lower(self, contract):
        c = self[contract]
        return c and c.value < contract.value

    def is_equal(self, contract):
        c = self[contract]
        return c and c.value == contract.value
