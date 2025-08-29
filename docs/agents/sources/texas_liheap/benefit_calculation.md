# Texas LIHEAP Benefit Calculation

## Benefit Structure

### Regular Energy Assistance

#### Benefit Ranges (FY 2025)
- **Minimum Benefit**: $1
- **Base Benefit Range**: $200 - $1,000
- **Maximum Benefit**: $12,300 (combined heating and cooling)

#### Calculation Factors
1. **Household Income Level**
   - Lower income = higher benefit
   - Calculated as percentage of FPL

2. **Household Size**
   - Larger households receive higher benefits
   - Uses SMI adjustment percentages

3. **Energy Burden**
   - Percentage of income spent on energy
   - Higher burden = higher benefit

4. **Energy Costs**
   - Based on previous 12-month billing cycle
   - Actual bills determine need

### Crisis Assistance

#### Maximum Crisis Benefit
- **Maximum**: $2,400 per household per program year

#### Qualifying Crisis Situations
1. Utility disconnection notice
2. Past due utility bills
3. Broken heating/cooling equipment
4. Nearly empty fuel tank (propane/oil)
5. Other energy emergencies

#### Crisis Benefit Calculation
- Based on amount needed to resolve crisis
- Cannot exceed $2,400
- May include:
  - Past due amounts
  - Reconnection fees
  - Equipment repair/replacement
  - Fuel delivery minimums

## Priority Group Benefits

### Vulnerable Household Adjustments
Households with vulnerable members may receive:
- Higher benefit amounts within the range
- Priority processing
- Extended assistance periods

### Benefit Allocation by Priority
1. **Vulnerable Priority Members**
   - May receive assistance up to allocation limit
   - Full 12-month assistance possible

2. **Non-Vulnerable Households**
   - May receive up to 6 months of assistance
   - Up to allocation limit

## Benefit Calculation Process

### Step 1: Determine Base Eligibility
```
If household_income <= 150% FPL:
    eligible = True
```

### Step 2: Calculate Energy Burden
```
energy_burden = annual_energy_costs / annual_household_income
```

### Step 3: Determine Priority Points
```
priority_points = 0
if elderly_member: priority_points += 20
if disabled_member: priority_points += 20
if child_under_6: priority_points += 20
if energy_burden > 0.10: priority_points += 30
if income < 75% FPL: priority_points += 30
```

### Step 4: Calculate Base Benefit
```
base_benefit = minimum($200 + (priority_points * $10), $1,000)
```

### Step 5: Apply Household Size Adjustment
```
size_multiplier = SMI_adjustment_percentage[household_size]
adjusted_benefit = base_benefit * size_multiplier
```

### Step 6: Apply Caps
```
final_benefit = minimum(adjusted_benefit, $12,300)
```

## Weatherization Assistance

### Maximum Benefit
- **Maximum**: $12,000 per household

### Eligibility
- Must meet LIHEAP income requirements
- Priority to households with:
  - High energy burden
  - Elderly members
  - Disabled members
  - Children

### Covered Improvements
- Insulation
- Weather stripping
- Energy-efficient windows
- HVAC system repairs
- Other cost-effective measures

## Payment Methods

### Vendor Payments (Primary)
- Paid directly to utility company
- Applied to customer account
- Requires vendor agreement

### Two-Party Checks
- Made out to client and vendor
- Used when vendor agreement unavailable

### Client Payments (Rare)
- Only in specific circumstances
- Requires documentation of hardship

## Benefit Timing

### Regular Assistance
- Once per program year
- Typically seasonal:
  - Cooling: April - September
  - Heating: October - March

### Crisis Assistance
- Available year-round
- Once per crisis situation
- Multiple crises possible if under cap

## Important Limitations

1. **Annual Cap**: Cannot exceed $12,300 for regular assistance
2. **Crisis Cap**: Cannot exceed $2,400 for crisis assistance
3. **Frequency**: Generally once per program year
4. **No Cash Benefits**: Payments go to vendors
5. **No Retroactive Payment**: For bills before application

## References

- **Benefit Amounts Source**: FY 2025 LIHEAP State Plan
- **Federal Guidance**: 45 CFR Part 96
- **State Tools**: CEAP Production Schedule Tool (July 2024)
- **Priority System**: TDHCA CEAP Program Guidance