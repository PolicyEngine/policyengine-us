from policyengine_us.model_api import *


class az_increased_excise_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Increased Excise Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "az_increased_excise_tax_credit_eligible"
    reference = (
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm",
        "https://www.azleg.gov/ars/43/01072-02.htm",
        # Form 140 line 56 instructions and worksheet.
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=25",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.increased_excise
        # The increased excise tax credit is allowed for each person that a
        # personal or dependent exemption can be claimed for
        # (A.R.S. 43-1072.01(C)); from 2021, 43-1072.02(C) allows $25 for each
        # person "who is either the taxpayer, the taxpayer's spouse who does
        # not file a return or a dependent". The Form 140 worksheet counts the
        # filers and the dependents "provided that person(s) qualifies as a
        # dependent for federal purposes", and the instructions let a joint
        # filer claim the credit but not for a spouse who is barred. So a
        # filer whom another taxpayer can claim is not counted, and a return
        # on which the filer (or, if joint, either spouse) can be claimed
        # counts no dependents (IRC 152(b)(1)).
        person = tax_unit.members
        filers = tax_unit.sum(person("is_tax_unit_head_or_spouse", period))
        claimed_filers = filers - tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        disallowed_dependents = where(
            filer_is_dependent, tax_unit("tax_unit_dependents", period), 0
        )
        persons = (
            tax_unit("tax_unit_size", period) - claimed_filers - disallowed_dependents
        )
        uncapped_credit = persons * p.amount
        return min_(uncapped_credit, p.max_amount)
