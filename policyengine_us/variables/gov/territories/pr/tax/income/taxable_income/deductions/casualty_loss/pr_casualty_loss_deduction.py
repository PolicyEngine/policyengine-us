from policyengine_us.model_api import *


class pr_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico casualty loss deduction on the principal residence"
    unit = USD
    definition_period = YEAR
    reference = (
        # P.R. Internal Revenue Code of 2011, Section 1033.15(a)(10)(A)
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=167",
        # Section 1033.05(a): an individual's other losses
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=137",
        # 2025 Schedule A Individual, Part I, line 2
        "https://hacienda.pr.gov/sites/default/files/inst_individuals_2025.pdf#page=24",
    )
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.casualty_loss
        # Section 1033.15(a)(10)(A) covers only the principal residence, not
        # every casualty or theft loss that the generic casualty_loss input
        # holds. Section 1033.05(a) allows other losses of an individual only
        # in a trade or business or a transaction entered into for profit.
        # A dependent's loss belongs on the dependent's own return.
        loss = tax_unit_non_dep_add(
            tax_unit, period, ["pr_principal_residence_casualty_loss"]
        )
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(separate, p.separate_percentage, 1) * loss
