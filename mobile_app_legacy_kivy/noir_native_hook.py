"""
p4a hook: noir_native_hook.py
Injects NoirNativeService, NoirBootReceiver, NoirProjectionActivity
into the Android build via python-for-android's recipe system.
"""
import os
import shutil
from pythonforandroid.toolchain import current_directory


def hook(ctx, arch, recipe, build_dir, *args, **kwargs):
    """Called by p4a after Java compilation phase."""

    # Source Java directory (relative to mobile_app/)
    java_src = os.path.join(os.path.dirname(__file__), "java")

    # Destination inside the p4a build tree
    java_dst = os.path.join(
        build_dir, "src", "main", "java", "org", "noir", "sovereign"
    )
    os.makedirs(java_dst, exist_ok=True)

    for fname in os.listdir(os.path.join(java_src, "org", "noir", "sovereign")):
        src = os.path.join(java_src, "org", "noir", "sovereign", fname)
        dst = os.path.join(java_dst, fname)
        shutil.copy2(src, dst)
        print(f"[NoirHook] Copied {fname} -> {dst}")
