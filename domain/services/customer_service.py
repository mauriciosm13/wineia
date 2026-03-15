from domain.models.customer import Customer

class CustomerService:

    def __init__(self, repository):
        self.repository = repository

    def create_customer(self, phone, name, status, plan):

        existing = self.repository.get_by_phone(phone)

        if existing:
            return existing

        customer = Customer(phone, name, status, plan)

        self.repository.save(customer)

        return customer.to_dict()