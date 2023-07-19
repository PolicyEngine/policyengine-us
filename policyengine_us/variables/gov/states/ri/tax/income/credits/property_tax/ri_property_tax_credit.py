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
        num_household = tax_unit("tax_unit_size", period)

        person = tax_unit.members
        direct_property_taxes = tax_unit.sum(
            person("real_estate_taxes", period)
        )
        rent = tax_unit.sum(person("rent", period))
        paid_property_taxes = (direct_property_taxes + rent) > 0

        base = where(
            num_household == 1,
            p.rate.one_person.calc(agi),
            p.rate.multiple_people.calc(agi),
        )
        credit_amount = base * agi
        exceedance = max_(direct_property_taxes + rent - credit_amount, 0)
        credit = exceedance * paid_property_taxes
        return min_(credit, p.max_amount)
