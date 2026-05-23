// Copyright (c) 2026, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Evaluation", {
	refresh(frm) {
		frm.set_query("booking", () => {
			const filters = {};
			if (frm.doc.event) {
				filters.event = frm.doc.event;
			}
			return { filters };
		});

		frm.set_query("ticket", () => {
			const filters = {};
			if (frm.doc.event) {
				filters.event = frm.doc.event;
			}
			if (frm.doc.booking) {
				filters.booking = frm.doc.booking;
			}
			return { filters };
		});
	},

	ticket(frm) {
		if (!frm.doc.ticket) {
			return;
		}

		frappe.db.get_value(
			"Event Ticket",
			frm.doc.ticket,
			["event", "booking", "attendee_name", "attendee_email", "attendee_phone"],
			(ticket) => {
				if (!ticket) {
					return;
				}

				frm.set_value({
					event: frm.doc.event || ticket.event,
					booking: frm.doc.booking || ticket.booking,
					customer_name: frm.doc.customer_name || ticket.attendee_name,
					customer_email: frm.doc.customer_email || ticket.attendee_email,
					customer_phone: frm.doc.customer_phone || ticket.attendee_phone,
				});
			}
		);
	},

	booking(frm) {
		if (!frm.doc.booking) {
			return;
		}

		frappe.db.get_value("Event Booking", frm.doc.booking, ["event", "user"], (booking) => {
			if (!booking) {
				return;
			}

			frm.set_value({
				event: frm.doc.event || booking.event,
				customer: frm.doc.customer || booking.user,
			});
		});
	},

	customer(frm) {
		if (!frm.doc.customer) {
			return;
		}

		frappe.db.get_value(
			"User",
			frm.doc.customer,
			["full_name", "email", "mobile_no", "phone"],
			(customer) => {
				if (!customer) {
					return;
				}

				frm.set_value({
					customer_name: frm.doc.customer_name || customer.full_name,
					customer_email: frm.doc.customer_email || customer.email,
					customer_phone: frm.doc.customer_phone || customer.mobile_no || customer.phone,
				});
			}
		);
	},
});
