from policyengine_us.model_api import *


class ia_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa taxable income when married couple file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        # assign total net_income to tax unit head
        is_head = person("is_tax_unit_head", period)
        net_income = person("ia_net_income", period)
        head_net_income = is_head * person.tax_unit.sum(net_income)
        # subtract joint deductions
        p = parameters(period).gov.states.ia.tax.income
        deductions = [
            f"{ded}_joint" if ded == "ia_basic_deduction" else ded
            for ded in p.deductions.sources
        ]
        deductions_amount = add(person.tax_unit, period, deductions)
        return is_head * max_(0, head_net_income - deductions_amount)
