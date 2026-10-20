from __future__ import annotations

import csv
import json
import math
import re
import unittest
import xml.etree.ElementTree as ET
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "specs.csv"
SPECS = ROOT / "data" / "processed" / "specs_limpas.csv"
RECALLS = ROOT / "data" / "processed" / "nhtsa_recalls.csv"
FINAL = ROOT / "data" / "processed" / "bmw_m_performance_fiabilidade.csv"
REJECTED = ROOT / "data" / "staging" / "rejeitados_specs.csv"
JSON_OUTPUT = ROOT / "data" / "output" / "bmw_m_catalogo_completo.json"
XML_OUTPUT = ROOT / "data" / "output" / "bmw_m_resumo_series.xml"
FIXTURES = ROOT / "tests" / "fixtures" / "nhtsa"

INT_FIELDS = {"year", "engine_hp", "weight_kg", "engine_cc", "price_usd", "nhtsa_recalls_count"}
FLOAT_FIELDS = {
    "zero_to_sixty_mph",
    "peso_ton",
    "litros",
    "hp_por_tonelada",
    "hp_por_litro",
    "recalls_por_100hp",
}
REQUIRED_FINAL_FIELDS = {
    "make",
    "model",
    "year",
    "engine_hp",
    "weight_kg",
    "zero_to_sixty_mph",
    "engine_cc",
    "price_usd",
    "versao",
    "model_prefix",
    "peso_ton",
    "litros",
    "hp_por_tonelada",
    "hp_por_litro",
    "series",
    "body_type",
    "nhtsa_recalls_count",
    "recalls_por_100hp",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def nullable_number(value: str, cast):
    return None if value == "" else cast(value)


def classify_nhtsa(status: int | None, body: str | None, error: str | None = None):
    """Espelho independente das regras documentadas em T2, usado com fixtures."""
    if error == "timeout":
        return None, "TIMEOUT"
    if status is None:
        return None, "SEM_STATUS_HTTP"
    if not 200 <= status < 300:
        return None, f"ERRO_HTTP_{status}"
    try:
        payload = json.loads(body or "")
    except json.JSONDecodeError:
        return None, "JSON_INVALIDO"
    if not isinstance(payload, dict) or "Count" not in payload:
        return None, "COUNT_AUSENTE"
    count = payload["Count"]
    if isinstance(count, bool) or not isinstance(count, (int, float)):
        return None, "COUNT_INVALIDO"
    if not math.isfinite(count) or count < 0 or int(count) != count:
        return None, "COUNT_INVALIDO"
    count = int(count)
    return count, "OK_ZERO" if count == 0 else "OK"


class DataQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = read_csv(RAW)
        cls.specs = read_csv(SPECS)
        cls.recalls = read_csv(RECALLS)
        cls.final = read_csv(FINAL)
        cls.rejected = read_csv(REJECTED)

    def test_csv_structure_and_counts(self):
        self.assertEqual(29, len(self.raw))
        self.assertEqual(28, len(self.specs))
        self.assertEqual(28, len(self.recalls))
        self.assertEqual(28, len(self.final))
        self.assertEqual(REQUIRED_FINAL_FIELDS, set(self.final[0]))

    def test_valid_models_match_raw_minus_quarantine(self):
        raw_keys = {(r["make"].strip().upper(), r["model"].strip(), r["year"]) for r in self.raw}
        rejected_keys = {(r["make"].strip().upper(), r["model"].strip(), r["year"]) for r in self.rejected}
        final_keys = {(r["make"], r["model"], r["year"]) for r in self.final}
        self.assertEqual(raw_keys - rejected_keys, final_keys)

    def test_rejected_record_is_preserved(self):
        self.assertEqual(1, len(self.rejected))
        row = self.rejected[0]
        self.assertEqual(("M3 E92 GTS", "2010", ""), (row["model"], row["year"], row["weight_kg"]))

    def test_no_source_or_final_duplicates(self):
        raw_keys = [(r["make"].strip().upper(), r["model"].strip(), r["year"]) for r in self.raw]
        final_keys = [(r["make"], r["model"], r["year"]) for r in self.final]
        self.assertEqual(len(raw_keys), len(set(raw_keys)))
        self.assertEqual(len(final_keys), len(set(final_keys)))

    def test_artificial_duplicate_is_removed_by_key(self):
        rows = self.raw + [dict(self.raw[0])]
        unique = {}
        for row in rows:
            key = (row["make"].strip().upper(), row["model"].strip(), row["year"])
            unique.setdefault(key, row)
        self.assertEqual(30, len(rows))
        self.assertEqual(29, len(unique))

    def test_required_values_and_ranges(self):
        for row in self.final:
            for field in REQUIRED_FINAL_FIELDS - {"price_usd", "nhtsa_recalls_count", "recalls_por_100hp"}:
                self.assertNotEqual("", row[field], f"{row['model']}: {field}")
            self.assertGreater(int(row["weight_kg"]), 0)
            self.assertGreater(int(row["engine_hp"]), 0)
            self.assertGreater(int(row["engine_cc"]), 0)
            self.assertGreaterEqual(int(row["year"]), 1886)
            self.assertLessEqual(int(row["year"]), 2100)

    def test_mechanical_calculations(self):
        for row in self.final:
            hp = Decimal(row["engine_hp"])
            kg = Decimal(row["weight_kg"])
            cc = Decimal(row["engine_cc"])
            self.assertAlmostEqual(float(kg / Decimal(1000)), float(row["peso_ton"]), delta=0.011)
            self.assertAlmostEqual(float(cc / Decimal(1000)), float(row["litros"]), delta=0.011)
            self.assertAlmostEqual(float(hp / (kg / Decimal(1000))), float(row["hp_por_tonelada"]), delta=0.011)
            self.assertAlmostEqual(float(hp / (cc / Decimal(1000))), float(row["hp_por_litro"]), delta=0.011)

    def test_recall_calculation_and_null_semantics(self):
        recall_by_key = {(r["make"], r["model"], r["year"]): r for r in self.recalls}
        for row in self.final:
            source = recall_by_key[(row["make"], row["model_prefix"], row["year"])]
            if source["nhtsa_query_status"] in {"OK", "OK_ZERO"}:
                self.assertNotEqual("", row["nhtsa_recalls_count"])
                expected = Decimal(row["nhtsa_recalls_count"]) / Decimal(row["engine_hp"]) * Decimal(100)
                self.assertAlmostEqual(float(expected), float(row["recalls_por_100hp"]), delta=0.011)
            else:
                self.assertEqual("", row["nhtsa_recalls_count"])
                self.assertEqual("", row["recalls_por_100hp"])

    def test_m5_e34_price_remains_null(self):
        row = next(r for r in self.final if r["model"] == "M5 E34")
        self.assertEqual("", row["price_usd"])


class OutputConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.final = read_csv(FINAL)
        with JSON_OUTPUT.open(encoding="utf-8") as stream:
            cls.catalog = json.load(stream)["catalogo_bmw_m"]
        cls.xml_root = ET.parse(XML_OUTPUT).getroot()

    def test_json_matches_consolidated_csv(self):
        csv_by_key = {(r["model"], int(r["year"])): r for r in self.final}
        json_by_key = {(r["model"], r["year"]): r for r in self.catalog}
        self.assertEqual(set(csv_by_key), set(json_by_key))
        for key, csv_row in csv_by_key.items():
            json_row = json_by_key[key]
            self.assertEqual(REQUIRED_FINAL_FIELDS, set(json_row))
            for field in REQUIRED_FINAL_FIELDS:
                if field in INT_FIELDS:
                    expected = nullable_number(csv_row[field], int)
                elif field in FLOAT_FIELDS:
                    expected = nullable_number(csv_row[field], float)
                else:
                    expected = csv_row[field]
                self.assertEqual(expected, json_row[field], f"{key}: {field}")

    def test_xml_aggregates_and_decimal_power_means(self):
        grouped = defaultdict(list)
        for row in self.final:
            grouped[row["series"]].append(row)
        xml_by_series = {node.findtext("series"): node for node in self.xml_root.findall("serie_analise")}
        self.assertEqual(set(grouped), set(xml_by_series))
        expected_power = {
            "Série 2 M": "422.50",
            "Série 3 M": "395.00",
            "Série 4 M": "487.75",
            "Série 5 M": "503.75",
            "Série 6 M": "533.50",
            "Série 8 M": "600.00",
        }
        for series, rows in grouped.items():
            node = xml_by_series[series]
            self.assertEqual(len(rows), int(node.findtext("total_modelos")))
            valid = [r for r in rows if r["nhtsa_recalls_count"] != ""]
            self.assertEqual(len(valid), int(node.findtext("modelos_com_resposta_nhtsa")))
            mean_hp = sum(Decimal(r["engine_hp"]) for r in rows) / Decimal(len(rows))
            self.assertEqual(mean_hp, Decimal(node.findtext("media_hp")))
            self.assertEqual(expected_power[series], node.findtext("media_hp"))
            if valid:
                self.assertEqual(sum(int(r["nhtsa_recalls_count"]) for r in valid), int(node.findtext("total_recalls_serie")))
                mean_recall = sum(Decimal(r["recalls_por_100hp"]) for r in valid) / Decimal(len(valid))
                self.assertAlmostEqual(float(mean_recall), float(node.findtext("media_recalls_100hp")), delta=0.00011)
            else:
                self.assertIn(node.findtext("total_recalls_serie"), {None, ""})
                self.assertIn(node.findtext("media_recalls_100hp"), {None, ""})


class KettleStructureTests(unittest.TestCase):
    def test_all_kettle_files_are_well_formed_and_hops_exist(self):
        paths = sorted((ROOT / "kettle" / "transformations").glob("*.ktr"))
        paths += sorted((ROOT / "kettle" / "jobs").glob("*.kjb"))
        self.assertEqual(6, len(paths))
        for path in paths:
            root = ET.parse(path).getroot()
            if path.suffix == ".ktr":
                steps = {step.findtext("name") for step in root.findall("step")}
                for hop in root.findall("./order/hop"):
                    self.assertIn(hop.findtext("from"), steps, path.name)
                    self.assertIn(hop.findtext("to"), steps, path.name)

    def test_t1_quality_rules_and_deduplication_are_configured(self):
        root = ET.parse(ROOT / "kettle" / "transformations" / "T1_extract_specs.ktr").getroot()
        steps = {s.findtext("name"): s for s in root.findall("step")}
        self.assertEqual("Unique", steps["Remover duplicados"].findtext("type"))
        self.assertEqual(["make", "model", "year"], [n.findtext("name") for n in steps["Remover duplicados"].findall("./fields/field")])
        validation_xml = ET.tostring(steps["Validar campos obrigatorios"], encoding="unicode")
        for field in ("weight_kg", "engine_hp", "engine_cc", "year"):
            self.assertIn(field, validation_xml)
        self.assertIn("Validar lookup series", steps)

    def test_nhtsa_validation_and_null_preservation_are_configured(self):
        t2 = ET.parse(ROOT / "kettle" / "transformations" / "T2_extract_nhtsa.ktr").getroot()
        script = next(s for s in t2.findall("step") if s.findtext("name") == "Validar resposta NHTSA")
        source = script.findtext("./jsScripts/jsScript/jsScript_script") or ""
        for state in ("ERRO_HTTP_", "JSON_INVALIDO", "COUNT_AUSENTE", "COUNT_INVALIDO", "OK_ZERO"):
            self.assertIn(state, source)
        t3 = ET.parse(ROOT / "kettle" / "transformations" / "T3_consolidate_metrics.ktr").getroot()
        self.assertNotIn("Tratar recalls nulos", {s.findtext("name") for s in t3.findall("step")})

    def test_postgres_has_no_versioned_secret_and_uses_upsert(self):
        for name in ("T4_load_postgres.ktr", "T5_export_reports.ktr"):
            root = ET.parse(ROOT / "kettle" / "transformations" / name).getroot()
            connection = root.find("connection")
            self.assertEqual("${PGPASSWORD}", connection.findtext("password"))
            self.assertEqual("${PGHOST}", connection.findtext("server"))
        t4 = ET.parse(ROOT / "kettle" / "transformations" / "T4_load_postgres.ktr").getroot()
        load = next(s for s in t4.findall("step") if s.findtext("name") == "Carregar PostgreSQL")
        self.assertEqual("InsertUpdate", load.findtext("type"))
        self.assertIsNone(load.find("truncate"))

    def test_t5_uses_decimal_input_for_average(self):
        root = ET.parse(ROOT / "kettle" / "transformations" / "T5_export_reports.ktr").getroot()
        table = next(s for s in root.findall("step") if s.findtext("name") == "Ler PostgreSQL")
        group = next(s for s in root.findall("step") if s.findtext("name") == "Agregar por Serie")
        output = next(s for s in root.findall("step") if s.findtext("name") == "Exportar Resumo XML")
        self.assertIn("CAST(engine_hp AS NUMERIC(10,2)) AS engine_hp_agregacao", table.findtext("sql"))
        media = next(f for f in group.findall("./fields/field") if f.findtext("aggregate") == "media_hp")
        self.assertEqual("engine_hp_agregacao", media.findtext("subject"))
        media_out = next(f for f in output.findall("./fields/field") if f.findtext("name") == "media_hp")
        self.assertEqual("0.00", media_out.findtext("format"))
        json_output = next(s for s in root.findall("step") if s.findtext("name") == "Exportar Catalogo JSON")
        self.assertEqual("Y", json_output.findtext("./file/DoNotOpenNewFileInit"))
        self.assertEqual("Y", output.findtext("./file/do_not_open_newfile_init"))

    def test_report_image_references_exist(self):
        report = (ROOT / "docs" / "relatorio_final.md").read_text(encoding="utf-8")
        references = re.findall(r"!\[[^]]*\]\(([^)]+)\)", report)
        self.assertGreater(len(references), 0)
        for reference in references:
            self.assertTrue((ROOT / "docs" / reference).resolve().is_file(), reference)


class NhtsaFixtureTests(unittest.TestCase):
    def fixture(self, name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8")

    def test_valid_positive(self):
        self.assertEqual((3, "OK"), classify_nhtsa(200, self.fixture("valid_positive.json")))

    def test_valid_zero_is_distinct(self):
        self.assertEqual((0, "OK_ZERO"), classify_nhtsa(200, self.fixture("valid_zero.json")))

    def test_http_error_does_not_become_zero(self):
        self.assertEqual((None, "ERRO_HTTP_500"), classify_nhtsa(500, self.fixture("valid_zero.json")))

    def test_invalid_json(self):
        self.assertEqual((None, "JSON_INVALIDO"), classify_nhtsa(200, self.fixture("invalid_json.txt")))

    def test_missing_and_invalid_count(self):
        self.assertEqual((None, "COUNT_AUSENTE"), classify_nhtsa(200, self.fixture("missing_count.json")))
        self.assertEqual((None, "COUNT_INVALIDO"), classify_nhtsa(200, self.fixture("invalid_count.json")))

    def test_timeout(self):
        self.assertEqual((None, "TIMEOUT"), classify_nhtsa(None, None, error="timeout"))


if __name__ == "__main__":
    unittest.main()
