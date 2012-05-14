\ProvidesClass{synhak}
\LoadClass[11pt,letterpaper,oneside]{article}

\newif\iflogo

\logotrue

\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{forloop}
\usepackage[cm]{fullpage}
\usepackage{setspace}
\usepackage{fancyhdr}
\pagestyle{fancy}

\DeclareOption{nologo}
    {\logofalse}
\DeclareOption{logo}
    {\logotrue}
\ProcessOptions

\input {\jobname.version.latex}

\makeatletter
\def \maketitle {%
  \begin{center}
  \iflogo
    \includegraphics[width=8cm]{images/logo}\\[1cm]
    \rule{\linewidth}{0.5mm}
  \fi

  \textsc{\Large \@title}\\[1cm]
  \end{center}
}
\makeatother

\makeatletter
\def \versioninfo {%
  \GITAbrHash, \GITAuthorDate, \GITAuthorName
}
\makeatother

\makeatletter
\fancyfoot[C]{\versioninfo}
\makeatother
