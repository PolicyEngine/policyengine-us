from policyengine_us.model_api import *


class above_the_line_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Above-the-line deductions"
    unit = USD
    documentation = (
        "Deductions applied to reach adjusted gross income from gross income "
        "(Schedule 1, line 26). A tax unit dependent's own deductions, such as "
        "the deductible part of their self-employment tax, their IRA "
        "deduction or their penalty on early withdrawal of savings, are on "
        "the dependent's own return, as their income is."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.ald
        # Person-level deductions are summed over the head and spouse only,
        # as irs_gross_income sums their income only, except amounts that are
        # the filer's even when recorded on a dependent. Tax-unit-level
        # deductions already describe this return.
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            p.deductions,
            include_dependents=p.filer_amounts_recorded_on_dependents,
        )
