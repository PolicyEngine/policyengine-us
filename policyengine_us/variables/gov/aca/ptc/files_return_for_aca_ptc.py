from policyengine_us.model_api import *


class files_return_for_aca_ptc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Files a federal return that claims the ACA premium tax credit"
    documentation = """
    Whether the tax unit files a federal income tax return on which it can
    claim the premium tax credit. A tax unit that files for any reason
    (tax_unit_is_filer) can, and so does one that takes up a credit it is
    due: it either receives advance payments, after which it "must file an
    income tax return for that taxable year ... and reconcile the advance
    credit payments" (26 CFR 1.6011-8(a)), or claims the credit on Form 8962
    with its return. Taking up coverage when the credit is $0 gives no such
    reason to file. A tax unit that neither files nor takes up a credit gets
    none, which keeps aca_ptc to filers as IRS filing data count it.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#a",
        "https://www.law.cornell.edu/cfr/text/26/1.6011-8#a",
        # Chart C, item 5: a return is required if advance payments of the
        # premium tax credit were made.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        files = tax_unit("tax_unit_is_filer", period)
        takes_up = tax_unit("takes_up_aca_if_eligible", period)
        credit = tax_unit("aca_ptc_before_filing_gate", period)
        return files | (takes_up & (credit > 0))
