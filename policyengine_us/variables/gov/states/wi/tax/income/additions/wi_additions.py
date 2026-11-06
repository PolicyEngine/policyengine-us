from policyengine_us.model_api import *


class wi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin additions to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD.pdf",
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD-inst.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleADf.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleAD-Inst.pdf",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Wisconsin adds these items to federal adjusted gross income, which
        # leaves out a tax unit dependent's income (the dependent files their
        # own return), so only the head's and spouse's amounts count, such as
        # their interest on other states' and municipalities' obligations.
        p = parameters(period).gov.states.wi.tax.income.additions
        return tax_unit_non_dep_add(tax_unit, period, p.sources)
