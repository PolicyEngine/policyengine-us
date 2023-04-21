from policyengine_us.model_api import *


class oh_child_dependent_care_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio senior citizen credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        agi_state_limit = parameters(
            period
        ).gov.states.oh.tax.income.credits.child.agi_state_limit
        age_federal_limit = parameters(
            period
        ).gov.states.oh.tax.income.credits.child.agi_federal_limit
        oh_cdcc_fraction = parameters(
            period
        ).gov.states.oh.tax.income.credits.child.cdcc_fraction

        agi = tax_unit("oh_agi", period)
        us_cdcc = tax_unit("cdcc", period)

        oh_eligible = age_federal_limit <= agi < agi_state_limit
        us_eligible = agi < age_federal_limit

        return (oh_eligible * oh_cdcc_fraction + us_eligible) * us_cdcc
