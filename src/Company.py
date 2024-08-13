class Company:
    def __init__(self, name, posta, skd, location, coords, employee_count):
        self.name = name
        self.posta = posta
        self.skd = skd
        self.location = location
        self.count = employee_count
        self.coords = coords
        if coords is not None:
            self.x = coords[0]
            self.y = coords[1]

    def __repr__(self):
        return f"{self.name} - {self.location} {self.skd}"
