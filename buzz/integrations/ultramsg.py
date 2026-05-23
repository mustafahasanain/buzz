import re

import frappe
import requests
from frappe import _


def get_ultramsg_settings():
	settings = frappe.get_single("Buzz Settings")
	api_url = (settings.ultramsg_api_url or "").strip().rstrip("/")
	token = settings.get_password("ultramsg_token")

	if (not api_url or not token) and frappe.db.table_exists("WP Settings"):
		wp_settings = frappe.get_single("WP Settings")
		api_url = api_url or (wp_settings.ultramsg_api_url or "").strip().rstrip("/")
		token = token or wp_settings.get_password("ultramsg_token")

	if not api_url or not token:
		frappe.throw(_("UltraMSG credentials are not configured in Buzz Settings or WP Settings"))

	return api_url, token


def normalize_phone(phone):
	"""Normalize local phone numbers using the Buzz Settings default country code."""
	if not phone:
		return phone

	clean = re.sub(r"[\s().-]+", "", phone.strip())
	country_code = (
		frappe.get_cached_value("Buzz Settings", "Buzz Settings", "default_whatsapp_country_code")
		or ""
	).strip()

	if not country_code and frappe.db.table_exists("WP Settings"):
		country_code = (
			frappe.get_cached_value("WP Settings", "WP Settings", "default_country_code") or ""
		).strip()

	if not country_code:
		return clean.lstrip("+")

	country_code = country_code.lstrip("+")

	if clean.startswith("+"):
		clean = clean[1:]

	if clean.startswith(country_code):
		return clean

	if clean.startswith("0"):
		return country_code + clean[1:]

	return clean


def send_whatsapp(phone, message_body):
	"""Send a WhatsApp text message via UltraMSG."""
	api_url, token = get_ultramsg_settings()
	normalized_phone = normalize_phone(phone)

	endpoint = f"{api_url}/messages/chat"
	payload = {"token": token, "to": normalized_phone, "body": message_body}
	return send_ultramsg_request(endpoint, payload)


def send_whatsapp_image(phone, image, caption=None):
	"""Send a WhatsApp image message via UltraMSG."""
	api_url, token = get_ultramsg_settings()
	normalized_phone = normalize_phone(phone)

	endpoint = f"{api_url}/messages/image"
	payload = {"token": token, "to": normalized_phone, "image": image}
	if caption:
		payload["caption"] = caption

	return send_ultramsg_request(endpoint, payload)


def send_ultramsg_request(endpoint, payload):
	try:
		response = requests.post(endpoint, data=payload, timeout=15)
		result = response.json()
	except requests.exceptions.Timeout:
		return {"success": False, "error": "Request timed out"}
	except Exception as e:
		return {"success": False, "error": str(e)}

	if result.get("error"):
		return {"success": False, "error": result.get("error")}

	if str(result.get("sent", "")).lower() == "false":
		return {"success": False, "error": result.get("message") or "UltraMSG rejected the message"}

	return {"success": True, "result": result}
