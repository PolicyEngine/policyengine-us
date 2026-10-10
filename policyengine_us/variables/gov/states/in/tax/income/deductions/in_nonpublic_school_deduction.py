from policyengine_us.model_api import *


class in_nonpublic_school_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana nonpublic school expenditures deduction"
    definition_period = YEAR
    unit = USD
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-22",  # (d)(1)
        # Information Bulletin 107: the child must qualify as the taxpayer's
        # dependent under IRC 152.
        "https://www.in.gov/dor/files/ib107.pdf#page=1",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.deductions.nonpublic_school
        # Law specifies dependent children who attended a nonpublic school in
        # Indiana for 180 days or more and for whom non-reimbursed education
        # expenditures were made; using a national var here to save mem. A
        # return on which the filer (or, if joint, either spouse) can be
        # claimed as a dependent has no dependents (IRC 152(b)(1)).
        children = add(tax_unit, period, ["is_in_k12_nonpublic_school"])
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(filer_is_dependent, 0, children) * p.amount
