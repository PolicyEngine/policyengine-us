from policyengine_us.model_api import *


class vt_ccfap_child_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    defined_for = "vt_ccfap_eligible_child"
    label = "Vermont CCFAP monthly rate for the child before the family share"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=13",
    )

    def formula(person, period, parameters):
        # From 2023-12-17 payment is based on the state rate regardless of the
        # provider's charges. Before then, Vermont paid the lesser of the state
        # rate and the provider's rate, and the child's bill stands in for that.
        # With no bill in the SPM unit the charges are unknown, so nothing caps
        # the state rate. A child whose provider charges nothing for it draws
        # nothing under the earlier rule. The model reads parameters at the
        # start of each month, so all of December 2023 falls under that rule.
        # Source: CCFAP Understanding Payments (Q3 and "Jane Smith" example)
        # https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf
        p = parameters(period).gov.states.vt.dcf.ccfap.rates
        in_care = person("vt_ccfap_in_care", period)
        state_rate = person("vt_ccfap_state_rate", period)
        annual_bill = person("vt_ccfap_child_bill", period) * MONTHS_IN_YEAR
        unit_bill = person.spm_unit.sum(
            person("pre_subsidy_childcare_expenses", period.this_year)
        )
        weekly_rate = where(
            p.pays_above_provider_charge | (unit_bill == 0),
            state_rate,
            min_(state_rate, annual_bill / WEEKS_IN_YEAR),
        )
        return weekly_rate * in_care * WEEKS_IN_YEAR / MONTHS_IN_YEAR
