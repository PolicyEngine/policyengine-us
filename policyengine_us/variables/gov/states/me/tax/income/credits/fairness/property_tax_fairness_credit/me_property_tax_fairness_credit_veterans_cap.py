from policyengine_us.model_api import *


class me_property_tax_fairness_credit_veterans_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Veterans cap for Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = {
        "title": "2024 SCHEDULE PTFC/STFC Form 1040ME",
        "href": "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/24_Form%201040ME_Sch%20PTFC_ff_0.pdf#page=2",
    }
    # Only one spouse needs to be a veteran for the filer to get the veteran match

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        base_cap = tax_unit("me_property_tax_fairness_credit_base_cap", period)
        has_veteran = tax_unit.any(tax_unit.members("is_veteran", period))
        return has_veteran * base_cap * p.veterans_matched
