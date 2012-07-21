\ProvidesClass{synhak}
\LoadClass[11pt,letterpaper,oneside]{article}

\newif\iflogo
\newif\ifcompact

\logotrue
\compactfalse

\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{forloop}
\usepackage[cm]{fullpage}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage[pdftex]{hyperref}
\usepackage{wasysym}
\pagestyle{fancy}

\DeclareOption{nologo}
    {\logofalse}
\DeclareOption{logo}
    {\logotrue}
\DeclareOption{compact}
    {\compacttrue}
\DeclareOption{full}
    {\compactfalse}
\ProcessOptions

\input {\jobname.version.latex}

\renewcommand{\headrulewidth}{0pt}
\def \maketitle {%
\ifcompact
  \begin{tabularx}{\textwidth}{ X X X }
    \iflogo \includegraphics[width=3cm]{images/logo} \fi & \@title & \versioninfo \\
  \end{tabularx}
\else
  \begin{center}
  \iflogo
    \includegraphics[width=8cm]{images/logo}\\[1cm]
    \rule{\linewidth}{0.5mm}
  \fi

  \textsc{\Large \@title}\\[1cm]
  \end{center}
\fi
}
\makeatother

\makeatletter
\def \versioninfo {%
  \GITAbrHash, \GITAuthorDate, \GITAuthorName
}
\makeatother

\ifcompact
\else
\makeatletter
\fancyfoot[C]{\versioninfo}
\makeatother
\fi
