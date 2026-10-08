from policyengine_us.model_api import *


class form_4952_capital_gain_distributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 capital gain distributions reported without Schedule D"
    unit = USD
    definition_period = YEAR
    documentation = """
    The head's and spouse's capital gain distributions reported without
    Schedule D, each floored at zero as in irs_gross_income. The Form 4952
    line 4d instructions include capital gain distributions in the net gain,
    and the line 4e instructions say "Capital gain distributions from mutual
    funds are treated as long-term capital gains." Distributions reported on
    Schedule D are already part of long_term_capital_gains. A tax unit
    dependent's distributions belong on the dependent's own return.
    """
    reference = [
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=3",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=2",
    ]

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filer = ~person("is_tax_unit_dependent", period)
        distributions = max_(0, person("non_sch_d_capital_gains", period))
        return tax_unit.sum(filer * distributions)
