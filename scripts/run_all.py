import subprocess
import sys

def run(script):
    print(f"\n▶ Running {script}")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(f"❌ Failed: {script}")

run("scripts/live_engine.py")
run("scripts/trust_signal.py")
run("scripts/discover_signal.py")
run("generators/build_articles.py")

print("\n✅ All PureStill engines completed successfully")
