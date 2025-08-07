from policyengine_us.model_api import *


class md_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=5"
        "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=5"
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        md_itmded = tax_unit("md_itemized_deductions", period)
        md_stdded = tax_unit("md_standard_deduction", period)
        # 2021 and 2022 Form 502 instructions on page 5 include this FAQ:
        # 3. Itemized deductions.
        #    Q: Can I claim itemized deductions on my Maryland return if
        #       I claimed standard deduction on my federal return?
        #    A: No. You may claim itemized deductions on your Maryland
        #       return only if you claimed itemized deductions on your
        #       federal return. If you claimed your itemized deductions
        #       on your federal return, you may figure your tax using
        #       both deduction methods to determine which is best for you.
        federal_itemizer = tax_unit("tax_unit_itemizes", period)
        return where(federal_itemizer, max_(md_stdded, md_itmded), md_stdded)
