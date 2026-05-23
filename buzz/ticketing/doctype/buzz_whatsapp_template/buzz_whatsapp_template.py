import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template


class BuzzWhatsAppTemplate(Document):
	def validate(self):
		if self.message:
			try:
				validate_template(self.message)
			except Exception as e:
				frappe.throw(f"Invalid Jinja template in Message Body: {e}")
