frappe.ready(function () {
	// Frappe's Phone control defaults its country to `frappe.sys_defaults.country`,
	// falling back to a hardcoded "India". On the public portal `sys_defaults` isn't
	// populated for guests, so the fallback always wins. Force Iraq (+964) instead.
	const defaultCountry = "Iraq";

	// Covers any later refresh()/set_default_country() calls on the control.
	frappe.sys_defaults = frappe.sys_defaults || {};
	if (!frappe.sys_defaults.country) {
		frappe.sys_defaults.country = defaultCountry;
	}

	setDefaultPhoneCountry("customer_phone", defaultCountry);

	// The Phone control builds asynchronously (it fetches country codes), so poll
	// briefly until the picker is ready, then switch the default country.
	function setDefaultPhoneCountry(fieldname, country, attempt = 0) {
		const field = frappe.web_form?.fields_dict?.[fieldname];
		const isReady =
			field && field.country_code_picker && field.country_codes?.[country];

		if (!isReady) {
			if (attempt < 50) {
				setTimeout(() => setDefaultPhoneCountry(fieldname, country, attempt + 1), 100);
			}
			return;
		}

		// Don't override anything the user has already typed.
		if (!field.get_value()) {
			field.country_code_picker.on_change(country, false);
		}
	}
});
