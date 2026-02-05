# -*- coding: utf-8 -*-


class CodeFileMixin(object):
    def __init__(self, executable=None, header_code=None, footer_code=None):
        self._code = []
        self._executable = executable
        self._footer_code = footer_code
        self._header_code = header_code

    @property
    def content(self):
        content = ""

        if len(self._code) > 0:
            if self._executable is not None:
                content += f"#!{self._executable}\n\n"

            if self._header_code is not None:
                content += self._header_code + "\n"

            for code in self._code:
                content += f"\n{code}\n"

            if self._footer_code is not None:
                content += "\n" + self._footer_code

        return content.strip() + "\n"

    @property
    def empty(self):
        return len(self._code) < 1

    def add_code(self, content):
        self._code.append(content.strip())
