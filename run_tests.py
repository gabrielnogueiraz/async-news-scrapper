#!/usr/bin/env python
import sys
import subprocess


def run_tests():
    """Execute a suite completa de testes com cobertura."""
    print("🧪 Executando testes...\n")
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Todos os testes passaram!")
        print("📊 Relatório de cobertura gerado em: htmlcov/index.html")
    else:
        print("\n❌ Alguns testes falharam!")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
