// Copyright (c) 2026, BWH Studios and contributors
// For license information, please see license.txt

const TICKET_JINJA_VARIABLES = [
	{ label: __("Attendee Name"), value: "{{ doc.attendee_name }}" },
	{ label: __("First Name"), value: "{{ doc.first_name }}" },
	{ label: __("Last Name"), value: "{{ doc.last_name }}" },
	{ label: __("Ticket ID"), value: "{{ doc.name }}" },
	{ label: __("Booking Ref"), value: "{{ doc.booking }}" },
	{ label: __("Attendee Email"), value: "{{ doc.attendee_email }}" },
	{ label: __("Attendee Phone"), value: "{{ doc.attendee_phone }}" },
	{ label: __("Event Title"), value: "{{ event_title }}" },
	{ label: __("Ticket Type"), value: "{{ ticket_type }}" },
	{ label: __("Event Date"), value: "{{ frappe.format_date(event_doc.start_date) }}" },
	{ label: __("Event Time"), value: "{{ event_doc.start_time }}" },
];

frappe.ui.form.on("Buzz WhatsApp Template", {
	refresh(frm) {
		render_jinja_buttons(frm);
	},
});

function render_jinja_buttons(frm) {
	const field = frm.fields_dict.message;
	if (!field || !field.$wrapper) return;

	field.$wrapper.find(".buzz-jinja-buttons").remove();

	const buttons = TICKET_JINJA_VARIABLES.map(
		(variable) => `
			<button type="button" class="btn btn-xs btn-default buzz-jinja-btn" data-value="${frappe.utils.escape_html(variable.value)}">
				${frappe.utils.escape_html(variable.label)}
			</button>
		`
	).join("");

	const html = `
		<div class="buzz-jinja-buttons mb-2">
			<div class="text-muted small mb-1">${__("Insert Jinja Variable")}</div>
			<div class="flex flex-wrap gap-2">${buttons}</div>
		</div>
	`;

	field.$wrapper.find(".control-input").before(html);
	field.$wrapper.find(".buzz-jinja-btn").on("click", function () {
		insert_jinja_variable(frm, $(this).attr("data-value"));
	});
}

function insert_jinja_variable(frm, variable) {
	const field = frm.fields_dict.message;
	const input = field?.$input?.get(0);
	const current = frm.doc.message || "";

	if (!input || typeof input.selectionStart !== "number") {
		frm.set_value("message", `${current}${current ? " " : ""}${variable}`);
		return;
	}

	const start = input.selectionStart;
	const end = input.selectionEnd;
	const next_value = `${current.slice(0, start)}${variable}${current.slice(end)}`;

	frm.set_value("message", next_value).then(() => {
		input.focus();
		input.setSelectionRange(start + variable.length, start + variable.length);
	});
}
