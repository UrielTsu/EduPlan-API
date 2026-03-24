from pathlib import Path


def load_legacy_module(module_globals, *relative_parts):
    legacy_root = Path(__file__).resolve().parent.parent / "EduPlan-API"
    module_path = legacy_root.joinpath(*relative_parts)
    source = module_path.read_text(encoding="utf-8")
    exec(compile(source, str(module_path), "exec"), module_globals)