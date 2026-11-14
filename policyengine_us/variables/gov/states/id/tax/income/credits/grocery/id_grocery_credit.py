from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7",
        # Idaho Code 63-3024A(1), (4): a credit for the taxpayer, the spouse and
        # each IRC 152 dependent claimed on the return, never two for the same
        # personal exemption.
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3024A/",
        # 2025 Form 40 instructions, line 43 and the Food Tax Credit
        # Worksheet (yourself, spouse, dependents).
        # PDF pages 13-14
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=13",
        # IRC 152(b)(1).
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partV-sec152.htm",
        "https://files.dfm.idaho.gov/dfm-admin-website/rules/2022%20Archive/35/350101.pdf#page=125",
        "https://adminrules.idaho.gov/rules/current/35/350101.pdf#page=107",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        qualified_months = person("id_grocery_credit_qualified_months", period)
        p = parameters(period).gov.states.id.tax.income.credits.grocery.aged
        if p.in_effect:
            full_amount = add(
                person,
                period,
                ["id_grocery_credit_base", "id_grocery_credit_aged"],
            )
        else:
            full_amount = person("id_grocery_credit_base", period)
        # Idaho grants each taxpayer an amount under Code 63-3024A(1), and
        # (4) allows one credit per personal exemption. Exclude a filer whom
        # another taxpayer claims; claimability alone removes no amount.
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed_filer = person("claimed_as_dependent_on_another_return", period)
        # A claimable filer cannot claim dependents under IRC 152(b)(1), subject
        # to the outside claimant's federal filing exception.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        eligible = where(filer, ~claimed_filer, ~filer_is_dependent)
        credit_value = full_amount * (qualified_months / MONTHS_IN_YEAR) * eligible
        return tax_unit.sum(credit_value)
