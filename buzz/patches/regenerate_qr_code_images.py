import frappe

from buzz.utils import generate_qr_code_file


def execute():
	for ticket_name in frappe.db.get_all("Event Ticket", pluck="name"):
		ticket = frappe.get_doc("Event Ticket", ticket_name)
		file_url = generate_qr_code_file(
			doc=ticket,
			data=ticket.name,
			file_prefix="ticket-qr-code",
		)
		ticket.db_set("qr_code", file_url, update_modified=False)

	for campaign_name in frappe.db.get_all("Buzz Campaign", pluck="name"):
		campaign = frappe.get_doc("Buzz Campaign", campaign_name)
		register_url = f"{frappe.utils.get_url()}/dashboard/register-interest/{campaign.name}"
		file_url = generate_qr_code_file(
			doc=campaign,
			data=register_url,
			field_name="qr_code",
			file_prefix="campaign-qr-code",
		)
		campaign.db_set("qr_code", file_url, update_modified=False)
