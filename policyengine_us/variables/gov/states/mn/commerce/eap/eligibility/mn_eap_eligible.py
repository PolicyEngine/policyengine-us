from policyengine_us.model_api import *


class mn_eap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Minnesota EAP Primary Heat eligibility"
    defined_for = StateCode.MN
    reference = (
        # PDF pages 72, 80-81, 84, 88, 126
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=72",
        # PDF pages 74, 82-83, 86, 90, 128
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=74",
        # PDF pages 8-9
        "https://liheapch.acf.gov/docs/2026/state-plans/MN_Plan_2026.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("mn_eap_household_size", period)
        income = spm_unit("mn_eap_countable_income", period)
        limit = spm_unit("mn_eap_income_limit", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        heating_reported = (heating_type != types.UNSPECIFIED) & (
            heating_type != types.NONE
        )
        # A household must be vulnerable to rising energy costs: it pays an
        # energy vendor, or pays for heat through unsubsidized rent. Subsidized
        # housing with heat in rent qualifies only when the household pays
        # electricity, and is ineligible with heat and electricity included.
        # Paying electricity is read from a positive electricity expense, so
        # the $200 minimum for such a household with no electric usage is not
        # modeled.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        vulnerable = (heat_in_rent & ~subsidized) | (
            spm_unit("mn_eap_energy_cost", period) > 0
        )
        # No categorical eligibility or asset test applies. Residency duration,
        # SSNs, dwelling eligibility, institutions, the application deadline
        # and the one-grant-per-year rule are not modeled.
        return (size > 0) & (income <= limit) & heating_reported & vulnerable
