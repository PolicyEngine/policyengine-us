from policyengine_us.model_api import *


class me_property_tax_fairness_credit_veterans_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Veterans cap for Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",
        # PDF pages 2-3.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.fairness.property_tax
        base_cap = tax_unit("me_property_tax_fairness_credit_base_cap", period)
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_qualified_veteran = person(
            "is_va_100_percent_permanent_service_connected_disabled_veteran", period
        )
        has_qualified_veteran = tax_unit.any(is_head_or_spouse & is_qualified_veteran)
        return has_qualified_veteran * base_cap * p.veterans_matched
