"""
Streamlit Web Interface for Budget Impact Model.

Provides an interactive web application for running BIM analysis with:
- Country and scenario selection
- Population and cost inputs
- Subgroup analysis options
- Real-time calculation
- Chart visualizations
- Excel download options
"""

import streamlit as st
import numpy as np
from io import BytesIO
from typing import Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bim import (
    BIMInputs,
    ExtendedBIMInputs,
    BIMCalculator,
    EnhancedBIMCalculator,
    ExcelGenerator,
    EnhancedExcelGenerator,
    UptakeScenario,
    SubgroupType,
    COUNTRY_CONFIGS,
)

# Page configuration
st.set_page_config(
    page_title="Budget Impact Model - IXA-001",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1F4E79;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .positive-impact {
        color: #dc3545;
    }
    .negative-impact {
        color: #28a745;
    }
</style>
""", unsafe_allow_html=True)


def format_currency(value: float, symbol: str) -> str:
    """Format currency value with symbol and thousands separator."""
    if abs(value) >= 1_000_000:
        return f"{symbol}{value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"{symbol}{value/1_000:,.1f}K"
    else:
        return f"{symbol}{value:,.0f}"


def create_sidebar_inputs() -> ExtendedBIMInputs:
    """Create sidebar with all input controls."""
    st.sidebar.markdown("## 📊 Model Inputs")

    # Country selection
    st.sidebar.markdown("### 🌍 Country")
    country_options = {
        "US": "United States",
        "UK": "United Kingdom",
        "DE": "Germany",
        "FR": "France",
        "IT": "Italy",
        "ES": "Spain",
    }
    selected_country = st.sidebar.selectbox(
        "Select Country",
        options=list(country_options.keys()),
        format_func=lambda x: country_options[x],
        index=0,
    )

    # Create inputs for selected country
    inputs = ExtendedBIMInputs.for_country(selected_country)

    # Scenario selection
    st.sidebar.markdown("### 📈 Scenario")
    scenario_options = {
        UptakeScenario.CONSERVATIVE: "Conservative",
        UptakeScenario.MODERATE: "Moderate",
        UptakeScenario.OPTIMISTIC: "Optimistic",
    }
    selected_scenario = st.sidebar.selectbox(
        "Uptake Scenario",
        options=list(scenario_options.keys()),
        format_func=lambda x: scenario_options[x],
        index=1,  # Default to Moderate
    )
    inputs.selected_scenario = selected_scenario

    # Population inputs
    st.sidebar.markdown("### 👥 Population")

    inputs.population.total_population = st.sidebar.slider(
        "Total Plan Population",
        min_value=100_000,
        max_value=10_000_000,
        value=inputs.population.total_population,
        step=100_000,
        format="%d",
    )

    inputs.population.hypertension_prevalence = st.sidebar.slider(
        "Hypertension Prevalence (%)",
        min_value=15.0,
        max_value=50.0,
        value=inputs.population.hypertension_prevalence * 100,
        step=1.0,
    ) / 100

    inputs.population.resistant_htn_proportion = st.sidebar.slider(
        "Resistant HTN (% of HTN)",
        min_value=5.0,
        max_value=25.0,
        value=inputs.population.resistant_htn_proportion * 100,
        step=1.0,
    ) / 100

    inputs.population.uncontrolled_proportion = st.sidebar.slider(
        "Uncontrolled (% of Resistant)",
        min_value=30.0,
        max_value=80.0,
        value=inputs.population.uncontrolled_proportion * 100,
        step=5.0,
    ) / 100

    # Cost inputs
    st.sidebar.markdown("### 💰 Costs (Annual)")
    currency = inputs.country.currency_symbol

    inputs.costs.ixa_001_annual = st.sidebar.number_input(
        f"IXA-001 Drug Cost ({currency})",
        min_value=1000.0,
        max_value=20000.0,
        value=float(inputs.costs.ixa_001_annual),
        step=500.0,
    )

    inputs.costs.spironolactone_annual = st.sidebar.number_input(
        f"Spironolactone Cost ({currency})",
        min_value=50.0,
        max_value=1000.0,
        value=float(inputs.costs.spironolactone_annual),
        step=10.0,
    )

    # Subgroup selection
    st.sidebar.markdown("### 📊 Subgroup Analysis")

    enable_subgroups = st.sidebar.checkbox("Enable Subgroup Analysis", value=False)
    if enable_subgroups:
        subgroup_options = {
            SubgroupType.AGE: "Age Groups",
            SubgroupType.CKD_STAGE: "CKD Stage",
            SubgroupType.PRIOR_CV: "Prior CV Events",
            SubgroupType.DIABETES: "Diabetes Status",
            SubgroupType.PRIMARY_ALDOSTERONISM: "Primary Aldosteronism (IXA-001 Target)",
            SubgroupType.SECONDARY_HTN_ETIOLOGY: "Secondary HTN Etiology (Treatment Response)",
        }

        selected_subgroups = st.sidebar.multiselect(
            "Select Subgroups",
            options=list(subgroup_options.keys()),
            format_func=lambda x: subgroup_options[x],
            default=[SubgroupType.AGE],
        )
        inputs.selected_subgroup_types = selected_subgroups
    else:
        inputs.selected_subgroup_types = []

    # Analysis options
    st.sidebar.markdown("### ⚙️ Analysis Options")

    inputs.include_persistence = st.sidebar.checkbox(
        "Model Treatment Persistence",
        value=False,
    )

    inputs.include_events = st.sidebar.checkbox(
        "Include Event Analysis",
        value=True,
    )

    return inputs


def display_key_metrics(results, currency_symbol: str):
    """Display key metrics in a row of cards."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Eligible Patients",
            value=f"{results.total_eligible_patients:,}",
        )

    with col2:
        impact_5yr = results.total_budget_impact_5yr
        st.metric(
            label="5-Year Budget Impact",
            value=format_currency(impact_5yr, currency_symbol),
            delta=None,
        )

    with col3:
        st.metric(
            label="Average Annual Impact",
            value=format_currency(results.average_annual_impact, currency_symbol),
        )

    with col4:
        st.metric(
            label="Year 1 PMPM",
            value=f"{currency_symbol}{results.pmpm_impact_year1:.2f}",
        )

    with col5:
        st.metric(
            label="Year 5 PMPM",
            value=f"{currency_symbol}{results.pmpm_impact_year5:.2f}",
        )


def display_year_by_year_table(results, currency_symbol: str):
    """Display year-by-year results table."""
    st.markdown("### Year-by-Year Budget Impact")

    import pandas as pd

    data = []
    cumulative = 0
    for yr in results.yearly_results:
        cumulative += yr.budget_impact
        data.append({
            "Year": yr.year,
            "IXA-001 Patients": yr.patients_ixa_001,
            "IXA-001 Share": f"{yr.share_ixa_001:.1%}",
            "Current World": f"{currency_symbol}{yr.cost_current_world:,.0f}",
            "New World": f"{currency_symbol}{yr.cost_new_world:,.0f}",
            "Budget Impact": f"{currency_symbol}{yr.budget_impact:,.0f}",
            "Cumulative": f"{currency_symbol}{cumulative:,.0f}",
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_budget_impact_chart(results, currency_symbol: str):
    """Display budget impact bar chart."""
    import pandas as pd

    st.markdown("### Budget Impact Visualization")

    col1, col2 = st.columns(2)

    with col1:
        # Bar chart for annual impact
        chart_data = pd.DataFrame({
            "Year": [f"Year {yr.year}" for yr in results.yearly_results],
            "Budget Impact": [yr.budget_impact for yr in results.yearly_results],
        })
        st.bar_chart(chart_data.set_index("Year"), use_container_width=True)

    with col2:
        # Market share evolution
        share_data = pd.DataFrame({
            "Year": [f"Year {yr.year}" for yr in results.yearly_results],
            "IXA-001": [yr.share_ixa_001 for yr in results.yearly_results],
            "Spironolactone": [yr.share_spironolactone for yr in results.yearly_results],
            "Other MRA": [yr.share_other_mra for yr in results.yearly_results],
            "No Treatment": [yr.share_no_treatment for yr in results.yearly_results],
        })
        st.area_chart(share_data.set_index("Year"), use_container_width=True)


def display_scenario_comparison(inputs: ExtendedBIMInputs):
    """Display comparison across all scenarios."""
    st.markdown("### Scenario Comparison")

    calculator = BIMCalculator(inputs)
    all_results = calculator.run_all_scenarios()

    import pandas as pd

    currency = inputs.country.currency_symbol
    data = []
    for scenario in UptakeScenario:
        res = all_results[scenario]
        data.append({
            "Scenario": scenario.value.capitalize(),
            "5-Year Impact": f"{currency}{res.total_budget_impact_5yr:,.0f}",
            "Avg Annual": f"{currency}{res.average_annual_impact:,.0f}",
            "Year 1 PMPM": f"{currency}{res.pmpm_impact_year1:.2f}",
            "Year 5 PMPM": f"{currency}{res.pmpm_impact_year5:.2f}",
            "Year 5 Patients": res.yearly_results[-1].patients_ixa_001 if res.yearly_results else 0,
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Comparison chart
    impacts = [all_results[s].total_budget_impact_5yr for s in UptakeScenario]
    chart_df = pd.DataFrame({
        "Scenario": [s.value.capitalize() for s in UptakeScenario],
        "5-Year Impact": impacts,
    })
    st.bar_chart(chart_df.set_index("Scenario"), use_container_width=True)


def display_subgroup_results(extended_results, currency_symbol: str):
    """Display subgroup analysis results."""
    if not extended_results.subgroup_results:
        return

    st.markdown("### Subgroup Analysis")

    import pandas as pd

    for subgroup_type, results_list in extended_results.subgroup_results.items():
        st.markdown(f"**{subgroup_type.value.title()} Subgroups**")

        data = []
        for sg in results_list:
            data.append({
                "Subgroup": sg.subgroup_name,
                "Patients": sg.patients,
                "Proportion": f"{sg.proportion:.1%}",
                "5-Year Impact": f"{currency_symbol}{sg.budget_impact_5yr:,.0f}",
                "Per Patient": f"{currency_symbol}{sg.budget_impact_per_patient:,.0f}",
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def display_event_analysis(extended_results, currency_symbol: str):
    """Display event analysis results."""
    if not extended_results.event_results:
        return

    st.markdown("### Events Avoided (5-Year)")

    import pandas as pd

    events = extended_results.event_results
    data = []

    event_labels = {
        "stroke": "Stroke",
        "mi": "MI",
        "hf": "HF Hospitalization",
        "ckd": "CKD Progression",
        "esrd": "ESRD",
    }

    for event_type, avoided in events.events_avoided.items():
        if avoided != 0:
            cost = events.event_costs.get(event_type, 0)
            label = event_labels.get(event_type.value, event_type.value)
            data.append({
                "Event Type": label,
                "Events Avoided": f"{avoided:,.1f}",
                "Cost Avoided": f"{currency_symbol}{cost:,.0f}",
            })

    if data:
        data.append({
            "Event Type": "TOTAL",
            "Events Avoided": f"{sum(events.events_avoided.values()):,.1f}",
            "Cost Avoided": f"{currency_symbol}{events.total_costs_avoided:,.0f}",
        })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def run_psa_analysis(inputs: ExtendedBIMInputs, iterations: int = 500):
    """Run PSA with progress bar."""
    st.markdown("### Probabilistic Sensitivity Analysis")

    progress_bar = st.progress(0)
    status_text = st.empty()

    calculator = EnhancedBIMCalculator(inputs)

    # Run PSA in chunks to update progress
    chunk_size = 50
    all_impacts = []

    for i in range(0, iterations, chunk_size):
        chunk_iterations = min(chunk_size, iterations - i)
        psa_results = calculator.run_probabilistic_sensitivity(
            iterations=chunk_iterations,
            seed=i,  # Different seed for each chunk
        )
        all_impacts.extend(psa_results.impact_distribution)

        progress = min(1.0, (i + chunk_size) / iterations)
        progress_bar.progress(progress)
        status_text.text(f"Running iteration {min(i + chunk_size, iterations)}/{iterations}...")

    progress_bar.empty()
    status_text.empty()

    # Calculate final statistics
    impacts = np.array(all_impacts)
    currency = inputs.country.currency_symbol

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mean Impact", format_currency(np.mean(impacts), currency))

    with col2:
        ci_low = np.percentile(impacts, 2.5)
        ci_high = np.percentile(impacts, 97.5)
        st.metric("95% CI Lower", format_currency(ci_low, currency))

    with col3:
        st.metric("95% CI Upper", format_currency(ci_high, currency))

    # Histogram
    import pandas as pd
    hist_df = pd.DataFrame({"Budget Impact": impacts})
    st.markdown("**Distribution of Results**")
    st.line_chart(pd.DataFrame({
        "Impact": np.sort(impacts)
    }))


def generate_excel_download(inputs: ExtendedBIMInputs, extended_results) -> BytesIO:
    """Generate Excel file and return as bytes."""
    import tempfile
    import os

    # Create a temporary file to generate the Excel
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Generate the full Excel workbook with all sheets
        generator = EnhancedExcelGenerator(inputs, extended_results)
        generator.generate(tmp_path)

        # Read the generated file into a BytesIO buffer
        buffer = BytesIO()
        with open(tmp_path, 'rb') as f:
            buffer.write(f.read())
        buffer.seek(0)

        return buffer
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def main():
    """Main application entry point."""
    # Header with version
    st.markdown('<p class="main-header">Budget Impact Model</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">IXA-001 for Resistant Hypertension</p>', unsafe_allow_html=True)

    # Version header with feature badges
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1F4E79 0%, #2E86AB 100%); padding: 0.8rem 1.2rem; border-radius: 8px; margin-bottom: 1rem;">
        <span style="color: white; font-weight: bold;">v4.0</span>
        <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 10px;">Dual-Branch Phenotyping</span>
        <span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 5px;">Secondary HTN Etiology</span>
        <span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 5px;">PA Target Population</span>
    </div>
    """, unsafe_allow_html=True)

    # Budget Impact Model Architecture Diagram
    with st.expander("📐 Budget Impact Model Architecture", expanded=False):
        st.markdown("""
        This diagram shows the complete Budget Impact Model structure, from eligible population
        identification through market share evolution to final budget impact calculation.
        """)
        diagram_path = Path(__file__).parent / "docs" / "bim_diagram_vertical.png"
        if diagram_path.exists():
            st.image(str(diagram_path), use_container_width=True)
        else:
            st.warning("Model diagram not found. Please ensure docs/bim_diagram_vertical.png exists.")

        st.markdown("""
        **Key Model Components:**

        | Component | Description |
        |-----------|-------------|
        | **Population Funnel** | Filters total plan population through HTN prevalence → Resistant HTN → Uncontrolled |
        | **Subgroup Stratification** | Segments by secondary HTN etiology (PA, OSA, RAS, Essential) and risk factors |
        | **Uptake Scenarios** | Conservative (15%), Moderate (30%), Optimistic (45%) Year-5 market share |
        | **Market Evolution** | Tracks shift from current world (no IXA-001) to new world across 5 years |
        | **Cost Components** | Drug costs (IXA-001 vs Spironolactone) + Event costs (MI, Stroke, HF, ESRD) |
        | **Budget Calculation** | New World costs − Current World costs = Net Budget Impact |
        """)

    # Create sidebar inputs
    inputs = create_sidebar_inputs()

    # Run calculation
    calculator = EnhancedBIMCalculator(inputs)
    extended_results = calculator.calculate_full(
        include_subgroups=len(inputs.selected_subgroup_types) > 0,
        include_persistence=inputs.include_persistence,
        include_events=inputs.include_events,
        include_extended_horizon=True,
    )

    base_results = extended_results.base_results
    currency_symbol = inputs.country.currency_symbol

    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Results",
        "📈 Scenarios",
        "👥 Subgroups",
        "🏥 Events",
        "🎲 PSA",
        "🧬 HTN Etiology"
    ])

    with tab1:
        # Key metrics
        display_key_metrics(base_results, currency_symbol)

        st.divider()

        # Year-by-year table
        display_year_by_year_table(base_results, currency_symbol)

        st.divider()

        # Charts
        display_budget_impact_chart(base_results, currency_symbol)

    with tab2:
        display_scenario_comparison(inputs)

    with tab3:
        if inputs.selected_subgroup_types:
            display_subgroup_results(extended_results, currency_symbol)
        else:
            st.info("Enable subgroup analysis in the sidebar to see stratified results.")

    with tab4:
        if inputs.include_events and extended_results.event_results:
            display_event_analysis(extended_results, currency_symbol)

            st.markdown("### Event Rates (per 1,000 patient-years)")
            import pandas as pd

            rates = inputs.event_rates
            rate_data = {
                "Event": ["Stroke", "MI", "HF", "CKD", "ESRD"],
                "IXA-001": [rates.stroke_ixa_001, rates.mi_ixa_001, rates.hf_ixa_001,
                           rates.ckd_ixa_001, rates.esrd_ixa_001],
                "Spironolactone": [rates.stroke_spironolactone, rates.mi_spironolactone,
                                   rates.hf_spironolactone, rates.ckd_spironolactone,
                                   rates.esrd_spironolactone],
                "No Treatment": [rates.stroke_no_treatment, rates.mi_no_treatment,
                                rates.hf_no_treatment, rates.ckd_no_treatment,
                                rates.esrd_no_treatment],
            }
            st.dataframe(pd.DataFrame(rate_data), use_container_width=True, hide_index=True)
        else:
            st.info("Enable event analysis in the sidebar to see clinical outcomes.")

    with tab5:
        st.markdown("""
        Probabilistic Sensitivity Analysis (PSA) varies all uncertain parameters
        simultaneously using Monte Carlo simulation to characterize uncertainty
        in the budget impact estimate.
        """)

        psa_iterations = st.slider(
            "Number of Iterations",
            min_value=100,
            max_value=2000,
            value=500,
            step=100,
        )

        if st.button("Run PSA", type="primary"):
            run_psa_analysis(inputs, psa_iterations)

    with tab6:
        st.markdown("### Secondary Hypertension Etiology Analysis")

        st.markdown("""
        The model stratifies patients by secondary hypertension etiology to capture
        differential treatment responses to IXA-001. Each etiology has a unique
        treatment effect modifier that adjusts the expected clinical benefit.
        """)

        import pandas as pd

        # Treatment response modifiers table
        st.markdown("#### Treatment Response Modifiers by Etiology")
        etiology_data = pd.DataFrame({
            "Etiology": ["Primary Aldosteronism (PA)", "Renal Artery Stenosis (RAS)",
                        "Pheochromocytoma (Pheo)", "Obstructive Sleep Apnea (OSA)", "Essential HTN"],
            "IXA-001 Response": ["1.70× (Enhanced)", "1.05× (Slight)", "0.40× (Contraindicated)",
                                "1.20× (Moderate)", "1.00× (Baseline)"],
            "Rationale": [
                "Direct aldosterone pathway targeting - optimal response",
                "Renovascular cause - limited benefit from MRA",
                "Catecholamine-driven - MRA contraindicated",
                "Aldosterone elevation common - moderate benefit",
                "Standard response - no specific enhancement"
            ],
            "Prevalence": ["8-12%", "2-5%", "0.1-0.6%", "30-50%", "~50%"]
        })
        st.dataframe(etiology_data, use_container_width=True, hide_index=True)

        st.markdown("---")

        # PA-specific risk modifiers
        st.markdown("#### Primary Aldosteronism Baseline Risk Modifiers")
        st.markdown("""
        Patients with PA have elevated baseline risk for cardiovascular and renal events
        due to direct aldosterone-mediated organ damage (independent of BP).
        """)

        pa_risk_data = pd.DataFrame({
            "Event": ["Myocardial Infarction", "Stroke", "Heart Failure", "ESRD", "Atrial Fibrillation", "CV Death"],
            "Risk Multiplier": ["1.40×", "1.50×", "2.05×", "1.80×", "3.00×", "1.60×"],
            "Source": ["Monticone 2018", "Monticone 2018", "Monticone 2018", "Model estimate", "Monticone 2018", "Model estimate"]
        })
        st.dataframe(pa_risk_data, use_container_width=True, hide_index=True)

        st.info("""
        💡 **Budget Impact Implication**: PA patients represent the highest-value subgroup for IXA-001
        due to their elevated baseline event risk combined with enhanced treatment response (1.70×).
        Events avoided in this population generate substantial cost offsets.
        """)

    # Download section
    st.divider()
    st.markdown("### 📥 Download Results")

    col1, col2 = st.columns(2)

    with col1:
        # Run tornado analysis for Excel
        extended_results.tornado_results = calculator.run_tornado_analysis()

        # Run PSA for Excel (smaller iteration count for speed)
        extended_results.psa_results = calculator.run_probabilistic_sensitivity(
            iterations=500, seed=42
        )

        # Generate Excel
        excel_buffer = generate_excel_download(inputs, extended_results)

        st.download_button(
            label="Download Enhanced Excel Report",
            data=excel_buffer,
            file_name=f"BIM_Report_{inputs.country.country_code}_{inputs.selected_scenario.value}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col2:
        st.markdown("""
        **Excel Report Includes:**
        - Input Dashboard
        - Results Dashboard
        - Scenario Comparison
        - Tornado Diagram
        - Subgroup Analysis
        - 10-Year Projection
        - Event Analysis
        - PSA Results
        """)


if __name__ == "__main__":
    main()
