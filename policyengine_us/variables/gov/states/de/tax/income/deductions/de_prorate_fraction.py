from policyengine_us.model_api import *


class de_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Delaware joint amount proration fraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=7"
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=11"
        "https://casetext.com/statute/delaware-code/title-30-state-taxes/part-ii-income-inheritance-and-estate-taxes/chapter-11-personal-income-tax/subchapter-ii-resident-individuals/section-1109-itemized-deductions-for-application-of-this-section-see-66-del-laws-c-86-section-8"
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        net_income = person("de_net_income", period)
        total_net_income = person.tax_unit.sum(net_income)
        # avoid divide-by-zero warnings when using where() function
        fraction = np.zeros_like(total_net_income)
        mask = total_net_income != 0
        fraction[mask] = net_income[mask] / total_net_income[mask]
        # if no net income, then assign entirely to head.
        return where(
            total_net_income == 0,
            person("is_tax_unit_head", period),
            fraction,
        )
