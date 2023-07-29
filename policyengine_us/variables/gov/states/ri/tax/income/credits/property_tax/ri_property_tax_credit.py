from policyengine_us.model_api import *


class ri_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-9.htm"
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.property_tax
        agi = tax_unit("adjusted_gross_income", period)

        threshold_agi_percent = where(
            tax_unit("tax_unit_size", period) == 1,
            p.rate.one_person.calc(agi),
            p.rate.multiple_people.calc(agi),
        )
        threshold = threshold_agi_percent * agi
        rent_plus_property_tax = add(
            tax_unit, period, ["real_estate_taxes", "rent"]
        )
        uncapped_credit = max_(rent_plus_property_tax - threshold, 0)
        return min_(uncapped_credit, p.max_amount)
