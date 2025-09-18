import ast
from pathlib import Path


def test_no_legacy_pydantic_config_classes():
    """Fail if any Pydantic model declares an inner class named Config.

    This guards against reintroducing deprecated V1-style `class Config:` blocks.
    Allowed exceptions: none (update here if a non-BaseModel inner class named Config is ever required).
    """
    project_root = Path(__file__).resolve().parent.parent
    offenders: list[str] = []

    for py_file in project_root.rglob("*.py"):
        # Skip virtual environment or hidden dirs if somehow inside root
        parts = {p for p in py_file.parts}
        if any(x.startswith(".") for x in parts) or ".venv" in parts:
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        class_stack: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Config":
                # Try to detect parent model class by looking upward in source text (simpler than scope resolution)
                offenders.append(str(py_file))

    assert not offenders, (
        "Deprecated Pydantic inner Config classes found in files:\n" + "\n".join(sorted(offenders))
    )
