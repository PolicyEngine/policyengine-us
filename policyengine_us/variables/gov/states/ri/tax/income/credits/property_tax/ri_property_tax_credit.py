from policyengine_us.model_api import *


class ri_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-9.htm"
    defined_for = "ri_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.property_tax
        household_income = tax_unit("ri_property_tax_household_income", period)
        # R.I. Gen. Laws 44-33-9(1) keys the percentage to household size
        # (RI-1040H line 1f), counting everyone in the dwelling unit.
        household_size = tax_unit.household("household_size", period)
        household_income_percent = where(
            household_size == 1,
            p.rate.one_person.calc(household_income),
            p.rate.multiple_people.calc(household_income),
        )
        threshold = household_income_percent * household_income
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        applicable_rent = rent * p.rate.rent
        rent_plus_property_tax = property_tax + applicable_rent
        uncapped_credit = max_(rent_plus_property_tax - threshold, 0)
        return min_(uncapped_credit, p.max_amount)
