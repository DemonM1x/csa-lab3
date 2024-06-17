import contextlib
import io
import logging
import os
import tempfile
import pytest

import simulation
import translator


@pytest.mark.golden_test("golden_tests/*_golden.yml")
def test_golden(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.fr")
        input_file = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.json")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_file, "w", encoding="utf-8") as file:
            file.write(golden["input"])

        translator.main(source, target)
        with open(target, "r", encoding="utf-8") as file:
            code = file.read()
            assert code == golden["machine"]

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            simulation.main(target, input_file)
            assert stdout.getvalue() == golden["output"]

        proc_log = caplog.text.replace("\x00", " ")
        assert proc_log == golden["out_log"]
