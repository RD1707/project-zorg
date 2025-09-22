#!/usr/bin/env python3
"""
Script para executar todos os testes do ZORG.
"""
import subprocess
import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Executa todos os testes."""
    try:
        # Executar pytest com configuração completa
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "--tb=short",
            "--cov=core",
            "--cov=data",
            "--cov=scenes",
            "--cov=screens",
            "--cov=utils",
            "--cov=widgets",
            "--cov-report=term-missing",
            "--cov-report=html",
            "tests/",
        ]

        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode

    except Exception as e:
        print(f"Erro ao executar testes: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
