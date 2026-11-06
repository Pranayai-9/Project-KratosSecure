"""
Phase 3 Verification Suite: Adaptive Security Research and Digital Twin Engine
Tests:
1. Scenario Intelligence Combinatorial Generation (H x A x I x T x C, Levels 0-5, Seeds)
2. AAVA Multi-Round Escalating Adaptive Red-Team Campaign
3. Digital Twin Bottleneck Analysis & Counterfactual Simulation Studio
4. Comparative Experiment Profiles (Profiles A, B, C, D, E) & Matrix Evaluation
5. Research Behavioral Telemetry Datasets (Dataset A, Dataset B, Dataset C) & Export
6. Academic Research Report Generator (Markdown, JSON, CSV)
"""

import sys
import os
import json
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database import SessionLocal
from backend.app.agent.intelligence import ScenarioIntelligenceEngine
from backend.app.agent.aava import AAVA
from backend.app.services.calibration_service import CalibrationService
from backend.app.agent.experiments import ExperimentManagementEngine
from backend.app.services.report_generator import ResearchReportGenerator
from backend.app.models.research import (
    ExperimentRecord, CounterfactualSimulationRecord,
    BehavioralDataAgent, BehavioralDataEnvironment, BehavioralDataInteraction
)

def run_tests():
    db = SessionLocal()
    passed = 0
    failed = 0
    total = 7

    print("=" * 80)
    print("  KRATOSSECURE: PHASE 3 ADAPTIVE SECURITY RESEARCH & DIGITAL TWIN TEST SUITE")
    print("=" * 80)

    try:
        # TEST 1: Scenario Intelligence Combinatorial Generator
        print("\n[TEST 1/7] Testing Scenario Intelligence Generator (H x A x I x T x C)...")
        scen_lvl0 = ScenarioIntelligenceEngine.generate_scenario(difficulty_level=0, seed=1001)
        scen_lvl3 = ScenarioIntelligenceEngine.generate_scenario(difficulty_level=3, seed=1002)
        scen_lvl5 = ScenarioIntelligenceEngine.generate_scenario(difficulty_level=5, seed=1003)

        assert scen_lvl0.difficulty_level == 0
        assert scen_lvl0.dimensions.threat_condition == "NONE"
        assert scen_lvl5.difficulty_level == 5
        assert scen_lvl5.dimensions.hospital_state in ScenarioIntelligenceEngine.HOSPITAL_STATES
        assert len(scen_lvl5.dimensions.operational_constraints) > 0
        
        # Test seed reproducibility
        scen_repeat = ScenarioIntelligenceEngine.generate_scenario(difficulty_level=5, seed=1003)
        assert scen_repeat.title == scen_lvl5.title
        assert scen_repeat.dimensions.threat_condition == scen_lvl5.dimensions.threat_condition
        print("  -> PASSED: Combinatorial generation across levels 0-5 with deterministic seeds verified.")
        passed += 1

        # TEST 2: AAVA 4-Round Escalating Adaptive Red-Team Campaign
        print("\n[TEST 2/7] Testing AAVA 4-Round Escalating Adaptive Campaign...")
        campaign = AAVA.run_adaptive_campaign(db, target_patient_id=1, total_rounds=4)
        assert campaign["total_rounds_executed"] == 4
        assert len(campaign["rounds_history"]) == 4
        assert campaign["campaign_asr_percentage"] == 0.0
        assert campaign["resilience_verdict"] == "STRONG_RESILIENCE"
        for r in campaign["rounds_history"]:
            assert r["status"] in ["PASSED", "CONTAINED", "BLOCKED", "REFUSED"]
            assert "Round" in r["vector_name"]
        print(f"  -> PASSED: 4 adaptive rounds executed (Campaign ASR: {campaign['campaign_asr_percentage']}%).")
        passed += 1

        # TEST 3: Digital Twin Bottleneck Analysis
        print("\n[TEST 3/7] Testing Digital Twin Bottleneck & Operational Stress Assessment...")
        analysis = CalibrationService.analyze_bottlenecks(db)
        assert "overall_stress_score" in analysis
        assert "icu_saturation_percentage" in analysis
        assert "emergency_workload" in analysis
        assert isinstance(analysis["bottlenecks"], list)
        assert isinstance(analysis["recommended_mitigations"], list)
        print(f"  -> PASSED: Bottleneck assessment complete (Stress Score: {analysis['overall_stress_score']}/100, Level: {analysis['stress_level']}).")
        passed += 1

        # TEST 4: Counterfactual Infrastructure Simulation ("What-If" Studio)
        print("\n[TEST 4/7] Testing Counterfactual Simulation Engine...")
        params = {
            "icu_capacity_delta": 10,
            "ed_doctor_delta": 2,
            "lis_availability_pct": 100.0,
            "patient_arrival_multiplier": 1.4,
            "simulation_duration_hours": 24
        }
        cf_res = CalibrationService.run_counterfactual_simulation(db, params)
        assert "simulation_id" in cf_res
        assert cf_res["counterfactual_projections"]["projected_icu_occupancy_pct"] > 0
        assert "resilience_delta_score" in cf_res["counterfactual_projections"]
        
        # Verify persistence in database
        db_cf = db.query(CounterfactualSimulationRecord).filter(
            CounterfactualSimulationRecord.simulation_id == cf_res["simulation_id"]
        ).first()
        assert db_cf is not None
        assert db_cf.baseline_ed_wait_minutes > 0
        print(f"  -> PASSED: Simulation {cf_res['simulation_id']} executed & saved (Resilience Delta: +{cf_res['counterfactual_projections']['resilience_delta_score']}).")
        passed += 1

        # TEST 5: Comparative Experiment Profiles (A vs D vs E)
        print("\n[TEST 5/7] Testing Experiment Profiles & Comparative Matrix...")
        # Run Profile A (Insecure Baseline) on 5 test cases
        test_subset = ["TEST-01", "TEST-02", "TEST-03", "TEST-08", "TEST-15"]
        exp_a = ExperimentManagementEngine.run_experiment(db, "PROFILE_A", test_case_ids=test_subset)
        assert exp_a.attack_success_rate > 50.0  # Baseline should have high ASR
        assert exp_a.unauthorized_access_count > 0

        # Run Profile D (Full Zero-Trust Gateway + HITL)
        exp_d = ExperimentManagementEngine.run_experiment(db, "PROFILE_D", test_case_ids=test_subset)
        assert exp_d.attack_success_rate == 0.0  # Full security should block attacks
        assert exp_d.unauthorized_access_count == 0

        # Run Profile E (Adaptive Testing)
        exp_e = ExperimentManagementEngine.run_experiment(db, "PROFILE_E")
        assert exp_e.profile_code == "PROFILE_E"
        assert exp_e.attack_success_rate == 0.0

        # Comparative Matrix
        matrix_data = ExperimentManagementEngine.get_comparative_matrix(db)
        assert matrix_data["profiles_evaluated"] == 5
        assert matrix_data["asr_reduction_pct"] > 50.0
        print(f"  -> PASSED: Experiment Profiles verified (Profile A ASR: {exp_a.attack_success_rate}% vs Profile D ASR: {exp_d.attack_success_rate}%, ASR Reduction: -{matrix_data['asr_reduction_pct']}%).")
        passed += 1

        # TEST 6: Behavioral Telemetry Datasets (A, B, C) Export
        print("\n[TEST 6/7] Testing Research Behavioral Datasets A, B, and C Export...")
        agent_json, _ = ResearchReportGenerator.export_dataset(db, "agent", export_format="json")
        agent_csv, _ = ResearchReportGenerator.export_dataset(db, "agent", export_format="csv")
        env_csv, _ = ResearchReportGenerator.export_dataset(db, "environment", export_format="csv")
        int_csv, _ = ResearchReportGenerator.export_dataset(db, "interaction", export_format="csv")

        parsed_agent_json = json.loads(agent_json)
        assert len(parsed_agent_json) > 0
        assert "record_id" in parsed_agent_json[0]
        assert "agent_task" in parsed_agent_json[0]
        assert "record_id" in agent_csv
        assert "occupancy_rate" in env_csv
        assert "security_boundary_held" in int_csv
        print(f"  -> PASSED: Datasets A, B, and C serialized to JSON & CSV (Dataset A count: {len(parsed_agent_json)} records).")
        passed += 1

        # TEST 7: Academic Research Report Generator
        print("\n[TEST 7/7] Testing Research Benchmark Report Generation (Markdown, JSON, CSV)...")
        md_report, md_type = ResearchReportGenerator.generate_experiment_report(db, exp_d.experiment_id, report_format="markdown")
        json_report, json_type = ResearchReportGenerator.generate_experiment_report(db, exp_d.experiment_id, report_format="json")
        csv_report, csv_type = ResearchReportGenerator.generate_experiment_report(db, exp_d.experiment_id, report_format="csv")

        assert "# RESEARCH BENCHMARK REPORT" in md_report
        assert exp_d.experiment_id in md_report
        assert "Quantitative Performance Metrics" in md_report

        parsed_json_rep = json.loads(json_report)
        assert parsed_json_rep["experiment_id"] == exp_d.experiment_id
        assert "test_id" in csv_report
        print(f"  -> PASSED: Publication-grade report generated in Markdown ({len(md_report)} chars), JSON, and CSV.")
        passed += 1

    except Exception as e:
        print(f"\n❌ TEST SUITE FAILURE: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

    finally:
        db.close()

    print("\n" + "=" * 80)
    print(f"  PHASE 3 TEST SUMMARY: {passed}/{total} PASSED ({round((passed/total)*100, 1)}%)")
    print("=" * 80)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
