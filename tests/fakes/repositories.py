from domain.models.customer import Customer
from domain.models.pre_sale_customer import PreSaleCustomer
from domain.models.waitlist_lead import WaitlistLead


def _customer_status(customer):
    if isinstance(customer, Customer):
        return customer.status
    return customer.get("status")


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

    def list_active(self):
        return [
            customer
            for customer in self._by_phone.values()
            if _customer_status(customer) == "active"
        ]

    def list_all(self):
        return list(self._by_phone.values())

    def seed(self, customer_dict):
        self._by_phone[customer_dict["phone"]] = dict(customer_dict)


class FakePreSaleCustomerRepository:
    def __init__(self):
        self._by_email = {}
        self.save_calls = 0
        self.delete_calls = 0

    def get_by_email(self, email):
        return self._by_email.get(email)

    def get_by_whatsapp(self, whatsapp):
        for lead in self._by_email.values():
            if isinstance(lead, dict):
                if lead.get("whatsapp") == whatsapp:
                    return dict(lead)
            elif getattr(lead, "whatsapp", None) == whatsapp:
                return lead
        return None

    def save(self, customer):
        self.save_calls += 1
        if isinstance(customer, PreSaleCustomer):
            self._by_email[customer.email] = customer.to_dict()
        else:
            self._by_email[customer["email"]] = dict(customer)

    def delete(self, email):
        self.delete_calls += 1
        self._by_email.pop(email, None)

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


class FakeWaitlistRepository:
    def __init__(self):
        self._by_phone = {}
        self.save_calls = 0
        self.update_calls = 0

    def get_by_phone(self, phone):
        lead = self._by_phone.get(phone)
        return dict(lead) if lead is not None else None

    def save(self, lead):
        self.save_calls += 1
        if isinstance(lead, WaitlistLead):
            payload = lead.to_dict()
        else:
            payload = dict(lead)
        self._by_phone[payload["phone"]] = payload

    def update(self, lead):
        self.update_calls += 1
        if isinstance(lead, WaitlistLead):
            payload = lead.to_dict()
        else:
            payload = dict(lead)
        self._by_phone[payload["phone"]] = payload

    def list_all(self):
        return [dict(lead) for lead in self._by_phone.values()]

    def seed(self, lead_dict):
        self._by_phone[lead_dict["phone"]] = dict(lead_dict)
