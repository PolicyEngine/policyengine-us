from policyengine_us.model_api import *


class ri_property_tax_nontaxable_alimony(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island property tax credit alimony outside federal AGI"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Alimony received that federal gross income leaves out, which Rhode "
        "Island counts as non-taxable income for the property tax credit "
        "(R.I. Gen. Laws 44-33-3(7)). Federal adjusted gross income already "
        "holds alimony under a divorce instrument executed before 2019 "
        "(RI-1040H line 17), so only the rest is added and alimony counts "
        "once."
    )
    reference = (
        "http://webserver.rilegislature.gov/Statutes/TITLE44/44-33/44-33-3.htm",
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2026-01/2025%201040H_w.pdf#page=2",
    )
    defined_for = StateCode.RI

    def formula(person, period, parameters):
        alimony = person("alimony_income", period)
        sources = parameters(period).gov.irs.gross_income.sources
        # Federal gross income holds taxable_alimony_income, the alimony under
        # pre-2019 divorce instruments, when that is a listed source.
        if "taxable_alimony_income" in sources:
            taxable_alimony = person("taxable_alimony_income", period)
            return max_(alimony - taxable_alimony, 0)
        return alimony
