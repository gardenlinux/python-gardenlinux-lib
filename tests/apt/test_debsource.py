import io

from gardenlinux.apt import DebsrcFile

test_data = """Package: vim
Source: vim (2:9.1.0496-1)
Version: 2:9.1.0496-1+b1
Architecture: amd64
Maintainer: Debian Vim Maintainers <team+vim@tracker.debian.org>
Installed-Size: 3788
Depends: vim-common (= 2:9.1.0496-1), vim-runtime (= 2:9.1.0496-1), libacl1 (>= 2.2.23), libc6 (>= 2.38), libgpm2 (>= 1.20.7), libselinux1 (>= 3.1~), libsodium23 (>= 1.0.14), libtinfo6 (>= 6)
Suggests: ctags, vim-doc, vim-scripts
Provides: editor
Filename: pool/d4e0296c516812e2038ff3574f99af7c1a4810612598c3360cb99de61e047011/vim_2%3a9.1.0496-1+b1_amd64.deb
Size: 1619492
MD5sum: 65a0123a1fc76cf7695d90030f5e80d2
SHA1: b0aebce641b3c708235d940f50b1627b5fd42f99
SHA256: d4e0296c516812e2038ff3574f99af7c1a4810612598c3360cb99de61e047011
Section: editors
Priority: optional
Homepage: https://www.vim.org/
Description: Vi IMproved - enhanced vi editor
 This is a sample description.
 .
 It can have multiple lines.
 .

Package: vim-common
Source: vim
Version: 2:9.1.0496-1
Architecture: all
Maintainer: Debian Vim Maintainers <team+vim@tracker.debian.org>
Installed-Size: 1850
Recommends: xxd, vim | vim-gtk3 | vim-motif | vim-nox | vim-tiny
Breaks: vim-runtime (<< 2:9.0.1658-1~)
Replaces: vim-runtime (<< 2:9.0.1658-1~)
Filename: pool/3eb851c9789f075d9e1dbdd721d40e5c6d0e835776518f66fd4335e0bb6f1f61/vim-common_2%3a9.1.0496-1_all.deb
Size: 411852
MD5sum: 259c2baa838b5325829c88dbf583bf2b
SHA1: 2b7252742fb40dff8ce3abbc6c54730a3e519b2f
SHA256: 3eb851c9789f075d9e1dbdd721d40e5c6d0e835776518f66fd4335e0bb6f1f61
Section: editors
Priority: important
Multi-Arch: foreign
Homepage: https://www.vim.org/
Description: Vi IMproved - Common files

Package: vim-runtime
Source: vim
Version: 2:9.1.0496-1
Architecture: all
Maintainer: Debian Vim Maintainers <team+vim@tracker.debian.org>
Installed-Size: 36945
Recommends: vim | vim-gtk3 | vim-motif | vim-nox | vim-tiny
Enhances: vim-tiny
Breaks: vim-tiny (<< 2:9.1.0496-1)
Filename: pool/488a128a939e430f681230ef9fd83b371585f0e0d3cf7649f135270133b5b162/vim-runtime_2%3a9.1.0496-1_all.deb
Size: 7116680
MD5sum: a2e9e7a7907644444b7555eb6b23ce59
SHA1: 330bb657c0249504a3114f56cd70848bee5e7270
SHA256: 488a128a939e430f681230ef9fd83b371585f0e0d3cf7649f135270133b5b162
Section: editors
Priority: optional
Multi-Arch: foreign
Homepage: https://www.vim.org/
Description: Vi IMproved - Runtime files

Package: vim-tiny
Source: vim (2:9.1.0496-1)
Version: 2:9.1.0496-1+b1
Architecture: amd64
Maintainer: Debian Vim Maintainers <team+vim@tracker.debian.org>
Installed-Size: 1750
Depends: vim-common (= 2:9.1.0496-1), libacl1 (>= 2.2.23), libc6 (>= 2.34), libselinux1 (>= 3.1~), libtinfo6 (>= 6)
Suggests: indent
Provides: editor
Filename: pool/a44d841ab0ba4dcea6da764126fbfa351642a913920ad15a10781239e4297e27/vim-tiny_2%3a9.1.0496-1+b1_amd64.deb
Size: 743340
MD5sum: 518f5bb267de52be4613a9eaac5325fb
SHA1: 5bc3956b165fd36a7da185ed3962afc7d0957d53
SHA256: a44d841ab0ba4dcea6da764126fbfa351642a913920ad15a10781239e4297e27
Section: editors
Priority: important
Homepage: https://www.vim.org/
Description: Vi IMproved - enhanced vi editor - compact version
"""


def test_parse_debsource_file():
    expected = sorted(
        [
            "vim-common 2:9.1.0496-1",
            "vim-runtime 2:9.1.0496-1",
            "vim-tiny 2:9.1.0496-1+b1",
            "vim 2:9.1.0496-1+b1",
        ]
    )
    unit_under_test = DebsrcFile()

    unit_under_test.read(io.StringIO(test_data))

    # Explicitly sort list for comparison because the order is not deterministic
    actual = sorted([f"{f'{package!r}'}" for package in unit_under_test.values()])
    assert expected == actual
