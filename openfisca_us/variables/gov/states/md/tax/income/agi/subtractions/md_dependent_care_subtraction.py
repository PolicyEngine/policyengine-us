from policyengine_us.model_api import *


class md_dependent_care_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD depdendent care subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-ii-maryland-adjusted-gross-income/section-10-208-effective-until-712024-subtractions-from-federal-adjusted-gross-income-state-adjustments"
    defined_for = StateCode.MD

    """
    (e) The subtraction under subsection (a) of this section includes expenses
    for household and dependent care services not exceeding the dollar limit
    allowed under § 21(c) of the Internal Revenue Code and determined without
    reference to the percentage limitation in § 21(a)(2) of the Internal Revenue Code.

    IRC § 21(c): https://www.law.cornell.edu/uscode/text/26/21#c
    IRC § 21(a)(2): https://www.law.cornell.edu/uscode/text/26/21#a_2
    """

    formula = sum_of_variables(["cdcc_relevant_expenses"])
