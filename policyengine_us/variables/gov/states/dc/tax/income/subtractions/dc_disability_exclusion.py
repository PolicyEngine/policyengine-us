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
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-2440.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.disability_income_exclusion
        tax_unit = person.tax_unit
        # Form D-2440 is one per return, with a column for you and one for
        # your spouse. A dependent's disability payments are on their own
        # return.
        filer = ~person("is_tax_unit_dependent", period)
        disability_payments = person("total_disability_payments", period)
        # Up to $5,200 per disabled person.
        capped_disability_payments = filer * min_(disability_payments, p.cap)
        # Line 4.
        total_capped_payments = tax_unit.sum(capped_disability_payments)
        # Lines 5 to 9.
        federal_agi = tax_unit("adjusted_gross_income", period)
        social_security_income = tax_unit("tax_unit_taxable_social_security", period)
        reduced_income = federal_agi - social_security_income - p.amount
        capped_reduced_income = max_(reduced_income, 0)
        # Line 10.
        exclusion = max_(total_capped_payments - capped_reduced_income, 0)
        # dc_taxable_income_joint sums every person, so each filer gets a
        # share of the return's exclusion in proportion to their payments.
        share = np.zeros_like(total_capped_payments)
        mask = total_capped_payments > 0
        share[mask] = capped_disability_payments[mask] / total_capped_payments[mask]
        return exclusion * share
