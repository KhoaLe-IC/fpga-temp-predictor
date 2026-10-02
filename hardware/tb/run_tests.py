#!/usr/bin/env python3
"""Verilator DPI-C runner. Real RTL is mandatory unless --selftest is explicit."""
import argparse
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def run(command, *, expect_failure=False, reason=None, quiet=False):
    result = subprocess.run([str(x) for x in command], text=True, capture_output=True)
    if expect_failure:
        if result.returncode == 0 or not reason or reason not in result.stdout + result.stderr:
            raise RuntimeError(f"Fault escaped or failed for the wrong reason: {command}\n{result.stdout}{result.stderr}")
        print(f"Fault detected ({reason})")
    else:
        if result.returncode:
            raise RuntimeError(f"Command failed: {command}\n{result.stdout}{result.stderr}")
        if not quiet: print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    return result

def compare_replays(speed_path, resource_path):
    def load(path):
        with path.open() as stream:
            rows = list(csv.DictReader(stream))
        pairs = [(int(r["sample_index"]), int(r["prediction_raw"])) for r in rows]
        if not pairs or [i for i, _ in pairs] != list(range(25, 25 + len(pairs))):
            raise RuntimeError(f"EQUIVALENCE: empty, missing, duplicate or reordered results: {path}")
        return pairs
    speed, resource = load(speed_path), load(resource_path)
    if speed != resource:
        raise RuntimeError("EQUIVALENCE: speed/resource replay outputs differ by accepted-sample index")
    print(f"EQUIVALENCE PASS: {len(speed)} forecasts matched by accepted-sample index")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="Use behavioral stand-ins; does NOT verify RTL")
    parser.add_argument("--variant", choices=["speed", "resource", "both"], default="both")
    parser.add_argument("--rtl", nargs="+", type=Path, help="Real DUT source files, including dependencies")
    parser.add_argument("--model", type=Path, help="JSON trained a,b,c; quantize using spec rounding; overrides --a/--b/--c")
    parser.add_argument("--a", type=int, default=8192)
    parser.add_argument("--b", type=int, default=3277)
    parser.add_argument("--c", type=int, default=0)
    parser.add_argument("--speed-latency", type=int, default=5)
    parser.add_argument("--resource-latency", type=int, default=8)
    parser.add_argument("--no-dut-parameters", action="store_true", help="DUT has hard-coded coefficients; TB values must match")
    parser.add_argument("--matrix", action="store_true", help="Compile/run representative coefficient configurations")
    parser.add_argument("--vectors", type=Path, help="Replay existing vectors instead of generated synthetic C++ vectors")
    parser.add_argument("--build-dir", type=Path, default=HERE / "build")
    args = parser.parse_args()
    if args.selftest and args.rtl:
        parser.error("--selftest and --rtl are mutually exclusive")
    if not args.selftest and not args.rtl:
        parser.error("No DUT RTL exists by default. Supply --rtl files or explicitly use --selftest.")
    if args.no_dut_parameters and args.matrix:
        parser.error("A coefficient matrix requires configurable DUT coefficients")
    if args.vectors and args.matrix:
        parser.error("One external vector file cannot represent a coefficient matrix")
    for tool in ("verilator", "make", "g++"):
        if not shutil.which(tool): parser.error(f"Required executable missing: {tool}")
    sources = [HERE / "support/behavioral_duts.sv"] if args.selftest else [p.resolve() for p in args.rtl]
    for path in sources:
        if not path.is_file() or not path.stat().st_size:
            parser.error(f"Missing/empty DUT source: {path}")
    # Verilator uses abort on $fatal; avoid core dumps for intentional fault runs.
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0,0))
    except ImportError:
        pass
    build = args.build_dir.resolve(); build.mkdir(parents=True, exist_ok=True)
    bridge_test = build / "test_dpi_bridge"
    run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-O2",
         HERE / "support/test_dpi_bridge.cpp", HERE / "dpi/ols_dpi.cpp", "-o", bridge_test])
    run([bridge_test])
    generator = build / "generate_vectors"
    run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-O2",
         HERE / "support/generate_vectors.cpp", "-o", generator])
    variants = ["speed", "resource"] if args.variant == "both" else [args.variant]
    if args.model:
        model = json.loads(args.model.read_text())
        def quantize(value, fractional):
            scaled = float(value) * (1 << fractional)
            if not math.isfinite(scaled): parser.error("Nonfinite model coefficient")
            q = math.floor(abs(scaled) + 0.5) * (-1 if scaled < 0 else 1)
            if not -32768 <= q <= 32767: parser.error("Model coefficient outside spec range")
            return q
        args.a, args.b, args.c = [quantize(model[k], f) for k, f in (("a",14),("b",14),("c",8))]
        print(f"Trained model coefficients: A_Q={args.a} B_Q={args.b} C_Q={args.c}")
    coefficients = [(args.a,args.b,args.c)]
    if args.matrix:
        coefficients += [(0,0,0), (-32768,32767,-32768), (32767,-32768,32767), (1,-1,-1)]
    print("CHECKER SELF-TEST ONLY — behavioral stand-ins" if args.selftest else "REAL DUT VERIFICATION")
    fault_reasons = {"DATA":"DATA:", "EARLY":"LATENCY:", "DROP":"MISSING:",
                     "RESET_STALE":"RESET:", "READY":None}
    replay_results = {}
    for variant in variants:
        top = f"tb_temp_predictor_{variant}"
        latency = args.speed_latency if variant == "speed" else args.resource_latency
        if not 1 <= latency <= (8 if variant == "speed" else 10):
            parser.error("Latency outside specification ceiling")
        for index,(a,b,c) in enumerate(coefficients):
            objdir = build / f"{variant}_{index}_dpi"
            sim = objdir / "sim"
            vectors = args.vectors.resolve() if args.vectors else build / f"{variant}_{index}.txt"
            if not args.vectors: run([generator, vectors, a, b, c, 4096])
            command = ["verilator", "--binary", "--timing", "--trace", "--assert",
                       "-j", "2", "--top-module", top, "--Mdir", objdir, "-o", "sim",
                       "-CFLAGS", "-std=c++17", f"-GA_Q={a}", f"-GB_Q={b}",
                       f"-GC_Q={c}", f"-GLATENCY={latency}"]
            if args.no_dut_parameters: command.append("-DOLS_DUT_NO_PARAMETERS")
            if args.selftest:
                command += [f"-DOLS_MOCK_SPEED_LATENCY={args.speed_latency}",
                            f"-DOLS_MOCK_RESOURCE_LATENCY={args.resource_latency}"]
            command += [HERE / "ols_tb_driver.sv", HERE / f"{top}.sv", *sources,
                        HERE / "dpi/ols_dpi.cpp"]
            run(command, quiet=True)
            results_path = build / f"{variant}_{index}_results.csv"
            result = run([sim, f"+VECTORS={vectors}", f"+RESULTS={results_path}"])
            replay_results[(variant,index)] = results_path
            if "PASS:" not in result.stdout: raise RuntimeError("Simulation ended without PASS receipt")
            if args.selftest and index == 0:
                for mutation,reason in fault_reasons.items():
                    if mutation == "READY": reason = "READY:" if variant == "speed" else "BUSY:"
                    run([sim, f"+MUTATION={mutation}"], expect_failure=True, reason=reason)
    if args.variant == "both":
        for index in range(len(coefficients)):
            compare_replays(replay_results[("speed",index)], replay_results[("resource",index)])
    print("All checker self-tests passed. Real DUTs remain unverified." if args.selftest else "All requested DUT simulations passed.")

if __name__ == "__main__":
    try: main()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
