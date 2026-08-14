from policyengine_us.model_api import *


class mo_ptc_income_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit upper income limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=57542",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # The higher homestead limit requires a homestead owned and occupied
        # by the claimant for the entire year; units that paid any rent take
        # the renter/part-year-owner limit.
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        homestead = (property_tax > 0) & ~tax_unit("rents", period)
        return where(
            joint,
            where(
                homestead,
                p.upper_income_limit.married_homestead,
                p.upper_income_limit.married,
            ),
            where(
                homestead,
                p.upper_income_limit.single_homestead,
                p.upper_income_limit.single,
            ),
        )
