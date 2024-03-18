from policyengine_us.model_api import *


class md_eitc_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD state eitc cap"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=19"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # 18A - individual with qualified child
        # OR married couple filing separetely
        # OR jointly with or without qualifying child
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.md.tax.income.credits.eitc
        md_general_eitc = federal_eitc * p.match.non_refundable

        # 18A.1 – individual without qualifying child
        md_single_childless_eitc = min_(p.childless.max_amount, federal_eitc)

        md_qualifies_for_single_childless_eitc = tax_unit(
            "md_qualifies_for_single_childless_eitc", period
        )

        return where(
            md_qualifies_for_single_childless_eitc,
            md_single_childless_eitc,
            md_general_eitc,
        )
