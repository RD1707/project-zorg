#!/usr/bin/env python3
"""
Script para verificar a qualidade do código ZORG.
"""
import sys
import subprocess
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_black():
    """Executa formatação com Black."""
    print("Executando formatacao com Black...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "black",
            "--line-length", "88",
            "."
        ], cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("Black: Formatacao concluida")
        else:
            print(f"Black: {result.stderr}")
        return result.returncode
    except Exception as e:
        print(f"Erro ao executar Black: {e}")
        return 1

def run_isort():
    """Executa organização de imports com isort."""
    print("Organizando imports com isort...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "isort",
            "--profile", "black",
            "."
        ], cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("isort: Imports organizados")
        else:
            print(f"isort: {result.stderr}")
        return result.returncode
    except Exception as e:
        print(f"Erro ao executar isort: {e}")
        return 1

def run_flake8():
    """Executa verificação de estilo com flake8."""
    print("Verificando estilo com flake8...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "flake8",
            "--max-line-length", "88",
            "--extend-ignore", "E203,W503",
            "."
        ], cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("flake8: Nenhum problema encontrado")
        else:
            print(f"AVISO - flake8: Problemas encontrados:\n{result.stdout}")
        return result.returncode
    except Exception as e:
        print(f"Erro ao executar flake8: {e}")
        return 1

def run_mypy():
    """Executa verificação de tipos com mypy."""
    print("Verificando tipos com mypy...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "mypy",
            "--ignore-missing-imports",
            "--follow-imports", "silent",
            "core/", "data/", "scenes/", "screens/", "utils/", "widgets/"
        ], cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("mypy: Verificacao de tipos passou")
        else:
            print(f"AVISO - mypy: Problemas de tipo encontrados:\n{result.stdout}")
        return result.returncode
    except Exception as e:
        print(f"Erro ao executar mypy: {e}")
        return 1

def main():
    """Executa todas as verificações de qualidade."""
    print("Iniciando verificacoes de qualidade do codigo ZORG\n")

    exit_codes = []

    # Formatação automática
    exit_codes.append(run_black())
    exit_codes.append(run_isort())

    print()

    # Verificações
    exit_codes.append(run_flake8())
    exit_codes.append(run_mypy())

    print("\nResumo:")

    if all(code == 0 for code in exit_codes):
        print("Todas as verificacoes passaram!")
        return 0
    else:
        failed_checks = sum(1 for code in exit_codes if code != 0)
        print(f"{failed_checks} verificacao(oes) falharam")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)