from policyengine_us.model_api import *


class ri_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Rhode Island property tax credit eligibility status"
    definition_period = YEAR
    reference = (
        "http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-3.htm"
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.property_tax
        # minimum age eligibility
        head_age = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        age_eligible = max_(head_age, spouse_age) >= p.age_threshold
        # disability eligibility
        head_is_disabled = tax_unit("head_is_disabled", period)
        spouse_is_disabled = tax_unit("spouse_is_disabled", period)
        is_disabled = head_is_disabled | spouse_is_disabled
        return age_eligible | is_disabled
