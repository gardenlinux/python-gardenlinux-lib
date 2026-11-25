from typing import Any

from sphinx.application import Sphinx


def _register_relative_headings(app: Sphinx) -> None:
    try:
        from sphinx_markdown_builder.contexts import TitleContext
        from sphinx_markdown_builder.translator import (
            MarkdownTranslator,
            pushing_context,
        )
    except ImportError:
        return

    class SectionRelativeMarkdownTranslator(MarkdownTranslator):  # type: ignore[misc]
        """Render rubric and signature headings relative to their section.

        sphinx-markdown-builder pins these headings to level 3 while section
        titles use their absolute nesting depth. Nested sphinx-click and
        sphinxcontrib-autoprogram sections then jump from level 3 to 5, which
        breaks the aggregated documentation (gldq HEAD-SKIP).
        """

        @pushing_context
        def visit_rubric(self, _node: Any) -> None:
            self._push_context(TitleContext(self.status.section_level + 1))

        @pushing_context
        def visit_desc_signature(self, node: Any) -> None:
            if self.config.markdown_anchor_signatures:
                for anchor in node.get("ids", []):
                    self._add_anchor(anchor)
            level = self.status.section_level + 1
            if node.get("class"):
                level += 1
            self._push_context(TitleContext(level))

    app.set_translator("markdown", SectionRelativeMarkdownTranslator, override=True)


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Garden Linux Python Library"
copyright = "2024, Garden Linux Maintainers"
author = "Garden Linux Maintainers"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx_rtd_theme",
    "sphinx.ext.napoleon",
    "sphinxcontrib.autoprogram",
    "sphinx_markdown_builder",
]

# Markdown builder configuration (GitHub-Flavored Markdown for VitePress)
# We can enable this after https://github.com/liran-funaro/sphinx-markdown-builder/pull/53 is merged
# markdown_flavor = "github"
markdown_anchor_sections = True
markdown_anchor_signatures = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc_mock_imports = ["networkx"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Logo configuration
html_logo = "_static/gardenlinux-logo.svg"

html_theme_options = {
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#027154",  # Primary green
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}


# Add custom CSS
def setup(app: Sphinx) -> None:
    app.add_css_file("custom.css")
    _register_relative_headings(app)
