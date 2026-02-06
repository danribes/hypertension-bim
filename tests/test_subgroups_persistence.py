"""
Tests for SubgroupDefinitions and TreatmentPersistence.

Validates subgroup proportion sums, PA treatment effect modifiers,
and persistence/discontinuation calculations.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import (
    SubgroupDefinitions,
    SubgroupType,
    TreatmentPersistence,
)


class TestSubgroupProportions:
    """Test that subgroup proportions sum to 1.0 within each type."""

    def test_age_proportions_sum(self):
        """Age subgroup proportions should sum to 1.0: 0.35+0.40+0.25."""
        sg = SubgroupDefinitions()
        age = sg.get_subgroups(SubgroupType.AGE)
        total = sum(s.proportion for s in age)
        proportions = [s.proportion for s in age]
        print(f"Age proportions: {proportions}, sum = {total}")
        assert abs(total - 1.0) < 0.01

    def test_ckd_proportions_sum(self):
        """CKD subgroup proportions should sum to 1.0: 0.50+0.35+0.15."""
        sg = SubgroupDefinitions()
        ckd = sg.get_subgroups(SubgroupType.CKD_STAGE)
        total = sum(s.proportion for s in ckd)
        proportions = [s.proportion for s in ckd]
        print(f"CKD proportions: {proportions}, sum = {total}")
        assert abs(total - 1.0) < 0.01

    def test_pa_proportions_sum(self):
        """PA subgroup proportions should sum to 1.0: 0.83+0.17."""
        sg = SubgroupDefinitions()
        pa = sg.get_subgroups(SubgroupType.PRIMARY_ALDOSTERONISM)
        total = sum(s.proportion for s in pa)
        proportions = [s.proportion for s in pa]
        print(f"PA proportions: {proportions}, sum = {total}")
        assert abs(total - 1.0) < 0.01

    def test_secondary_htn_proportions_sum(self):
        """Secondary HTN proportions should sum to 1.0: 0.17+0.11+0.01+0.15+0.56."""
        sg = SubgroupDefinitions()
        sec = sg.get_subgroups(SubgroupType.SECONDARY_HTN_ETIOLOGY)
        total = sum(s.proportion for s in sec)
        proportions = [(s.code, s.proportion) for s in sec]
        print(f"Secondary HTN proportions: {proportions}, sum = {total}")
        assert abs(total - 1.0) < 0.01

    def test_prior_cv_proportions_sum(self):
        """Prior CV proportions should sum to 1.0: 0.70+0.30."""
        sg = SubgroupDefinitions()
        cv = sg.get_subgroups(SubgroupType.PRIOR_CV)
        total = sum(s.proportion for s in cv)
        print(f"Prior CV proportions: {[s.proportion for s in cv]}, sum = {total}")
        assert abs(total - 1.0) < 0.01

    def test_diabetes_proportions_sum(self):
        """Diabetes proportions should sum to 1.0: 0.55+0.45."""
        sg = SubgroupDefinitions()
        dm = sg.get_subgroups(SubgroupType.DIABETES)
        total = sum(s.proportion for s in dm)
        print(f"Diabetes proportions: {[s.proportion for s in dm]}, sum = {total}")
        assert abs(total - 1.0) < 0.01


class TestPATreatmentModifier:
    """Test PA-specific treatment effect modifiers."""

    def test_pa_treatment_effect_modifier(self):
        """PA subgroup treatment_effect_modifier should be 1.70."""
        sg = SubgroupDefinitions()
        pa_subgroups = sg.get_subgroups(SubgroupType.PRIMARY_ALDOSTERONISM)
        pa = [s for s in pa_subgroups if s.code == "with_primary_aldo"][0]
        print(f"PA treatment_effect_modifier: {pa.treatment_effect_modifier} (expected 1.70)")
        assert pa.treatment_effect_modifier == 1.70

    def test_pa_etiology_treatment_effect_modifier(self):
        """PA in secondary etiology should also have 1.70 modifier."""
        sg = SubgroupDefinitions()
        sec = sg.get_subgroups(SubgroupType.SECONDARY_HTN_ETIOLOGY)
        pa = [s for s in sec if s.code == "pa"][0]
        print(f"PA etiology modifier: {pa.treatment_effect_modifier} (expected 1.70)")
        assert pa.treatment_effect_modifier == 1.70


class TestTreatmentPersistence:
    """Test persistence and discontinuation calculations."""

    def test_ixa_persistence_year1(self):
        """IXA Year 1 persistence: (1-0.15) = 0.85."""
        tp = TreatmentPersistence()
        persistence = tp.get_persistence("ixa_001", 1)
        expected = 1 - 0.15
        print(f"IXA Year 1 persistence: {persistence} (expected {expected})")
        assert abs(persistence - expected) < 0.0001

    def test_ixa_persistence_year3(self):
        """IXA Year 3 persistence: 0.85 × 0.92 × 0.92 = 0.71944."""
        tp = TreatmentPersistence()
        persistence = tp.get_persistence("ixa_001", 3)
        expected = (1 - 0.15) * (1 - 0.08) * (1 - 0.08)  # 0.71944
        print(f"IXA Year 3 persistence: {persistence:.5f} (expected {expected:.5f})")
        assert abs(persistence - expected) < 0.0001

    def test_spiro_persistence_less_than_ixa(self):
        """Spiro persistence should be < IXA persistence for all years."""
        tp = TreatmentPersistence()
        for year in range(1, 6):
            ixa_p = tp.get_persistence("ixa_001", year)
            spiro_p = tp.get_persistence("spironolactone", year)
            print(f"Year {year}: IXA={ixa_p:.4f}, Spiro={spiro_p:.4f}")
            assert spiro_p < ixa_p, (
                f"Year {year}: Spiro ({spiro_p:.4f}) >= IXA ({ixa_p:.4f})"
            )

    def test_no_treatment_persistence_is_one(self):
        """No treatment should have persistence = 1.0 (no discontinuation)."""
        tp = TreatmentPersistence()
        for year in range(1, 6):
            persistence = tp.get_persistence("no_treatment", year)
            print(f"No treatment Year {year}: {persistence} (expected 1.0)")
            assert persistence == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
