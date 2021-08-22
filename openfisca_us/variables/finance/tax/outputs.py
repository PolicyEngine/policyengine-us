from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Standard deduction, including for dependents, aged and blind"
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # calculate basic standard deduction

        STD = parameters(period).tax.deductions.standard
        MARS = taxunit("MARS", period)
        MIDR = taxunit("MIDR", period)
        MARSType = MARS.possible_values
        c15100_if_DSI = max_(
            350 + taxunit("earned", period), STD.amount.dependent
        )
        basic_if_DSI = min_(STD.amount.filer[MARS], c15100_if_DSI)
        basic_if_not_DSI = where(MIDR, 0, STD.amount.filer[MARS])
        basic_stded = where(
            taxunit("DSI", period), basic_if_DSI, basic_if_not_DSI
        )

        # calculate extra standard deduction for aged and blind
        num_extra_stded = (
            taxunit("blind_head", period) * 1
            + taxunit("blind_spouse", period) * 1
        )
        extra_joint_multiplier = where(MARS == MARSType.JOINT, 2, 1)
        num_extra_stded += (
            taxunit("age_head", period) >= 65
        ) * extra_joint_multiplier
        extra_stded = num_extra_stded * STD.amount.aged_or_blind[MARS]

        # calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((MARS == MARSType.SEPARATE) & MIDR, 0, standard)
        standard += STD.charity.allow_nonitemizers * min_(
            taxunit("c19700", period), STD.charity.nonitemizers_max
        )

        return standard



class earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return max_(
            0,
            add(taxunit, period, "e00200p", "e00200s", "sey")
            - taxunit("c03260", period),
        )


class TaxInc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # not accurate, for demo
        return max_(
            0,
            taxunit("earned", period) - taxunit("standard_deduction", period),
        )


class income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        # not accurate, for demo
        return taxunit("TaxInc", period)

# Placeholder until actual logic implemented

class Taxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        income = taxunit("income", period)
        MARS = taxunit("MARS", period)
        brackets = parameters(period).tax.income.bracket
        thresholds = (
            [0]
            + [brackets.thresholds[str(i)][MARS] for i in range(1, 7)]
            + [infinity]
        )
        rates = [brackets.rates[str(i)] for i in range(1, 8)]
        bracketed_amounts = [
            amount_between(income, lower, upper)
            for lower, upper in zip(thresholds[:-1], thresholds[1:])
        ]
        bracketed_tax_amounts = [
            rates[i] * bracketed_amounts[i] for i in range(7)
        ]
        tax_amount = sum(bracketed_tax_amounts)
        return tax_amount


class AfterTaxIncome(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return taxunit("earned", period) - taxunit("Taxes", period)

# End of placeholder


class sey_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "e00900p", "e02100p", "k1bx14p")


class sey_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return add(taxunit, period, "e00900s", "e02100ps", "k1bx14s")


class sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR



class niit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Net Investment Income Tax from Form 8960"""


class combined(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sum of iitax and payrolltax and lumpsum_tax"""


class earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class earned_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class earned_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class was_plus_sey_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class was_plus_sey_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Earned Income Credit"""


class rptc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for filing unit"""


class rptc_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for taxpayer"""


class rptc_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for spouse"""


class exact(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class expanded_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Broad income measure that includes benefit_value_total"""
    )


class iitax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output"""


class num(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """2 when MARS is 2 (married filing jointly); otherwise 1"""
    )


class othertaxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)"""


class payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was + setax + ptax_amc)"""


class refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total refundable income tax credits"""


class sep(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """2 when MARS is 3 (married filing separately); otherwise 1"""
    )


class sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "sey_p", "sey_s")


class standard(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Standard deduction (zero for itemizers)"""


class surtax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class taxbc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Regular tax on regular taxable income before credits"""


class c00100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Adjusted Gross Income (AGI)"""


class c01000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c02500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Social security (OASDI) benefits included in AGI"""


class c02900(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Total of all 'above the line' income adjustments to get AGI"""
    )


class c03260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c04470(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Itemized deductions after phase-out (zero for non-itemizers)"""
    )


class c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal exemptions after phase-out"""


class qbided(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Qualified Business Income (QBI) deduction"""


class c04800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Regular taxable income"""


class c05200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Tax amount from Sch X,Y,X tables"""


class c05700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c05800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)"""


class c07100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total non-refundable credits used to reduce positive tax liability"""


class c07180(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Nonrefundable credit for child and dependent care expenses from Form 2441"""


class CDCC_refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable credit for child and dependent care expenses from Form 2441"""


class c07200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Schedule R credit for the elderly and the disabled"""


class c07220(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Child tax credit (adjusted) from Form 8812"""


class c07230(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Education tax credits non-refundable amount from Form 8863 (includes c87668)"""


class c07240(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07400(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c08000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c09200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"""


class c09600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Alternative Minimum Tax (AMT) liability"""


class c10960(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """American Opportunity Credit refundable amount from Form 8863"""
    )


class c11070(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Child tax credit (refunded) from Form 8812"""


class c17000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Medical expenses deducted (component of pre-limitation c21060 total)"""


class e17500_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Sch A: Medical expenses, capped as a decimal fraction of AGI"""
    )


class c18300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)"""


class e18400_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: State and local income taxes deductible, capped as a decimal fraction of AGI"""


class e18500_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: State and local real estate taxes deductible, capped as a decimal fraction of AGI"""


class c19200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Interest deducted (component of pre-limitation c21060 total)"""


class e19200_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Interest deduction deductible, capped as a decimal fraction of AGI"""


class c19700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Charity contributions deducted (component of pre-limitation c21060 total)"""


class e19800_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Charity cash contributions deductible, capped as a decimal fraction of AGI"""


class e20100_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Charity noncash contributions deductible, capped as a decimal fraction of AGI"""


class c20500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)"""


class g20500_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Gross casualty or theft loss deductible, capped as a decimal fraction of AGI"""


class c20800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)"""


class e20400_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Gross miscellaneous deductions deductible, capped as a decimal fraction of AGI"""


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Itemized deductions that are phased out"""


class c21060(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Itemized deductions before phase-out (zero for non-itemizers)"""
    )


class c23650(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c59660(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c62100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Alternative Minimum Tax (AMT) taxable income"""


class c87668(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)"""


class care_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ctc_new(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class odc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Other Dependent Credit"""


class personal_refundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal refundable credit"""


class recovery_rebate_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Recovery Rebate Credit, from American Rescue Plan Act of 2021"""
    )


class personal_nonrefundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal nonrefundable credit"""


class charity_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Credit for charitable giving"""


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks13(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class fstax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class invinc_agi_ec(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class invinc_ec_base(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class lumpsum_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Lumpsum (or head) tax; appears as LSTAX variable in tc CLI minimal output"""


class pre_c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal exemption before phase-out"""


class codtc_limited(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ptax_amc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Additional Medicare Tax from Form 8959 (included in payrolltax)"""
    )


class ptax_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)"""


class ptax_was(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Employee + employer OASDI + HI FICA tax"""


class setax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Self-employment tax"""


class ymod(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ymod1(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Universal Basic Income benefit for filing unit"""


class taxable_ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Amount of UBI benefit included in AGI"""


class nontaxable_ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Amount of UBI benefit excluded from AGI"""


class mtr_paytax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Marginal payroll tax rate (in percentage terms) on extra taxpayer earnings (e00200p)"""


class mtr_inctax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Marginal income tax rate (in percentage terms) on extra taxpayer earnings (e00200p)"""


class aftertax_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """After tax income is equal to expanded_income minus combined"""
    )


class benefit_cost_total(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Government cost of all benefits received by tax unit"""


class benefit_value_total(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Consumption value of all benefits received by tax unit, which is included in expanded_income"""
