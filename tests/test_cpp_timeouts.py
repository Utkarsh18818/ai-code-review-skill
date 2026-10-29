import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.cpp_benchmark import load_cases
from scripts.run_cpp_benchmark import run


class TimeoutEvidenceTests(unittest.TestCase):
    def invoke(self, directory, responses, cases=None):
        if cases is None:
            cases = [load_cases()[0]]
        with patch("scripts.run_cpp_benchmark.sys.platform", "linux"), \
             patch("scripts.run_cpp_benchmark.shutil.which", return_value="clang++"), \
             patch("scripts.run_cpp_benchmark.load_cases", return_value=cases), \
             patch("scripts.run_cpp_benchmark.execute", side_effect=responses) as execute, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = run(directory, "clang++")
        report = json.loads((Path(directory) / "results.json").read_text(encoding="utf-8"))
        return status, report, execute.call_count

    def version(self):
        return subprocess.CompletedProcess(["clang++", "--version"], 0, "test compiler", "")

    def built(self):
        return subprocess.CompletedProcess(["clang++"], 0, "build output", "")

    def test_build_timeout_preserves_bytes_and_phase(self):
        error = subprocess.TimeoutExpired(["clang++"], 30,
                                          output=b"partial output\xff\n", stderr=b"compiler diagnostic\n")
        with tempfile.TemporaryDirectory() as directory:
            status, report, calls = self.invoke(directory, [self.version(), error])
            record = report["cases"][0]
            log = (Path(directory) / record["diagnostic_log"]).read_text(encoding="utf-8")
            self.assertIn("partial output\ufffd", log)
            self.assertIn("compiler diagnostic", log)
            self.assertFalse((Path(directory) / "n01-run.log").exists())
        self.assertEqual(status, 1)
        self.assertFalse(report["passed"])
        self.assertFalse(record["verified"])
        self.assertEqual(record["failure_phase"], "build")
        self.assertTrue(record["timed_out"])
        self.assertEqual(record["timeout_seconds"], 30)
        self.assertEqual(calls, 2)

    def test_run_timeout_preserves_text_and_phase(self):
        error = subprocess.TimeoutExpired(["case"], 5,
                                          output="partial program output\n", stderr="sanitizer diagnostic\n")
        with tempfile.TemporaryDirectory() as directory:
            status, report, calls = self.invoke(directory, [self.version(), self.built(), error])
            record = report["cases"][0]
            log = (Path(directory) / record["diagnostic_log"]).read_text(encoding="utf-8")
            self.assertIn("partial program output", log)
            self.assertIn("sanitizer diagnostic", log)
            self.assertEqual((Path(directory) / "n01-build.log").read_text(encoding="utf-8"), "build output")
        self.assertEqual(status, 1)
        self.assertFalse(record["verified"])
        self.assertEqual(record["failure_phase"], "run")
        self.assertTrue(record["timed_out"])
        self.assertEqual(record["timeout_seconds"], 5)
        self.assertNotIn("run_exit", record)
        self.assertEqual(calls, 3)

    def test_empty_timeout_output_still_writes_log_and_continues(self):
        cases = [load_cases()[0], load_cases()[1]]
        error = subprocess.TimeoutExpired(["clang++"], 30)
        clean = subprocess.CompletedProcess(["case"], 0, "", "")
        with tempfile.TemporaryDirectory() as directory:
            status, report, calls = self.invoke(directory, [self.version(), error, self.built(), clean], cases)
            self.assertEqual((Path(directory) / "n01-build.log").read_text(encoding="utf-8"), "")
        self.assertEqual(status, 1)
        self.assertTrue(report["complete"])
        self.assertFalse(report["passed"])
        self.assertFalse(report["cases"][0]["verified"])
        self.assertTrue(report["cases"][1]["verified"])
        self.assertEqual(calls, 4)

    def test_compiler_version_timeout_preserves_evidence(self):
        error = subprocess.TimeoutExpired(["clang++", "--version"], 10, stderr=b"toolchain diagnostic")
        with tempfile.TemporaryDirectory() as directory:
            status, report, calls = self.invoke(directory, [error])
            log = (Path(directory) / report["diagnostic_log"]).read_text(encoding="utf-8")
            self.assertEqual(log, "toolchain diagnostic")
        self.assertEqual(status, 1)
        self.assertFalse(report["complete"])
        self.assertFalse(report["passed"])
        self.assertEqual(report["failure_phase"], "compiler-version")
        self.assertTrue(report["timed_out"])
        self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
