# -*- coding: utf-8 -*-

from collections import OrderedDict
import textwrap

from .debian_file_mixin import DebianFileMixin


class RulesFile(DebianFileMixin):
    def __init__(self):
        DebianFileMixin.__init__(self)

        self._hooks = OrderedDict()

    def add_hook(self, hook, content):
        hook = hook.lower()

        if hook in self._hooks:
            self._hooks[hook] += "\n\n"
        else:
            self._hooks[hook] = ""

        self._hooks[hook] += content.strip()

    @property
    def content(self):
        additional_hooks = "\n"

        for hook, content in self._hooks.items():
            content = textwrap.indent(content, "\t")
            additional_hooks += f"{hook}:\n{content}\n"

        content = f"""
#!/usr/bin/make -f
{additional_hooks}
%:
	dh $@
        """

        return content.strip() + "\n"

    def generate(self, target_dir):
        self._generate(target_dir, "rules", self.content, 0o777)
