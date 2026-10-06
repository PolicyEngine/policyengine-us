from policyengine_us.model_api import *


class pr_personal_property_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico casualty loss deduction on automobiles and household goods"
    unit = USD
    definition_period = YEAR
    reference = (
        # P.R. Internal Revenue Code of 2011, Section 1033.15(a)(10)(B)
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=167",
        # Sections 1061.01(b)(2)(B) and 1021.03(a)(4): spouses filing
        # separately split (a)(10) deductions 50/50
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=321",
        "https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/2-ingles/1-2011.pdf#page=40",
        # 2025 Schedule A Individual, Part I, line 5
        "https://hacienda.pr.gov/sites/default/files/inst_individuals_2025.pdf#page=26",
    )
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.casualty_loss
        # A dependent's loss belongs on the dependent's own return.
        loss = tax_unit_non_dep_add(
            tax_unit, period, ["pr_personal_property_casualty_loss"]
        )
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # A spouse filing separately claims half of the couple's loss
        # (Sections 1061.01(b)(2)(B) and 1021.03(a)(4)), up to the lower
        # separate cap. A carryover from the two preceding years counts
        # toward the same annual cap.
        own_loss = where(separate, p.separate_percentage, 1) * loss
        carryover = tax_unit("pr_personal_property_casualty_loss_carryover", period)
        return min_(own_loss + carryover, p.personal_property_cap[filing_status])
