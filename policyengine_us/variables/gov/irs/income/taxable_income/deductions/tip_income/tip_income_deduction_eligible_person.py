from policyengine_us.model_api import *


class tip_income_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Person's tips count toward the tip income deduction"
    documentation = "Whether the person is the head or spouse of the tax unit and has a Social Security number valid for the tip income deduction, so that qualified tips the person receives count toward the unit's deduction."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/224#e_1",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=101",
    )

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_str = ssn_card_type.decode_to_str()
        p = parameters(period).gov.irs.deductions.tip_income
        # 26 U.S.C. 224(e)(1) requires the SSN of the individual who received
        # the tips, so on a joint return a spouse without tips needs none.
        eligible_ssn_card_type = np.isin(ssn_card_str, p.eligible_ssn_card_type)
        # A dependent's tips are the dependent's own income (26 U.S.C. 73(a)
        # for a child's services) and go on the dependent's own return;
        # irs_gross_income likewise leaves dependents' income out of the unit.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eligible_ssn_card_type & head_or_spouse
