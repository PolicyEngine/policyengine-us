from policyengine_us.model_api import *


class dc_deduction_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC deduction for each tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        # D.C. Code 47-1803.04(a)(1), (b) and (e), as added by D.C. Law 26-189,
        # sec. 7112(e).
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.04",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # DC individual income tax FAQs include this:
        # Q: If I claimed itemized deductions on my federal return, must I
        #    also itemize on my DC return?
        # A: Yes. If you claim itemized deductions on your federal tax return,
        #    you must itemize on your DC tax return. You must take the same
        #    type of deduction (itemized or standard) on your DC return as
        #    taken on your federal return.
        # https://web.archive.org/web/20220726171620/https://otr.cfo.dc.gov/page/individual-income-tax-special-circumstances-faqs
        # Candidate: us-dc:additional-deductions-standard-deduction-filers
        # Subsection (e) also allows the additional deductions for filers
        # who take the standard deduction, under the exception in (b).
        standard_with_additional = tax_unit("dc_standard_deduction", period) + tax_unit(
            "dc_additional_deductions", period
        )
        return where(
            tax_unit("tax_unit_itemizes", period),
            tax_unit("dc_itemized_deductions", period),
            standard_with_additional,
        )
