from policyengine_us.model_api import *


class nj_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey qualified and other dependent children exemption"
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-3-1/",
        # 2025 NJ-1040 instructions, lines 10 and 11.
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=9",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Then get the NJ Exemptions part of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exemptions.dependents

        # Total the number of dependents. Each must qualify "as your dependent
        # for federal tax purposes" (NJ-1040 lines 10 and 11), and under IRC
        # 152(b)(1) a return on which the filer (or, if joint, either spouse)
        # can be claimed as a dependent has none.
        dependents = tax_unit("tax_unit_dependents", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)

        # Get their dependent exemption amount based on their filing status.
        return where(filer_is_dependent, 0, dependents) * p.amount
