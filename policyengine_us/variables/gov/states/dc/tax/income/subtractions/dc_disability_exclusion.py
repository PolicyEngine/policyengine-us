from policyengine_us.model_api import *


class dc_disability_exclusion(Variable):
    value_type = float
    entity = Person
    label = "DC disability exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.02#(a)(2)(M)",
        # Form D-2440, lines 5 to 10.
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D-2440_Form_012626.pdf#page=1",
        # Form D-40, line 10: "Taxable amount of social security and tier 1
        # railroad retirement".
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D40_Form_0002_030526.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.disability_income_exclusion
        tax_unit = person.tax_unit

        disability_payments = person("total_disability_payments", period)
        capped_disability_payments = min_(disability_payments, p.cap)
        total_capped_payments = tax_unit.sum(capped_disability_payments)

        federal_agi = tax_unit("adjusted_gross_income", period)
        # Line 6 takes Form D-40 line 10, "Taxable amount of social security
        # and tier 1 railroad retirement".
        taxable_benefits = add(
            tax_unit,
            period,
            [
                "tax_unit_taxable_social_security",
                "tax_unit_taxable_railroad_social_security_equivalent_benefits",
            ],
        )
        reduced_income = federal_agi - taxable_benefits - p.amount
        capped_reduced_income = max_(reduced_income, 0)

        return max_(total_capped_payments - capped_reduced_income, 0)
