"""
Excel Generator for Budget Impact Model.

Creates a user-friendly Excel workbook with:
- Input dashboard
- Results dashboard with visualizations
- Scenario comparisons
- Sensitivity analysis
"""

from typing import Dict, List, Optional
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import (
        Font, PatternFill, Border, Side, Alignment, NamedStyle
    )
    from openpyxl.chart import BarChart, LineChart, Reference, PieChart
    from openpyxl.chart.label import DataLabelList
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import DataBarRule
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from .inputs import BIMInputs, UptakeScenario, COUNTRY_CONFIGS
from .calculator import BIMCalculator, BIMResults


class ExcelGenerator:
    """
    Generates user-friendly Excel workbook for BIM.
    """

    # Style constants
    HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
    SUBHEADER_FILL = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    INPUT_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    RESULT_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    def __init__(self, inputs: BIMInputs, results: Optional[BIMResults] = None):
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl is required for Excel generation. Install with: pip install openpyxl")

        self.inputs = inputs
        self.results = results
        self.wb = Workbook()
        self._setup_styles()

    def _setup_styles(self):
        """Set up named styles for the workbook."""
        # Header style
        header_style = NamedStyle(name="header_style")
        header_style.font = self.HEADER_FONT
        header_style.fill = self.HEADER_FILL
        header_style.alignment = Alignment(horizontal="center", vertical="center")
        header_style.border = self.BORDER
        self.wb.add_named_style(header_style)

        # Input style
        input_style = NamedStyle(name="input_style")
        input_style.fill = self.INPUT_FILL
        input_style.border = self.BORDER
        input_style.alignment = Alignment(horizontal="right")
        self.wb.add_named_style(input_style)

        # Result style
        result_style = NamedStyle(name="result_style")
        result_style.fill = self.RESULT_FILL
        result_style.border = self.BORDER
        result_style.alignment = Alignment(horizontal="right")
        result_style.font = Font(bold=True)
        self.wb.add_named_style(result_style)

    def generate(self, output_path: str) -> str:
        """
        Generate the complete Excel workbook.

        Args:
            output_path: Path to save the Excel file

        Returns:
            Path to the generated file
        """
        # Remove default sheet
        if "Sheet" in self.wb.sheetnames:
            del self.wb["Sheet"]

        # Create all sheets
        self._create_cover_sheet()
        self._create_input_dashboard()
        self._create_population_sheet()
        self._create_market_sheet()
        self._create_cost_sheet()
        self._create_results_dashboard()
        self._create_scenario_comparison()
        self._create_sensitivity_sheet()
        self._create_documentation_sheet()

        # Save workbook
        self.wb.save(output_path)
        return output_path

    def _create_cover_sheet(self):
        """Create cover/instructions sheet."""
        ws = self.wb.create_sheet("Cover", 0)

        # Title
        ws.merge_cells("B2:G3")
        ws["B2"] = "Budget Impact Model"
        ws["B2"].font = Font(size=24, bold=True, color="1F4E79")
        ws["B2"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("B4:G4")
        ws["B4"] = "IXA-001 for Resistant Hypertension"
        ws["B4"].font = Font(size=16, italic=True)
        ws["B4"].alignment = Alignment(horizontal="center")

        # Model info
        info_start = 6
        info_items = [
            ("Product:", "IXA-001 (Selective Aldosterone Synthase Inhibitor)"),
            ("Indication:", "Uncontrolled Resistant Hypertension"),
            ("Sponsor:", "Atlantis Pharmaceuticals"),
            ("Model Version:", "1.0"),
            ("Date:", "February 2026"),
            ("Country:", self.inputs.country.country_name),
        ]

        for i, (label, value) in enumerate(info_items):
            row = info_start + i
            ws[f"B{row}"] = label
            ws[f"B{row}"].font = Font(bold=True)
            ws[f"C{row}"] = value

        # Instructions
        ws["B14"] = "Quick Start Guide"
        ws["B14"].font = Font(size=14, bold=True, color="1F4E79")

        instructions = [
            "1. Go to 'Input Dashboard' to modify key inputs",
            "2. Review 'Population' sheet for patient cascade",
            "3. Review 'Market Dynamics' for uptake assumptions",
            "4. View 'Results Dashboard' for budget impact summary",
            "5. Compare scenarios in 'Scenario Comparison' sheet",
            "6. Run sensitivity analysis in 'Sensitivity' sheet",
        ]

        for i, instruction in enumerate(instructions):
            ws[f"B{16 + i}"] = instruction

        # Key messages
        ws["B24"] = "Key Model Outputs"
        ws["B24"].font = Font(size=14, bold=True, color="1F4E79")

        if self.results:
            currency = self.inputs.country.currency_symbol
            ws["B26"] = f"Eligible Patients: {self.results.total_eligible_patients:,}"
            ws["B27"] = f"5-Year Budget Impact: {currency}{self.results.total_budget_impact_5yr:,.0f}"
            ws["B28"] = f"Year 1 PMPM: {currency}{self.results.pmpm_impact_year1:.2f}"
            ws["B29"] = f"Year 5 PMPM: {currency}{self.results.pmpm_impact_year5:.2f}"

        # Set column widths
        ws.column_dimensions["A"].width = 3
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 45

    def _create_input_dashboard(self):
        """Create the main input dashboard."""
        ws = self.wb.create_sheet("Input Dashboard")

        # Title
        ws.merge_cells("B2:F2")
        ws["B2"] = "INPUT DASHBOARD"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        # Instructions
        ws["B3"] = "Yellow cells can be modified. Press Enter after changes to update calculations."
        ws["B3"].font = Font(italic=True, size=10)

        # Population Inputs Section
        row = 5
        ws[f"B{row}"] = "POPULATION INPUTS"
        ws[f"B{row}"].style = "header_style"
        ws.merge_cells(f"B{row}:D{row}")

        pop_inputs = [
            ("Total Plan Population", self.inputs.population.total_population, "lives"),
            ("Adult Proportion (18+)", self.inputs.population.adult_proportion * 100, "%"),
            ("Hypertension Prevalence", self.inputs.population.hypertension_prevalence * 100, "%"),
            ("Resistant HTN (of HTN)", self.inputs.population.resistant_htn_proportion * 100, "%"),
            ("Uncontrolled (of Resistant)", self.inputs.population.uncontrolled_proportion * 100, "%"),
            ("Treatment-Seeking Rate", self.inputs.population.treatment_seeking_rate * 100, "%"),
        ]

        for i, (label, value, unit) in enumerate(pop_inputs):
            r = row + 1 + i
            ws[f"B{r}"] = label
            ws[f"C{r}"] = value
            ws[f"C{r}"].style = "input_style"
            ws[f"D{r}"] = unit

        # Calculated eligible patients
        r = row + len(pop_inputs) + 2
        ws[f"B{r}"] = "ELIGIBLE PATIENTS"
        ws[f"B{r}"].font = Font(bold=True)
        ws[f"C{r}"] = self.inputs.population.eligible_patients
        ws[f"C{r}"].style = "result_style"
        ws[f"C{r}"].number_format = "#,##0"

        # Market Inputs Section
        row = r + 3
        ws[f"B{row}"] = "MARKET INPUTS"
        ws[f"B{row}"].style = "header_style"
        ws.merge_cells(f"B{row}:D{row}")

        market_inputs = [
            ("Baseline - Spironolactone", self.inputs.market.baseline_spironolactone * 100, "%"),
            ("Baseline - Other MRA", self.inputs.market.baseline_other_mra * 100, "%"),
            ("Baseline - No 4th Line Tx", self.inputs.market.baseline_no_4th_line * 100, "%"),
        ]

        for i, (label, value, unit) in enumerate(market_inputs):
            r = row + 1 + i
            ws[f"B{r}"] = label
            ws[f"C{r}"] = value
            ws[f"C{r}"].style = "input_style"
            ws[f"D{r}"] = unit

        # Cost Inputs Section
        row = r + 3
        ws[f"B{row}"] = "COST INPUTS (Annual)"
        ws[f"B{row}"].style = "header_style"
        ws.merge_cells(f"B{row}:D{row}")

        currency = self.inputs.country.currency_symbol
        cost_inputs = [
            ("IXA-001 Drug Cost", self.inputs.costs.ixa_001_annual, currency),
            ("Spironolactone Drug Cost", self.inputs.costs.spironolactone_annual, currency),
            ("Other MRA Drug Cost", self.inputs.costs.other_mra_annual, currency),
            ("IXA-001 Monitoring", self.inputs.costs.monitoring_ixa_001, currency),
            ("Spironolactone Monitoring", self.inputs.costs.monitoring_spironolactone, currency),
            ("Office Visits (All)", self.inputs.costs.office_visits_annual, currency),
        ]

        for i, (label, value, unit) in enumerate(cost_inputs):
            r = row + 1 + i
            ws[f"B{r}"] = label
            ws[f"C{r}"] = value
            ws[f"C{r}"].style = "input_style"
            ws[f"C{r}"].number_format = f'"{unit}"#,##0'

        # Scenario Selection
        row = r + 3
        ws[f"B{row}"] = "ANALYSIS SETTINGS"
        ws[f"B{row}"].style = "header_style"
        ws.merge_cells(f"B{row}:D{row}")

        r = row + 1
        ws[f"B{r}"] = "Selected Scenario"
        ws[f"C{r}"] = self.inputs.selected_scenario.value.capitalize()
        ws[f"C{r}"].style = "input_style"

        r += 1
        ws[f"B{r}"] = "Time Horizon"
        ws[f"C{r}"] = self.inputs.time_horizon_years
        ws[f"C{r}"].style = "input_style"
        ws[f"D{r}"] = "years"

        r += 1
        ws[f"B{r}"] = "Include Event Offsets"
        ws[f"C{r}"] = "Yes" if self.inputs.include_event_offsets else "No"
        ws[f"C{r}"].style = "input_style"

        # Set column widths
        ws.column_dimensions["A"].width = 3
        ws.column_dimensions["B"].width = 30
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 10

    def _create_population_sheet(self):
        """Create population cascade sheet."""
        ws = self.wb.create_sheet("Population")

        # Title
        ws.merge_cells("B2:E2")
        ws["B2"] = "POPULATION CASCADE"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        # Cascade table
        cascade = self.inputs.population.get_cascade()

        headers = ["Stage", "Patients", "% of Previous", "% of Total"]
        for i, header in enumerate(headers):
            ws.cell(row=4, column=i+2, value=header).style = "header_style"

        cascade_items = [
            ("Total Plan Population", cascade["total_population"], 100.0, 100.0),
            ("Adults (18+)", cascade["adults_18_plus"],
             cascade["adults_18_plus"] / cascade["total_population"] * 100,
             cascade["adults_18_plus"] / cascade["total_population"] * 100),
            ("With Hypertension", cascade["with_hypertension"],
             cascade["with_hypertension"] / cascade["adults_18_plus"] * 100 if cascade["adults_18_plus"] > 0 else 0,
             cascade["with_hypertension"] / cascade["total_population"] * 100),
            ("Resistant Hypertension", cascade["resistant_hypertension"],
             cascade["resistant_hypertension"] / cascade["with_hypertension"] * 100 if cascade["with_hypertension"] > 0 else 0,
             cascade["resistant_hypertension"] / cascade["total_population"] * 100),
            ("Uncontrolled Resistant", cascade["uncontrolled_resistant"],
             cascade["uncontrolled_resistant"] / cascade["resistant_hypertension"] * 100 if cascade["resistant_hypertension"] > 0 else 0,
             cascade["uncontrolled_resistant"] / cascade["total_population"] * 100),
            ("Eligible for Treatment", cascade["eligible_for_treatment"],
             cascade["eligible_for_treatment"] / cascade["uncontrolled_resistant"] * 100 if cascade["uncontrolled_resistant"] > 0 else 0,
             cascade["eligible_for_treatment"] / cascade["total_population"] * 100),
        ]

        for i, (stage, patients, pct_prev, pct_total) in enumerate(cascade_items):
            row = 5 + i
            ws.cell(row=row, column=2, value=stage)
            ws.cell(row=row, column=3, value=patients).number_format = "#,##0"
            ws.cell(row=row, column=4, value=pct_prev).number_format = "0.0%"
            ws.cell(row=row, column=5, value=pct_total).number_format = "0.00%"

        # Highlight eligible patients row
        for col in range(2, 6):
            ws.cell(row=10, column=col).style = "result_style"

        # Add funnel chart data reference
        ws["B13"] = "Data Sources"
        ws["B13"].font = Font(bold=True)
        ws["B14"] = "Adult proportion: US Census / Eurostat"
        ws["B15"] = "HTN prevalence: NHANES / ESC Guidelines"
        ws["B16"] = "Resistant HTN: Carey et al., Circulation 2018"

        # Set column widths
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 15
        ws.column_dimensions["D"].width = 15
        ws.column_dimensions["E"].width = 15

    def _create_market_sheet(self):
        """Create market dynamics sheet."""
        ws = self.wb.create_sheet("Market Dynamics")

        # Title
        ws.merge_cells("B2:H2")
        ws["B2"] = "MARKET DYNAMICS & UPTAKE"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        # Baseline market shares
        ws["B4"] = "BASELINE MARKET SHARES (No IXA-001)"
        ws["B4"].style = "header_style"
        ws.merge_cells("B4:D4")

        baseline = [
            ("Spironolactone", self.inputs.market.baseline_spironolactone),
            ("Other MRA (Eplerenone)", self.inputs.market.baseline_other_mra),
            ("No 4th-line Treatment", self.inputs.market.baseline_no_4th_line),
        ]

        for i, (treatment, share) in enumerate(baseline):
            row = 5 + i
            ws.cell(row=row, column=2, value=treatment)
            ws.cell(row=row, column=3, value=share).number_format = "0%"

        # Displacement assumptions
        ws["B10"] = "DISPLACEMENT ASSUMPTIONS"
        ws["B10"].style = "header_style"
        ws.merge_cells("B10:D10")

        displacement = [
            ("From Spironolactone", self.inputs.market.displacement_from_spironolactone),
            ("From Other MRA", self.inputs.market.displacement_from_other_mra),
            ("New Treatment (Untreated)", self.inputs.market.displacement_from_untreated),
        ]

        for i, (source, pct) in enumerate(displacement):
            row = 11 + i
            ws.cell(row=row, column=2, value=source)
            ws.cell(row=row, column=3, value=pct).number_format = "0%"

        # Uptake curves
        ws["B16"] = "IXA-001 UPTAKE BY SCENARIO"
        ws["B16"].style = "header_style"
        ws.merge_cells("B16:G16")

        # Headers
        headers = ["Scenario", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
        for i, header in enumerate(headers):
            ws.cell(row=17, column=i+2, value=header).style = "header_style"

        # Data
        scenarios = [
            (UptakeScenario.CONSERVATIVE, "Conservative"),
            (UptakeScenario.MODERATE, "Moderate"),
            (UptakeScenario.OPTIMISTIC, "Optimistic"),
        ]

        for i, (scenario, name) in enumerate(scenarios):
            row = 18 + i
            ws.cell(row=row, column=2, value=name)
            for j, uptake in enumerate(self.inputs.market.uptake_curves[scenario]):
                ws.cell(row=row, column=3+j, value=uptake).number_format = "0%"

        # Add line chart for uptake
        chart = LineChart()
        chart.title = "IXA-001 Market Uptake by Scenario"
        chart.y_axis.title = "Market Share"
        chart.x_axis.title = "Year"
        chart.style = 10

        # Data references
        data = Reference(ws, min_col=3, min_row=17, max_col=7, max_row=20)
        cats = Reference(ws, min_col=3, min_row=17, max_col=7, max_row=17)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        chart.width = 15
        chart.height = 10
        ws.add_chart(chart, "B24")

        # Set column widths
        for col in range(2, 8):
            ws.column_dimensions[get_column_letter(col)].width = 12

    def _create_cost_sheet(self):
        """Create cost inputs sheet."""
        ws = self.wb.create_sheet("Costs")

        currency = self.inputs.country.currency_symbol

        # Title
        ws.merge_cells("B2:F2")
        ws["B2"] = f"COST INPUTS ({self.inputs.costs.currency})"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        # Per-patient annual costs table
        ws["B4"] = "ANNUAL PER-PATIENT COSTS"
        ws["B4"].style = "header_style"
        ws.merge_cells("B4:F4")

        headers = ["Cost Component", "IXA-001", "Spironolactone", "Other MRA", "No Treatment"]
        for i, header in enumerate(headers):
            ws.cell(row=5, column=i+2, value=header).style = "header_style"

        cost_rows = [
            ("Drug Cost",
             self.inputs.costs.ixa_001_annual,
             self.inputs.costs.spironolactone_annual,
             self.inputs.costs.other_mra_annual,
             self.inputs.costs.no_treatment_annual),
            ("Monitoring",
             self.inputs.costs.monitoring_ixa_001,
             self.inputs.costs.monitoring_spironolactone,
             self.inputs.costs.monitoring_other_mra,
             self.inputs.costs.monitoring_no_treatment),
            ("Office Visits",
             self.inputs.costs.office_visits_annual,
             self.inputs.costs.office_visits_annual,
             self.inputs.costs.office_visits_annual,
             self.inputs.costs.office_visits_annual),
            ("AE Management",
             self.inputs.costs.ae_management_ixa_001,
             self.inputs.costs.ae_management_spironolactone,
             self.inputs.costs.ae_management_other_mra,
             self.inputs.costs.ae_management_no_treatment),
        ]

        for i, row_data in enumerate(cost_rows):
            row = 6 + i
            for j, value in enumerate(row_data):
                cell = ws.cell(row=row, column=j+2, value=value)
                if j > 0:
                    cell.number_format = f'"{currency}"#,##0'

        # Subtotal
        row = 10
        ws.cell(row=row, column=2, value="Subtotal").font = Font(bold=True)
        for col in range(3, 7):
            subtotal = sum(ws.cell(row=r, column=col).value or 0 for r in range(6, 10))
            ws.cell(row=row, column=col, value=subtotal).number_format = f'"{currency}"#,##0'
            ws.cell(row=row, column=col).font = Font(bold=True)

        # Avoided events offset
        row = 12
        ws.cell(row=row, column=2, value="Avoided CV Events (Offset)")
        ws.cell(row=row, column=3, value=-self.inputs.costs.avoided_events_ixa_001_annual).number_format = f'"{currency}"#,##0'
        ws.cell(row=row, column=4, value=-self.inputs.costs.avoided_events_spironolactone_annual).number_format = f'"{currency}"#,##0'
        ws.cell(row=row, column=5, value=-self.inputs.costs.avoided_events_other_mra_annual).number_format = f'"{currency}"#,##0'
        ws.cell(row=row, column=6, value=0).number_format = f'"{currency}"#,##0'

        # Net cost
        row = 14
        ws.cell(row=row, column=2, value="NET ANNUAL COST").style = "result_style"
        treatments = ["ixa_001", "spironolactone", "other_mra", "no_treatment"]
        for i, treatment in enumerate(treatments):
            net_cost = self.inputs.costs.get_total_annual_cost(treatment, include_offsets=True)
            ws.cell(row=row, column=3+i, value=net_cost).style = "result_style"
            ws.cell(row=row, column=3+i).number_format = f'"{currency}"#,##0'

        # Cost comparison bar chart
        chart = BarChart()
        chart.title = "Net Annual Cost per Patient"
        chart.y_axis.title = f"Cost ({self.inputs.costs.currency})"
        chart.type = "col"
        chart.style = 10

        data = Reference(ws, min_col=3, min_row=14, max_col=6, max_row=14)
        cats = Reference(ws, min_col=3, min_row=5, max_col=6, max_row=5)
        chart.add_data(data)
        chart.set_categories(cats)
        chart.shape = 4

        chart.width = 12
        chart.height = 8
        ws.add_chart(chart, "B17")

        # Set column widths
        ws.column_dimensions["B"].width = 25
        for col in range(3, 7):
            ws.column_dimensions[get_column_letter(col)].width = 15

    def _create_results_dashboard(self):
        """Create results dashboard with key outputs and charts."""
        ws = self.wb.create_sheet("Results Dashboard")

        if not self.results:
            ws["B2"] = "No results available. Run the BIM calculator first."
            return

        currency = self.inputs.country.currency_symbol

        # Title
        ws.merge_cells("B2:H2")
        ws["B2"] = "BUDGET IMPACT RESULTS"
        ws["B2"].font = Font(size=18, bold=True, color="1F4E79")

        ws["B3"] = f"Scenario: {self.results.scenario.value.capitalize()}"
        ws["B3"].font = Font(size=12, italic=True)

        # Key metrics box
        ws["B5"] = "KEY METRICS"
        ws["B5"].style = "header_style"
        ws.merge_cells("B5:D5")

        metrics = [
            ("Eligible Patients", f"{self.results.total_eligible_patients:,}"),
            ("5-Year Budget Impact", f"{currency}{self.results.total_budget_impact_5yr:,.0f}"),
            ("Average Annual Impact", f"{currency}{self.results.average_annual_impact:,.0f}"),
            ("Year 1 PMPM", f"{currency}{self.results.pmpm_impact_year1:.2f}"),
            ("Year 5 PMPM", f"{currency}{self.results.pmpm_impact_year5:.2f}"),
            ("Cost per IXA-001 Patient", f"{currency}{self.results.cost_per_ixa_patient:,.0f}"),
            ("Incremental Cost/Patient", f"{currency}{self.results.incremental_cost_per_ixa_patient:,.0f}"),
        ]

        for i, (label, value) in enumerate(metrics):
            row = 6 + i
            ws.cell(row=row, column=2, value=label)
            ws.cell(row=row, column=3, value=value).style = "result_style"

        # Year-by-year table
        ws["B15"] = "YEAR-BY-YEAR BUDGET IMPACT"
        ws["B15"].style = "header_style"
        ws.merge_cells("B15:H15")

        headers = ["Year", "IXA-001 Patients", "Budget - Current", "Budget - New", "Budget Impact", "PMPM"]
        for i, header in enumerate(headers):
            ws.cell(row=16, column=i+2, value=header).style = "header_style"

        for i, yr in enumerate(self.results.yearly_results):
            row = 17 + i
            ws.cell(row=row, column=2, value=yr.year)
            ws.cell(row=row, column=3, value=yr.patients_ixa_001).number_format = "#,##0"
            ws.cell(row=row, column=4, value=yr.cost_current_world).number_format = f'"{currency}"#,##0'
            ws.cell(row=row, column=5, value=yr.cost_new_world).number_format = f'"{currency}"#,##0'
            ws.cell(row=row, column=6, value=yr.budget_impact).number_format = f'"{currency}"#,##0'
            pmpm = yr.budget_impact / self.inputs.population.total_population / 12
            ws.cell(row=row, column=7, value=pmpm).number_format = f'"{currency}"0.00'

        # Total row
        row = 17 + len(self.results.yearly_results)
        ws.cell(row=row, column=2, value="TOTAL").font = Font(bold=True)
        ws.cell(row=row, column=6, value=self.results.total_budget_impact_5yr).style = "result_style"
        ws.cell(row=row, column=6).number_format = f'"{currency}"#,##0'

        # Budget impact chart
        chart = BarChart()
        chart.title = "Annual Budget Impact"
        chart.y_axis.title = f"Budget Impact ({self.inputs.costs.currency})"
        chart.x_axis.title = "Year"
        chart.type = "col"
        chart.style = 10

        data = Reference(ws, min_col=6, min_row=16, max_col=6, max_row=16 + len(self.results.yearly_results))
        cats = Reference(ws, min_col=2, min_row=17, max_col=2, max_row=16 + len(self.results.yearly_results))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        chart.width = 12
        chart.height = 8
        ws.add_chart(chart, "I5")

        # Market share evolution chart
        ws["B25"] = "MARKET SHARE EVOLUTION"
        ws["B25"].style = "header_style"
        ws.merge_cells("B25:F25")

        share_headers = ["Year", "IXA-001", "Spironolactone", "Other MRA", "No Treatment"]
        for i, header in enumerate(share_headers):
            ws.cell(row=26, column=i+2, value=header).style = "header_style"

        for i, yr in enumerate(self.results.yearly_results):
            row = 27 + i
            ws.cell(row=row, column=2, value=yr.year)
            ws.cell(row=row, column=3, value=yr.share_ixa_001).number_format = "0%"
            ws.cell(row=row, column=4, value=yr.share_spironolactone).number_format = "0%"
            ws.cell(row=row, column=5, value=yr.share_other_mra).number_format = "0%"
            ws.cell(row=row, column=6, value=yr.share_no_treatment).number_format = "0%"

        # Set column widths
        ws.column_dimensions["B"].width = 20
        for col in range(3, 8):
            ws.column_dimensions[get_column_letter(col)].width = 18

    def _create_scenario_comparison(self):
        """Create scenario comparison sheet."""
        ws = self.wb.create_sheet("Scenario Comparison")

        if not self.results:
            ws["B2"] = "No results available."
            return

        # Run all scenarios
        calculator = BIMCalculator(self.inputs)
        all_results = calculator.run_all_scenarios()

        currency = self.inputs.country.currency_symbol

        # Title
        ws.merge_cells("B2:F2")
        ws["B2"] = "SCENARIO COMPARISON"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        # Comparison table
        headers = ["Metric", "Conservative", "Moderate", "Optimistic"]
        for i, header in enumerate(headers):
            ws.cell(row=4, column=i+2, value=header).style = "header_style"

        metrics = [
            ("5-Year Budget Impact", "total_budget_impact_5yr", f'"{currency}"#,##0'),
            ("Average Annual Impact", "average_annual_impact", f'"{currency}"#,##0'),
            ("Year 1 PMPM", "pmpm_impact_year1", f'"{currency}"0.00'),
            ("Year 5 PMPM", "pmpm_impact_year5", f'"{currency}"0.00'),
            ("Year 5 IXA-001 Patients", None, "#,##0"),
        ]

        for i, (label, attr, fmt) in enumerate(metrics):
            row = 5 + i
            ws.cell(row=row, column=2, value=label)
            for j, scenario in enumerate([UptakeScenario.CONSERVATIVE, UptakeScenario.MODERATE, UptakeScenario.OPTIMISTIC]):
                res = all_results[scenario]
                if attr:
                    value = getattr(res, attr)
                else:
                    value = res.yearly_results[-1].patients_ixa_001 if res.yearly_results else 0
                ws.cell(row=row, column=3+j, value=value).number_format = fmt

        # Year-by-year comparison
        ws["B12"] = "YEAR-BY-YEAR BUDGET IMPACT BY SCENARIO"
        ws["B12"].style = "header_style"
        ws.merge_cells("B12:E12")

        headers = ["Year", "Conservative", "Moderate", "Optimistic"]
        for i, header in enumerate(headers):
            ws.cell(row=13, column=i+2, value=header).style = "header_style"

        for year in range(1, 6):
            row = 13 + year
            ws.cell(row=row, column=2, value=year)
            for j, scenario in enumerate([UptakeScenario.CONSERVATIVE, UptakeScenario.MODERATE, UptakeScenario.OPTIMISTIC]):
                res = all_results[scenario]
                if year <= len(res.yearly_results):
                    value = res.yearly_results[year-1].budget_impact
                else:
                    value = 0
                ws.cell(row=row, column=3+j, value=value).number_format = f'"{currency}"#,##0'

        # Comparison chart
        chart = LineChart()
        chart.title = "Budget Impact by Scenario"
        chart.y_axis.title = f"Annual Budget Impact ({self.inputs.costs.currency})"
        chart.x_axis.title = "Year"
        chart.style = 10

        data = Reference(ws, min_col=3, min_row=13, max_col=5, max_row=18)
        cats = Reference(ws, min_col=2, min_row=14, max_col=2, max_row=18)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        chart.width = 15
        chart.height = 10
        ws.add_chart(chart, "B21")

        # Set column widths
        ws.column_dimensions["B"].width = 25
        for col in range(3, 6):
            ws.column_dimensions[get_column_letter(col)].width = 18

    def _create_sensitivity_sheet(self):
        """Create sensitivity analysis sheet."""
        ws = self.wb.create_sheet("Sensitivity")

        currency = self.inputs.country.currency_symbol

        # Title
        ws.merge_cells("B2:G2")
        ws["B2"] = "SENSITIVITY ANALYSIS"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        if not self.results:
            ws["B4"] = "No results available."
            return

        # One-way sensitivity - IXA-001 price
        calculator = BIMCalculator(self.inputs)
        base_price = self.inputs.costs.ixa_001_annual
        price_range = [base_price * mult for mult in [0.5, 0.75, 1.0, 1.25, 1.5]]

        ws["B4"] = "IXA-001 PRICE SENSITIVITY"
        ws["B4"].style = "header_style"
        ws.merge_cells("B4:D4")

        headers = ["Annual Price", "5-Year Impact", "PMPM Year 5"]
        for i, header in enumerate(headers):
            ws.cell(row=5, column=i+2, value=header).style = "header_style"

        price_results = calculator.sensitivity_analysis("ixa_001_annual", price_range)
        for i, result in enumerate(price_results):
            row = 6 + i
            ws.cell(row=row, column=2, value=result["value"]).number_format = f'"{currency}"#,##0'
            ws.cell(row=row, column=3, value=result["budget_impact_5yr"]).number_format = f'"{currency}"#,##0'
            ws.cell(row=row, column=4, value=result["pmpm_year5"]).number_format = f'"{currency}"0.00'

        # Resistant HTN proportion sensitivity
        ws["B13"] = "RESISTANT HTN PREVALENCE SENSITIVITY"
        ws["B13"].style = "header_style"
        ws.merge_cells("B13:D13")

        headers = ["Prevalence", "Eligible Patients", "5-Year Impact"]
        for i, header in enumerate(headers):
            ws.cell(row=14, column=i+2, value=header).style = "header_style"

        prev_range = [0.08, 0.10, 0.12, 0.14, 0.16]
        prev_results = calculator.sensitivity_analysis("resistant_htn_proportion", prev_range)
        for i, result in enumerate(prev_results):
            row = 15 + i
            ws.cell(row=row, column=2, value=result["value"]).number_format = "0%"
            # Recalculate eligible patients
            temp_inputs = BIMInputs()
            temp_inputs.population.resistant_htn_proportion = result["value"]
            ws.cell(row=row, column=3, value=temp_inputs.population.eligible_patients).number_format = "#,##0"
            ws.cell(row=row, column=4, value=result["budget_impact_5yr"]).number_format = f'"{currency}"#,##0'

        # Price threshold analysis
        ws["B22"] = "PRICE THRESHOLD ANALYSIS"
        ws["B22"].style = "header_style"
        ws.merge_cells("B22:D22")

        ws["B23"] = "Budget-neutral price (5-year impact = $0):"
        threshold_price = calculator.price_threshold_analysis(0)
        if threshold_price:
            ws["D23"] = threshold_price
            ws["D23"].number_format = f'"{currency}"#,##0'
            ws["D23"].style = "result_style"
        else:
            ws["D23"] = "N/A"

        # Set column widths
        ws.column_dimensions["B"].width = 35
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 18

    def _create_documentation_sheet(self):
        """Create technical documentation sheet."""
        ws = self.wb.create_sheet("Documentation")

        # Title
        ws.merge_cells("B2:G2")
        ws["B2"] = "TECHNICAL DOCUMENTATION"
        ws["B2"].font = Font(size=16, bold=True, color="1F4E79")

        # Model overview
        ws["B4"] = "MODEL OVERVIEW"
        ws["B4"].font = Font(size=12, bold=True)

        overview = [
            "This Budget Impact Model (BIM) estimates the financial impact of introducing",
            "IXA-001 to a healthcare plan's formulary for treating resistant hypertension.",
            "",
            "The model compares a 'Current World' (no IXA-001) to a 'New World' (with IXA-001)",
            "over a 5-year time horizon, calculating the incremental budget impact.",
        ]
        for i, line in enumerate(overview):
            ws[f"B{5+i}"] = line

        # Key assumptions
        ws["B12"] = "KEY ASSUMPTIONS"
        ws["B12"].font = Font(size=12, bold=True)

        assumptions = [
            "1. Population remains stable over the analysis period",
            "2. Treatment costs are applied for full year per patient",
            "3. IXA-001 displaces existing treatments according to specified proportions",
            "4. Avoided CV events are calculated from linked CEA model results",
            "5. No discounting applied (standard for BIM)",
            "6. Treatment adherence and discontinuation not explicitly modeled",
        ]
        for i, assumption in enumerate(assumptions):
            ws[f"B{13+i}"] = assumption

        # Data sources
        ws["B21"] = "DATA SOURCES"
        ws["B21"].font = Font(size=12, bold=True)

        sources = [
            ("Epidemiology", "NHANES, ESC Guidelines, Carey et al. Circulation 2018"),
            ("Drug Costs", "RED BOOK/WAC (US), BNF/MIMS (UK)"),
            ("Medical Costs", "CMS Fee Schedule (US), NHS Reference Costs (UK)"),
            ("Market Shares", "IQVIA, Symphony Health, Internal market research"),
            ("CV Event Rates", "Linked IXA-001 Cost-Effectiveness Model"),
        ]

        headers = ["Category", "Source"]
        for i, header in enumerate(headers):
            ws.cell(row=22, column=i+2, value=header).style = "header_style"

        for i, (cat, source) in enumerate(sources):
            row = 23 + i
            ws.cell(row=row, column=2, value=cat)
            ws.cell(row=row, column=3, value=source)

        # Limitations
        ws["B30"] = "LIMITATIONS"
        ws["B30"].font = Font(size=12, bold=True)

        limitations = [
            "- Model does not capture indirect costs (productivity loss)",
            "- Market dynamics may differ from assumed displacement patterns",
            "- Avoided event calculations based on clinical trial populations",
            "- Real-world adherence may differ from assumptions",
        ]
        for i, limitation in enumerate(limitations):
            ws[f"B{31+i}"] = limitation

        # Contact
        ws["B37"] = "MODEL CONTACT"
        ws["B37"].font = Font(size=12, bold=True)
        ws["B38"] = "For questions about this model, contact:"
        ws["B39"] = "Atlantis Pharmaceuticals - HEOR Team"

        # Set column widths
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 60
