# Copyright (c) 2025, BWH Studios and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from buzz.utils import generate_qr_code_file, make_qr_image

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class TestEventTicketEmail(FrappeTestCase):
	"""Tests for Event Ticket email sending with template fallback logic."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})
		cls.test_event.ticket_email_template = None
		cls.test_event.save()

		# Clear global settings
		settings = frappe.get_doc("Buzz Settings")
		settings.default_ticket_email_template = None
		settings.save()

	def setUp(self):
		self.test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": self.test_event.name,
				"title": "Email Test Ticket",
				"price": 100,
			}
		).insert()

		self.test_ticket = frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"event": self.test_event.name,
				"ticket_type": self.test_ticket_type.name,
				"attendee_name": "Test Attendee",
				"attendee_email": "test@example.com",
				"attendee_phone": "0770 123 4567",
			}
		).insert()

	def tearDown(self):
		frappe.delete_doc("Event Ticket", self.test_ticket.name, force=True)
		frappe.delete_doc("Event Ticket Type", self.test_ticket_type.name, force=True)

	def _create_template(self, name, subject_prefix):
		if frappe.db.exists("Email Template", name):
			frappe.delete_doc("Email Template", name, force=True)
		return frappe.get_doc(
			{
				"doctype": "Email Template",
				"name": name,
				"subject": f"{subject_prefix} - {{{{ event_title }}}}",
				"response": f"<p>{subject_prefix} content</p>",
			}
		).insert()

	@patch("frappe.sendmail")
	def test_uses_event_template_when_set(self, mock_sendmail):
		template = self._create_template("Event Ticket Template", "EVENT")
		try:
			self.test_event.ticket_email_template = template.name
			self.test_event.save()

			self.test_ticket.send_ticket_email(now=True)

			mock_sendmail.assert_called_once()
			self.assertIn("EVENT", mock_sendmail.call_args[1]["subject"])
		finally:
			self.test_event.ticket_email_template = None
			self.test_event.save()
			frappe.delete_doc("Email Template", template.name, force=True)

	@patch("frappe.sendmail")
	def test_falls_back_to_global_template(self, mock_sendmail):
		template = self._create_template("Global Ticket Template", "GLOBAL")
		try:
			self.test_event.ticket_email_template = None
			self.test_event.save()

			settings = frappe.get_doc("Buzz Settings")
			settings.default_ticket_email_template = template.name
			settings.save()

			self.test_ticket.send_ticket_email(now=True)

			mock_sendmail.assert_called_once()
			self.assertIn("GLOBAL", mock_sendmail.call_args[1]["subject"])
		finally:
			settings.default_ticket_email_template = None
			settings.save()
			frappe.delete_doc("Email Template", template.name, force=True)

	@patch("frappe.sendmail")
	def test_event_template_takes_precedence(self, mock_sendmail):
		event_template = self._create_template("Event Template", "EVENT")
		global_template = self._create_template("Global Template", "GLOBAL")
		try:
			self.test_event.ticket_email_template = event_template.name
			self.test_event.save()

			settings = frappe.get_doc("Buzz Settings")
			settings.default_ticket_email_template = global_template.name
			settings.save()

			self.test_ticket.send_ticket_email(now=True)

			mock_sendmail.assert_called_once()
			self.assertIn("EVENT", mock_sendmail.call_args[1]["subject"])
			self.assertNotIn("GLOBAL", mock_sendmail.call_args[1]["subject"])
		finally:
			self.test_event.ticket_email_template = None
			self.test_event.save()
			settings.default_ticket_email_template = None
			settings.save()
			frappe.delete_doc("Email Template", event_template.name, force=True)
			frappe.delete_doc("Email Template", global_template.name, force=True)

	@patch("frappe.sendmail")
	def test_uses_inline_template_when_none_configured(self, mock_sendmail):
		self.test_event.ticket_email_template = None
		self.test_event.save()

		settings = frappe.get_doc("Buzz Settings")
		settings.default_ticket_email_template = None
		settings.save()

		self.test_ticket.send_ticket_email(now=True)

		mock_sendmail.assert_called_once()
		self.assertEqual(mock_sendmail.call_args[1]["template"], "ticket")


class TestEventTicketWhatsApp(FrappeTestCase):
	"""Tests for Event Ticket WhatsApp sending via UltraMSG."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

	def setUp(self):
		self.test_event.send_ticket_whatsapp = 0
		self.test_event.ticket_whatsapp_message = None
		self.test_event.save()

		settings = frappe.get_doc("Buzz Settings")
		settings.ultramsg_api_url = "https://api.ultramsg.com/instance12345"
		settings.ultramsg_token = "test-token"
		settings.default_whatsapp_country_code = "964"
		settings.default_ticket_whatsapp_message = None
		settings.save()

		self.test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": self.test_event.name,
				"title": "WhatsApp Test Ticket",
				"price": 100,
			}
		).insert()

		self.test_ticket = frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"event": self.test_event.name,
				"ticket_type": self.test_ticket_type.name,
				"first_name": "WhatsApp",
				"last_name": "Attendee",
				"attendee_email": "whatsapp@example.com",
				"attendee_phone": "0770 123 4567",
			}
		).insert()

	def tearDown(self):
		frappe.delete_doc("Event Ticket", self.test_ticket.name, force=True)
		frappe.delete_doc("Event Ticket Type", self.test_ticket_type.name, force=True)
		self.test_event.send_ticket_whatsapp = 0
		self.test_event.ticket_whatsapp_message = None
		self.test_event.save()

		settings = frappe.get_doc("Buzz Settings")
		settings.ultramsg_api_url = None
		settings.ultramsg_token = None
		settings.default_whatsapp_country_code = None
		settings.default_ticket_whatsapp_message = None
		settings.save()

	@patch("buzz.integrations.ultramsg.requests.post")
	def test_sends_whatsapp_when_enabled(self, mock_post):
		mock_post.return_value.json.return_value = {"sent": "true", "id": "msg-1"}
		self.test_event.send_ticket_whatsapp = 1
		self.test_event.ticket_whatsapp_message = "Ticket {{ doc.name }} for {{ event_title }}"
		self.test_event.save()

		result = self.test_ticket.send_ticket_whatsapp()

		self.assertTrue(result["success"])
		mock_post.assert_called_once()
		endpoint = mock_post.call_args[0][0]
		payload = mock_post.call_args[1]["data"]
		self.assertEqual(endpoint, "https://api.ultramsg.com/instance12345/messages/chat")
		self.assertEqual(payload["to"], "9647701234567")
		self.assertEqual(payload["token"], "test-token")
		self.assertIn(self.test_ticket.name, payload["body"])

	@patch("buzz.integrations.ultramsg.requests.post")
	def test_skips_whatsapp_when_disabled(self, mock_post):
		result = self.test_ticket.send_ticket_whatsapp()

		self.assertIsNone(result)
		mock_post.assert_not_called()


class TestQRCodeGeneration(FrappeTestCase):
	"""Tests for QR code generation utility."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

	def test_make_qr_image_returns_png_bytes(self):
		"""QR image generation should return valid PNG bytes."""
		result = make_qr_image("test-data-123")

		self.assertIsInstance(result, bytes)
		# PNG magic bytes
		self.assertTrue(result.startswith(b"\x89PNG"))

	def test_generate_qr_code_file_creates_attachment(self):
		"""QR code file should be created and attached to document."""
		file_url = generate_qr_code_file(
			doc=self.test_event,
			data="test-qr-data",
			field_name="qr_code",
			file_prefix="test-qr",
		)

		self.assertIsNotNone(file_url)
		self.assertTrue(file_url.endswith(".png"))

		# Verify file exists in File doctype
		file_doc = frappe.get_doc("File", {"file_url": file_url})
		self.assertEqual(file_doc.attached_to_doctype, "Buzz Event")
		self.assertEqual(str(file_doc.attached_to_name), str(self.test_event.name))

		# Cleanup
		file_doc.delete()
