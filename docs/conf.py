# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

project = "Beekeeper"
copyright = "2025, Leonardo Furnielis"
author = "Leonardo Furnielis"
version = "0.7.4"
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

"""Setup project path for sphinx"""
sys.path.insert(0, os.path.abspath("../pineflow-core"))
base_ext_dir = os.path.abspath('../pineflow-extensions')

# Add every subdirectory that contains a `pineflow/` package to sys.path from extensions
for root, dirs, files in os.walk(base_ext_dir):
    if 'pineflow' in dirs:
        pineflow_path = os.path.join(root)
        sys.path.insert(0, pineflow_path)

extensions = [
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_favicon"
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".idea"]

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autoclass_content

autoclass_content = "class"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_typehints_description_target = "documented"
autodoc_class_signature = "separated"
autodoc_default_options = {"exclude-members": "__init__"}
autodoc_mock_imports = ["litellm"]

# -- Options for Sphinx Favicon -------------------------------------------------
# https://sphinx-favicon.readthedocs.io/en/latest/index.html

favicons = [
    "favicon-32x32.png",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_title = "Beekeeper"
html_last_updated_fmt = "%b %d, %Y"
html_copy_source = False
html_show_sourcelink = False

html_theme_options = {
    "light_css_variables": {
        "font-stack": "Montserrat, -apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif",
        "font-stack--monospace": "'IBM Plex Mono', 'SFMono-Regular', Menlo, Consolas, Lucida Console, monospace",
    },
    "footer_icons": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/beekeeper-ai/",
            "html": """
                <svg version="1.1" xmlns="http://www.w3.org/2000/svg"  stroke="currentColor" fill="currentColor" stroke-width="0" width="16px" height="16" viewBox="0 0 512 512">
                    <path d="M454,305.8294373l-91.1191101,33.691803v106.4807434L181.94487,512V298.2970276l179.8842926-66.8633728V58.8240128L454,92.4968643V305.8294373z M276.8390503,363.3849487c-15.7174377,5.7245483-28.4572144,23.9239502-28.4515686,40.6481018c0.0061646,16.7174377,12.7523499,25.6329346,28.4636841,19.919281c15.7173462-5.7247009,28.4602051-23.9217834,28.4544983-40.6459656C305.303009,366.5810547,292.5565491,357.6635437,276.8390503,363.3849487z M334.6160889,212.4997864l-180.3925323,66.8782959l0.2966461,135.7604065l-64.2104874,22.9912415L0,405.2594604V191.9265442l90.704361-33.6917877V51.7543259L232.9717102,0l101.6443787,32.4636765V212.4997864z M215.2144775,94.8330383c-15.7174835,5.7222672-28.4621582,23.9249802-28.458725,40.6499329c0.0025787,16.725235,12.750824,25.6462555,28.4683228,19.9248505c15.7174988-5.7219086,28.4623871-23.9248047,28.4592285-40.6498184C243.6806641,98.0326996,230.9319763,89.1116333,215.2144775,94.8330383z"/>
                </svg>
            """,
            "class": "",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/run-pineflow/pineflow",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

# -- Options for Python domain -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-python-domain

add_module_names = False

# -- Display method signatures without the class name prefix -------------------

# def setup(app):
#     from sphinx.ext.autodoc import MethodDocumenter 
    
#     # Override format_signature to remove class prefix from methods
#     original_format_signature = MethodDocumenter.format_signature

#     def custom_format_signature(self, *args, **kwargs):
#         sig = original_format_signature(self, *args, **kwargs)
#         # Prevent Sphinx from adding 'ClassName.' to method name
#         self.objpath = [self.objpath[-1]]  # Keep only the method name
#         return sig

#     MethodDocumenter.format_signature = custom_format_signature
