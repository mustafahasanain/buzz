import frappe
from frappe.tests.utils import FrappeTestCase


class TestBuzzWhatsAppTemplate(FrappeTestCase):
	def test_rejects_invalid_jinja(self):
		doc = frappe.get_doc(
			{
				"doctype": "Buzz WhatsApp Template",
				"template_name": "Invalid Jinja WhatsApp Template",
				"template_type": "Ticket",
				"message": "Hello {{ doc.name",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			doc.insert()

	def test_accepts_valid_jinja(self):
		doc = frappe.get_doc(
			{
				"doctype": "Buzz WhatsApp Template",
				"template_name": "Valid Jinja WhatsApp Template",
				"template_type": "Ticket",
				"message": "Hello {{ doc.attendee_name }}",
			}
		).insert()

		self.assertEqual(doc.name, "Valid Jinja WhatsApp Template")
