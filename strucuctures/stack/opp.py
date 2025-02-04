class Car:
    def __init__(self, model:str, kms:int):
        self.model = model
        self.kms = kms

    def __repr__(self):
        return f'model: {self.model}, kms: {self.kms}'
    
    def broom(self, distance:int):
        self.kms += distance





#testing
daily = Car('Mustang', 0)
print(daily.model)
print(daily.kms)
brom = daily.broom(100)
print(daily.kms)
print(daily.__repr__)