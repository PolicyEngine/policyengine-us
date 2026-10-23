from policyengine_us.model_api import *


class overtime_income_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Person's overtime counts toward the overtime income deduction"
    documentation = "Whether the person is the head or spouse of the tax unit and has a Social Security number valid for the overtime income deduction, so that qualified overtime compensation the person receives counts toward the unit's deduction."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/225#d_1",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=106",
    )

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_str = ssn_card_type.decode_to_str()
        p = parameters(period).gov.irs.deductions.overtime_income
        # 26 U.S.C. 225(d)(1) requires the SSN of the individual who received
        # the overtime, so on a joint return a spouse without overtime needs
        # none.
        eligible_ssn_card_type = np.isin(ssn_card_str, p.eligible_ssn_card_type)
        # A dependent's overtime is the dependent's own income (26 U.S.C. 73(a)
        # for a child's services) and goes on the dependent's own return;
        # irs_gross_income likewise leaves dependents' income out of the unit.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eligible_ssn_card_type & head_or_spouse
