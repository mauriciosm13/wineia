from domain.models.customer import Customer
from domain.models.pre_sale_customer import PreSaleCustomer


class FakeCustomerRepository:
    def __init__(self):
        self._by_phone = {}
        self.save_calls = 0
        self.update_calls = 0

    def get_by_phone(self, phone):
        return self._by_phone.get(phone)

    def save(self, customer):
        self.save_calls += 1
        if isinstance(customer, Customer):
            self._by_phone[customer.phone] = customer
        else:
            self._by_phone[customer["phone"]] = customer

    def update(self, customer):
        self.update_calls += 1
        phone = customer["phone"] if isinstance(customer, dict) else customer.phone
        self._by_phone[phone] = customer

    def seed(self, customer_dict):
        self._by_phone[customer_dict["phone"]] = dict(customer_dict)


class FakePreSaleCustomerRepository:
    def __init__(self):
        self._by_email = {}
        self.save_calls = 0

    def get_by_email(self, email):
        return self._by_email.get(email)

    def save(self, customer):
        self.save_calls += 1
        if isinstance(customer, PreSaleCustomer):
            self._by_email[customer.email] = customer.to_dict()
        else:
            self._by_email[customer["email"]] = dict(customer)

    def seed(self, customer_dict):
        self._by_email[customer_dict["email"]] = dict(customer_dict)


class FakeRecommendationContentRepository:
    def __init__(self):
        self.saved = []
        self.save_content_calls = 0

    def save_content(self, content):
        self.save_content_calls += 1
        self.saved.append(content)

    def list_active_contents(self):
        return list(self.saved)
