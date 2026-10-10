from policyengine_us.model_api import *


class ne_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf",
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-2716.01",
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2025/f_Individual_Income_Tax_Booklet.pdf#page=34",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.exemptions
        # Neb. Rev. Stat. 77-2716.01 allows no personal exemption credit for
        # an individual who can be claimed on another taxpayer's return, and
        # the Form 1040N worksheet leaves the box blank for a filer or spouse
        # whom someone else can claim. Dependents count only when the filers
        # may claim them, which under IRC 152(b)(1) they may not when either
        # filer can be claimed. The federal exemption count applies both
        # rules and equals the tax unit size when no filer can be claimed.
        return tax_unit("exemptions_count", period) * p.amount
