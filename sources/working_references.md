# Oregon 2025 Individual Income Tax - Working References

## Official Program Name

**Federal Program**: Individual Income Tax
**State's Official Name**: Oregon Personal Income Tax
**State Code**: OR
**Source**: Oregon Revised Statutes Chapter 316

**Variable Prefix**: `or_`

---

## Primary Sources

### 2025 Form OR-40 Instructions
- **URL**: https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf
- **Title**: 2025 Oregon Income Tax Form OR-40 Instructions
- **Content**: Tax rates, brackets, standard deduction, credits, subtractions

### 2025 Form OR-40
- **URL**: https://www.oregon.gov/dor/forms/FormsPubs/form-or-40_101-040_2025.pdf
- **Title**: 2025 Form OR-40 Oregon Individual Income Tax Return for Full-year Residents

### Oregon DOR Kicker Page
- **URL**: https://www.oregon.gov/dor/programs/individuals/pages/kicker.aspx
- **Title**: Oregon Surplus ("Kicker") Credit
- **2025 Kicker Rate**: 9.863%

### Oregon DOR Tax Credits Page
- **URL**: https://www.oregon.gov/dor/programs/individuals/pages/credits.aspx
- **Title**: Tax benefits for families

---

## 2025 Parameter Values

### Tax Brackets (Single Filers)
| Bracket | Threshold | Rate |
|---------|-----------|------|
| 1 | $0 | 4.75% |
| 2 | $4,400 | 6.75% |
| 3 | $11,050 | 8.75% |
| 4 | $125,000 | 9.90% |

### Tax Brackets (Joint/Surviving Spouse)
| Bracket | Threshold | Rate |
|---------|-----------|------|
| 1 | $0 | 4.75% |
| 2 | $8,850 | 6.75% |
| 3 | $22,100 | 8.75% |
| 4 | $250,000 | 9.90% |

### Standard Deduction
| Filing Status | Amount |
|--------------|--------|
| Single | $2,835 |
| MFS | $2,835 |
| Joint | $5,670 |
| HoH | $4,545 |
| Surviving Spouse | $5,670 |

### Personal Exemption Credit
- Amount per exemption: $256

### Federal Tax Subtraction Limit (Single)
| AGI Range | Limit |
|-----------|-------|
| $0-$125,000 | $8,500 |
| $125,000-$130,000 | $6,800 |
| $130,000-$135,000 | $5,100 |
| $135,000-$140,000 | $3,400 |
| $140,000-$145,000 | $1,700 |
| $145,000+ | $0 |

### Oregon Child Tax Credit (Kids Credit)
- Amount per child: $1,050
- Phase-out start: $26,550
- Phase-out width: $5,000
- Child limit: 5
- Ineligible age: 6

### Oregon Kicker Credit
- 2025 Rate: 9.863% (0.09863)

### Oregon EITC
- Match rate (young child): 12%
- Match rate (no young child): 9%
- Young child age threshold: 3

---

## Reference Format

All 2025 references should use format:
```yaml
- title: 2025 Oregon Income Tax Form OR-40 Instructions
  href: https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=XX
```
