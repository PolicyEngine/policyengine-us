from policyengine_us.model_api import *


class us_govt_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest on U.S. government obligations"
    unit = USD
    definition_period = YEAR
    documentation = "Interest on U.S. government obligations such as U.S. savings bonds, U.S. Treasury bills, and U.S. government certificates, received by the head and spouse."
    reference = (
        # 31 U.S.C. 3124(a) exempts the interest from state income tax; states
        # subtract it from federal adjusted gross income, which includes only
        # the filer's own interest.
        "https://www.law.cornell.edu/uscode/text/31/3124",
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # (21)(B)(i)
        "https://ndlegis.gov/cencode/t57c38.pdf#nameddest=57-38-30p3",  # 2(a)
    )

    def formula(tax_unit, period, parameters):
        # States subtract this interest from federal adjusted gross income or
        # taxable income. A tax unit dependent's interest is on the dependent's
        # own return and never in the filer's federal AGI, so only the head's
        # and spouse's interest counts.
        return tax_unit_non_dep_add(tax_unit, period, ["us_govt_interest_person"])
