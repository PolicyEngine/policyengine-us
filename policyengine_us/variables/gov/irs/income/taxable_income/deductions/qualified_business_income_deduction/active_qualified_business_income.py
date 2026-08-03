from policyengine_us.model_api import *


class active_qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "Active qualified business income"
    documentation = (
        "Proxy for aggregate qualified business income from active qualified "
        "trades or businesses under IRC §199A(i)(2)(B). Because the model "
        "lacks a §469(h) material-participation signal, the proxy treats "
        "qualified self-employment and farm-operations income as active; "
        "self-employment income implies material participation. It also "
        "includes qualified SSTB self-employment income because SSTBs count "
        "as qualified businesses below the taxable-income threshold, where "
        "the floor binds. Partnership and S-corporation income is included "
        "as predominantly materially participating, an approximation because "
        "the data lack an active/passive split. Rental and farm-rent income "
        "are excluded because §469(c)(2) treats rental activity as passive, "
        "and estate income is passive-presumed. Supplying this variable "
        "directly as an input overrides the proxy."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#i"

    def formula(person, period, parameters):
        active_qbi = 0
        for variable in (
            "self_employment_income",
            "farm_operations_income",
            "partnership_s_corp_income",
            "sstb_self_employment_income",
        ):
            active_qbi += person(variable, period) * person(
                variable + "_would_be_qualified", period
            )
        return active_qbi
