import pathlib
import shutil
import subprocess
import tempfile

from gardenlinux.build.exporter import export

arm64 = {'usr', 'usr/lib', 'usr/lib/aarch64-linux-gnu', 'usr/lib/aarch64-linux-gnu/ld-linux-aarch64.so.1', 'usr/lib/aarch64-linux-gnu/libc.so.6', 'usr/lib/aarch64-linux-gnu/libpthread.so.0'}
amd64 = {'usr', 'usr/lib', 'usr/lib/x86_64-linux-gnu', 'usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'usr/lib/x86_64-linux-gnu/libc.so.6', 'usr/lib/x86_64-linux-gnu/libpthread.so.0'}

def test_requests_export():
    dpkg = shutil.which("dpkg")
    assert dpkg
    
    out = subprocess.run([dpkg, "--print-architecture"], stdout=subprocess.PIPE)
    assert out.returncode == 0
    arch = out.stdout.decode().strip()

    with tempfile.TemporaryDirectory() as target_dir:
        target_dir = pathlib.Path(target_dir)
        site_packages = target_dir.joinpath("site-packages")
        required_libs = target_dir.joinpath("required_libs")

        site_packages.mkdir()
        required_libs.mkdir()

        pip3 = shutil.which("pip3")
        assert pip3

        out = subprocess.run([pip3, "install", "--target", site_packages, "requests"])

        assert out.returncode == 0

        export(required_libs, site_packages)

        exported = set()

        for path in required_libs.rglob("*"):
            exported.add(str(path.relative_to(required_libs)))

        if arch == "arm64":
            expected = arm64
        elif arch == "amd64":
            expected = amd64
        else:
            raise NotImplementedError(f"Architecture {arch} not supported")

        assert exported == expected