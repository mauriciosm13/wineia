from domain.models.pre_sale_customer import PreSaleCustomer


class PreSaleCustomerService:

    def __init__(self, repository):
        self.repository = repository

    def create_customer(self, name, email, whatsapp, preferences):
        existing = self.repository.get_by_email(email)

        if existing:
            return dict(existing)

        customer = PreSaleCustomer(name, email, whatsapp, preferences)

        self.repository.save(customer)

        return customer.to_dict()
