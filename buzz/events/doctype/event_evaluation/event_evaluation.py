# Copyright (c) 2026, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


RATING_FIELDS = (
	"overall_rating",
	"organization_rating",
	"venue_rating",
	"content_rating",
	"speaker_rating",
	"staff_rating",
	"value_rating",
)


class EventEvaluation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_comments: DF.Text | None
		asked_by: DF.Link | None
		asked_on: DF.Datetime | None
		attended_before: DF.Literal["Yes", "No", "Not Sure"]
		booking: DF.Link | None
		content_rating: DF.Int
		customer: DF.Link | None
		customer_email: DF.Data
		customer_name: DF.Data
		customer_phone: DF.Phone | None
		evaluation_date: DF.Date
		event: DF.Link
		favorite_part: DF.SmallText | None
		how_can_we_improve: DF.SmallText | None
		likelihood_to_recommend: DF.Int
		organization_rating: DF.Int
		overall_rating: DF.Int
		speaker_rating: DF.Int
		staff_rating: DF.Int
		status: DF.Literal["Draft", "Completed", "Needs Follow-up"]
		ticket: DF.Link | None
		topics_for_future: DF.SmallText | None
		value_rating: DF.Int
		venue_rating: DF.Int
		would_attend_again: DF.Literal["Yes", "No", "Maybe"]
		would_recommend: DF.Literal["Yes", "No", "Maybe"]
	# end: auto-generated types

	def before_insert(self):
		if not self.asked_by:
			self.asked_by = frappe.session.user

		if not self.asked_on:
			self.asked_on = frappe.utils.now_datetime()

	def validate(self):
		self.set_customer_details_from_links()
		self.validate_reference_events()
		self.validate_scores()

	def set_customer_details_from_links(self):
		if self.ticket:
			ticket = frappe.db.get_value(
				"Event Ticket",
				self.ticket,
				["event", "booking", "attendee_name", "attendee_email", "attendee_phone"],
				as_dict=True,
			)
			if not ticket:
				frappe.throw(_("Ticket {0} does not exist.").format(self.ticket))

			self.event = self.event or ticket.event
			self.booking = self.booking or ticket.booking
			self.customer_name = self.customer_name or ticket.attendee_name
			self.customer_email = self.customer_email or ticket.attendee_email
			self.customer_phone = self.customer_phone or ticket.attendee_phone

		if self.booking:
			booking = frappe.db.get_value(
				"Event Booking",
				self.booking,
				["event", "user"],
				as_dict=True,
			)
			if not booking:
				frappe.throw(_("Booking {0} does not exist.").format(self.booking))

			self.event = self.event or booking.event
			self.customer = self.customer or booking.user

		if self.customer:
			user = frappe.db.get_value(
				"User",
				self.customer,
				["full_name", "email", "mobile_no", "phone"],
				as_dict=True,
			)
			if not user:
				frappe.throw(_("Customer {0} does not exist.").format(self.customer))

			self.customer_name = self.customer_name or user.full_name
			self.customer_email = self.customer_email or user.email
			self.customer_phone = self.customer_phone or user.mobile_no or user.phone

	def validate_reference_events(self):
		if self.ticket:
			ticket_event, ticket_booking = frappe.db.get_value(
				"Event Ticket", self.ticket, ["event", "booking"]
			)
			if ticket_event and self.event != ticket_event:
				frappe.throw(_("Ticket {0} belongs to a different event.").format(self.ticket))

			if self.booking and ticket_booking and self.booking != ticket_booking:
				frappe.throw(_("Ticket {0} belongs to a different booking.").format(self.ticket))

		if self.booking:
			booking_event = frappe.db.get_value("Event Booking", self.booking, "event")
			if booking_event and self.event != booking_event:
				frappe.throw(_("Booking {0} belongs to a different event.").format(self.booking))

	def validate_scores(self):
		for fieldname in RATING_FIELDS:
			value = self.get(fieldname)
			if value is not None and value != "" and not 1 <= int(value) <= 5:
				label = self.meta.get_label(fieldname)
				frappe.throw(_("{0} must be between 1 and 5.").format(label))

		if self.likelihood_to_recommend not in (None, "") and not 0 <= int(
			self.likelihood_to_recommend
		) <= 10:
			frappe.throw(_("Likelihood to Recommend must be between 0 and 10."))
