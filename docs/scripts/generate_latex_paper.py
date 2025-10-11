#!/usr/bin/env python3
"""
Generate journal-quality LaTeX paper from PolicyEngine documentation.

This script converts the policy documentation into a LaTeX format suitable
for academic journal submission, focusing on policy rules and parameters.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
from datetime import datetime


class LaTeXGenerator:
    def __init__(self, docs_dir: Path, output_dir: Path):
        self.docs_dir = docs_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # LaTeX document setup
        self.preamble = r"""
\documentclass[11pt,letterpaper]{article}

% Packages
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}
\usepackage[round]{natbib}
\usepackage{setspace}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{array}
\usepackage{enumitem}
\usepackage{fancyhdr}

% Formatting
\onehalfspacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{10pt}

% Headers
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{PolicyEngine US: A Comprehensive Policy Rules Database}
\renewcommand{\headrulewidth}{0.4pt}

% Custom commands
\newcommand{\dollar}[1]{\$#1}
\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}

% Hyperref setup
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=blue,
    urlcolor=blue,
    citecolor=blue
}

% Title information
\title{PolicyEngine US: A Comprehensive Database of Tax and Benefit Policy Rules}
\author{
    PolicyEngine Contributors\thanks{
        This documentation represents collaborative work by the PolicyEngine community.
        For the complete list of contributors, see \url{https://github.com/PolicyEngine/policyengine-us/graphs/contributors}.
    }
}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
This paper presents PolicyEngine US, a comprehensive microsimulation model and policy rules database 
covering federal and state tax and benefit programs in the United States. We document the structure 
and implementation of major programs including tax credits (EITC, CTC), health programs (Medicaid, CHIP), 
nutrition assistance (SNAP, WIC, School Meals), cash assistance (TANF, SSI), housing assistance, 
education grants (Pell), and utility assistance (Lifeline). The database provides researchers, policymakers, and 
financial institutions with machine-readable policy rules that can be used for distributional 
analysis, reform modeling, and understanding program interactions. All parameters are traced to primary 
legislative and regulatory sources, with historical values and current law projections.
\end{abstract}

\section{Introduction}

The United States operates a complex system of tax credits, deductions, and benefit programs across 
federal, state, and local jurisdictions. Understanding the interactions between these programs is 
crucial for policy analysis, yet the complexity and frequent changes make comprehensive modeling 
challenging. PolicyEngine US addresses this challenge by providing a unified, open-source framework 
for representing and computing tax and benefit rules.

This paper documents the policy rules encoded in PolicyEngine US, focusing on program parameters, 
eligibility criteria, benefit calculations, and cross-program interactions. We present this information 
in a format suitable for academic research, policy analysis, and institutional use.
"""

    def markdown_to_latex(self, content: str) -> str:
        """Convert markdown content to LaTeX format."""

        # Headers
        content = re.sub(
            r"^# (.+)$", r"\\section{\1}", content, flags=re.MULTILINE
        )
        content = re.sub(
            r"^## (.+)$", r"\\subsection{\1}", content, flags=re.MULTILINE
        )
        content = re.sub(
            r"^### (.+)$", r"\\subsubsection{\1}", content, flags=re.MULTILINE
        )
        content = re.sub(
            r"^#### (.+)$", r"\\paragraph{\1}", content, flags=re.MULTILINE
        )

        # Bold and italic
        content = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", content)
        content = re.sub(r"\*(.+?)\*", r"\\textit{\1}", content)

        # Lists
        content = self._convert_lists(content)

        # Tables
        content = self._convert_tables(content)

        # Code blocks
        content = self._convert_code_blocks(content)

        # Links
        content = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)", r"\\href{\2}{\1}", content
        )

        # Dollar amounts
        content = re.sub(r"\$([0-9,]+)", r"\\dollar{\1}", content)

        # Escape special characters
        for char in ["%", "&", "_"]:
            if char != "_" or not re.match(
                r"\\[a-zA-Z]+{[^}]*" + char, content
            ):
                content = content.replace(char, "\\" + char)

        return content

    def _convert_lists(self, content: str) -> str:
        """Convert markdown lists to LaTeX."""
        lines = content.split("\n")
        new_lines = []
        in_list = False
        list_stack = []

        for line in lines:
            # Numbered list
            if re.match(r"^\d+\.\s+", line):
                if not in_list or list_stack[-1] != "enumerate":
                    if in_list:
                        new_lines.append("\\end{" + list_stack.pop() + "}")
                    new_lines.append("\\begin{enumerate}")
                    list_stack.append("enumerate")
                    in_list = True
                item_text = re.sub(r"^\d+\.\s+", "", line)
                new_lines.append(f"\\item {item_text}")

            # Bullet list
            elif re.match(r"^[-*]\s+", line):
                if not in_list or list_stack[-1] != "itemize":
                    if in_list:
                        new_lines.append("\\end{" + list_stack.pop() + "}")
                    new_lines.append("\\begin{itemize}")
                    list_stack.append("itemize")
                    in_list = True
                item_text = re.sub(r"^[-*]\s+", "", line)
                new_lines.append(f"\\item {item_text}")

            # End of list
            elif in_list and line.strip() == "":
                while list_stack:
                    new_lines.append("\\end{" + list_stack.pop() + "}")
                in_list = False
                new_lines.append("")

            else:
                new_lines.append(line)

        # Close any remaining lists
        while list_stack:
            new_lines.append("\\end{" + list_stack.pop() + "}")

        return "\n".join(new_lines)

    def _convert_tables(self, content: str) -> str:
        """Convert markdown tables to LaTeX."""
        lines = content.split("\n")
        new_lines = []
        in_table = False
        table_lines = []

        for i, line in enumerate(lines):
            if "|" in line and not in_table:
                # Start of table
                in_table = True
                table_lines = [line]
            elif in_table and "|" in line:
                table_lines.append(line)
            elif in_table and "|" not in line:
                # End of table
                latex_table = self._process_table(table_lines)
                new_lines.extend(latex_table)
                new_lines.append(line)
                in_table = False
                table_lines = []
            else:
                new_lines.append(line)

        # Handle table at end of content
        if in_table and table_lines:
            latex_table = self._process_table(table_lines)
            new_lines.extend(latex_table)

        return "\n".join(new_lines)

    def _process_table(self, table_lines: List[str]) -> List[str]:
        """Process a single markdown table to LaTeX."""
        if len(table_lines) < 2:
            return table_lines

        # Parse table
        header_line = table_lines[0]
        headers = [cell.strip() for cell in header_line.split("|")[1:-1]]

        # Skip separator line
        data_lines = table_lines[2:] if len(table_lines) > 2 else []

        # Determine column alignment
        num_cols = len(headers)
        col_spec = "l" * num_cols

        # Build LaTeX table
        latex_lines = [
            "\\begin{table}[H]",
            "\\centering",
            "\\begin{tabular}{" + col_spec + "}",
            "\\toprule",
        ]

        # Headers
        latex_lines.append(" & ".join(headers) + " \\\\")
        latex_lines.append("\\midrule")

        # Data rows
        for line in data_lines:
            if "|" in line:
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                latex_lines.append(" & ".join(cells) + " \\\\")

        latex_lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])

        return latex_lines

    def _convert_code_blocks(self, content: str) -> str:
        """Convert code blocks to LaTeX listings."""
        # Fenced code blocks
        pattern = r"```(\w*)\n(.*?)\n```"

        def replace_code_block(match):
            lang = match.group(1) or "text"
            code = match.group(2)

            return f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}"

        content = re.sub(pattern, replace_code_block, content, flags=re.DOTALL)

        # Inline code
        content = re.sub(r"`([^`]+)`", r"\\texttt{\1}", content)

        return content

    def generate_paper(self, include_sections: List[str] = None):
        """Generate the complete LaTeX paper."""

        # Default sections to include
        if include_sections is None:
            include_sections = [
                "policy/federal/irs/eitc.md",
                "policy/federal/irs/ctc.md",
                "policy/federal/hhs/medicaid.md",
                "policy/federal/hhs/chip.md",
                "policy/federal/hhs/tanf.md",
                "policy/federal/ssa/ssi.md",
                "policy/federal/usda/snap.md",
                "policy/federal/usda/wic.md",
                "policy/federal/usda/school-meals.md",
                "policy/federal/hud/housing-assistance.md",
                "policy/federal/ed/pell-grant.md",
                "policy/federal/fcc/lifeline.md",
                "policy/federal/fcc/acp.md",
            ]

        # Start document
        latex_content = [self.preamble]

        # Add each section
        for section_path in include_sections:
            full_path = self.docs_dir / section_path
            if full_path.exists():
                with open(full_path, "r") as f:
                    content = f.read()

                # Convert to LaTeX
                latex_section = self.markdown_to_latex(content)
                latex_content.append(latex_section)
                latex_content.append("\n\\clearpage\n")

        # Add conclusions
        latex_content.append(self._generate_conclusions())

        # Add bibliography
        latex_content.append(self._generate_bibliography())

        # Close document
        latex_content.append("\n\\end{document}")

        # Write output
        output_file = self.output_dir / "policyengine_us_policy_rules.tex"
        with open(output_file, "w") as f:
            f.write("\n".join(latex_content))

        # Generate BibTeX file
        self._generate_bibtex()

        print(f"Generated LaTeX file: {output_file}")

        # Compile to PDF if pdflatex is available
        self._compile_pdf(output_file)

    def _generate_conclusions(self) -> str:
        """Generate conclusions section."""
        return r"""
\section{Conclusions}

This paper has documented the key policy rules and parameters encoded in PolicyEngine US. 
The database provides several contributions to the policy analysis community:

\begin{enumerate}
\item \textbf{Comprehensive Coverage}: We model all major federal tax and benefit programs, 
along with state-specific implementations, capturing the full complexity of the U.S. social 
safety net.

\item \textbf{Legislative Grounding}: Every parameter is traced to primary sources including 
the U.S. Code, Code of Federal Regulations, IRS publications, and state statutes.

\item \textbf{Temporal Consistency}: The database includes historical values from 2017 forward 
and projects parameters under current law, enabling both retrospective and prospective analysis.

\item \textbf{Open Source}: All code and parameters are publicly available, promoting 
transparency and reproducibility in policy research.

\item \textbf{Machine Readable}: The structured format enables automated analysis, integration 
with other systems, and rapid prototyping of policy reforms.
\end{enumerate}

Future work will expand coverage to additional programs, improve modeling of administrative 
rules and take-up rates, and enhance the representation of program interactions. We welcome 
contributions from the research and policy communities to improve and extend this resource.
"""

    def _generate_bibliography(self) -> str:
        """Generate bibliography section."""
        return r"""
\bibliographystyle{apalike}
\bibliography{policyengine}

\section{Data Availability}

All code, parameters, and documentation are available at:
\begin{itemize}
\item GitHub Repository: \url{https://github.com/PolicyEngine/policyengine-us}
\item Documentation: \url{https://policyengine.github.io/policyengine-us}
\item Interactive Interface: \url{https://policyengine.org/us}
\end{itemize}
"""

    def _generate_bibtex(self):
        """Generate BibTeX file with references."""
        bibtex_content = r"""@techreport{crs2024eitc,
  title = {The Earned Income Tax Credit (EITC): How It Works and Who Receives It},
  author = {{Congressional Research Service}},
  year = {2024},
  number = {R43805},
  url = {https://crsreports.congress.gov/product/pdf/R/R43805}
}

@techreport{irs2024pub596,
  title = {Publication 596: Earned Income Credit},
  author = {{Internal Revenue Service}},
  year = {2024},
  institution = {Department of the Treasury},
  url = {https://www.irs.gov/pub/irs-pdf/p596.pdf}
}

@book{tpc2024briefing,
  title = {Briefing Book: Key Elements of the U.S. Tax System},
  author = {{Tax Policy Center}},
  year = {2024},
  publisher = {Urban Institute and Brookings Institution},
  url = {https://www.taxpolicycenter.org/briefing-book}
}

@misc{usda2024snap,
  title = {Supplemental Nutrition Assistance Program (SNAP) Policy Database},
  author = {{U.S. Department of Agriculture}},
  year = {2024},
  howpublished = {Economic Research Service},
  url = {https://www.ers.usda.gov/data-products/snap-policy-data-sets/}
}

@techreport{gao2023federal,
  title = {Federal Low-Income Programs: Eligibility and Benefits Differ for Selected Programs},
  author = {{U.S. Government Accountability Office}},
  year = {2023},
  number = {GAO-23-104577},
  url = {https://www.gao.gov/products/gao-23-104577}
}

@article{hoynes2016eitc,
  title = {The Earned Income Tax Credit},
  author = {Hoynes, Hilary and Rothstein, Jesse},
  year = {2016},
  journal = {Tax Policy and the Economy},
  volume = {30},
  number = {1},
  pages = {103--153}
}

@article{maag2020ctc,
  title = {Reforming the Child Tax Credit: How Different Proposals Change Who Benefits},
  author = {Maag, Elaine and Airi, Nikhita},
  year = {2020},
  journal = {Tax Policy Center Research Report}
}

@techreport{cbpp2024snap,
  title = {A Quick Guide to SNAP Eligibility and Benefits},
  author = {{Center on Budget and Policy Priorities}},
  year = {2024},
  url = {https://www.cbpp.org/research/food-assistance/a-quick-guide-to-snap-eligibility-and-benefits}
}

@article{bitler2003wic,
  title = {What Mean Impacts Miss: Distributional Effects of Welfare Reform Experiments},
  author = {Bitler, Marianne P. and Gelbach, Jonah B. and Hoynes, Hilary W.},
  year = {2003},
  journal = {American Economic Review},
  volume = {96},
  number = {4},
  pages = {988--1012}
}

@article{jacob2012housing,
  title = {The Effects of Housing Assistance on Labor Supply: Evidence from a Voucher Lottery},
  author = {Jacob, Brian A. and Ludwig, Jens},
  year = {2012},
  journal = {American Economic Review},
  volume = {102},
  number = {1},
  pages = {272--304}
}

@book{moffitt2003means,
  title = {Means-Tested Transfer Programs in the United States},
  editor = {Moffitt, Robert},
  year = {2003},
  publisher = {University of Chicago Press}
}

@article{dahl2012impact,
  title = {The Impact of Family Income on Child Achievement: Evidence from the Earned Income Tax Credit},
  author = {Dahl, Gordon B. and Lochner, Lance},
  year = {2012},
  journal = {American Economic Review},
  volume = {102},
  number = {5},
  pages = {1927--1956}
}
"""

        bibtex_file = self.output_dir / "policyengine.bib"
        with open(bibtex_file, "w") as f:
            f.write(bibtex_content)

        print(f"Generated BibTeX file: {bibtex_file}")

    def _compile_pdf(self, tex_file: Path):
        """Compile LaTeX to PDF if pdflatex is available."""
        try:
            # Check if pdflatex is available
            subprocess.run(
                ["pdflatex", "--version"], capture_output=True, check=True
            )

            # Compile twice for references
            print("Compiling LaTeX to PDF...")
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                    cwd=tex_file.parent,
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    print(f"LaTeX compilation warning: {result.stdout}")

            pdf_file = tex_file.with_suffix(".pdf")
            if pdf_file.exists():
                print(f"Generated PDF: {pdf_file}")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "pdflatex not found. Install a LaTeX distribution to compile PDF."
            )


def main():
    """Generate LaTeX paper from documentation."""
    repo_root = Path(__file__).parent.parent.parent
    docs_dir = repo_root / "docs"
    output_dir = repo_root / "docs" / "_build" / "latex"

    generator = LaTeXGenerator(docs_dir, output_dir)
    generator.generate_paper()


if __name__ == "__main__":
    main()
