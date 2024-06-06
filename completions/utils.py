import subprocess
import sys

def run_code(code : str) -> dict[str, str | None | bool]:
    proc = subprocess.Popen(
    [sys.executable, './completions/sandbox.py', code],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    )
    is_timed_out = False
    try:
        stdout, stderr = proc.communicate(None, timeout=10)
    except subprocess.TimeoutExpired:
        is_timed_out = True
        proc.kill()
        stdout, stderr = proc.communicate()
    return {
        'is_correct': (not stderr) and (not is_timed_out),
        'errors': stderr.decode(),
    }
