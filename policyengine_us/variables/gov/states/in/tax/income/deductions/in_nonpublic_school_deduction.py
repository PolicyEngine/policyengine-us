from policyengine_us.model_api import *


class in_nonpublic_school_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nonpublic school expenditures deduction for IN"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-22"  # (d)(1)

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.nonpublic_school
        )
        children = add(tax_unit, period, ["is_in_k12_nonpublic_school"])
        # Law specifices dependent children who attended a nonpublic school in Indiana
        # for 180 days or more and for whom non-reimbursed education expenditures were made;
        # using a national var here to save mem

        return children * p.amount
