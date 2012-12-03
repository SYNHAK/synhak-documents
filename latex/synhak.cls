\ProvidesClass{synhak}
\LoadClass[11pt,letterpaper,oneside]{article}

\newif\iflogo
\newif\ifcompact
\newif\ifgit
\newif\ifletterhead

\gittrue
\logotrue
\compactfalse
\letterheadfalse

\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{forloop}
\usepackage[cm]{fullpage}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage[pdftex]{hyperref}
\usepackage{wasysym}
\usepackage{pbox}
\usepackage{fancybox}
\usepackage{wrapfig}
\pagestyle{fancy}

\DeclareOption{nologo}
    {\logofalse}
\DeclareOption{logo}
    {\logotrue}
\DeclareOption{compact}
    {\compacttrue}
\DeclareOption{full}
    {\compactfalse}
\DeclareOption{git}
    {\gittrue}
\DeclareOption{nogit}
    {\gitfalse}
\DeclareOption{letterhead}
    {\letterheadtrue}
\DeclareOption{noletterhead}
    {\letterheadfalse}
\ProcessOptions

\input {\jobname.version.latex}

\renewcommand{\headrulewidth}{0pt}
\def \maketitle {%
\ifcompact
  \begin{tabularx}{\textwidth}{ X X X }
    \iflogo \includegraphics[width=3cm]{images/logo} \fi & \pbox{5cm}{\@title} \ifgit & \versioninfo \fi \\
  \end{tabularx}
\else
  \begin{center}
  \iflogo
    \includegraphics[width=8cm]{images/logo}\\[1cm]
    The Akron Hackerspace \\
    \ifletterhead
      \textsc{\small 21 W. North St., Akron, OH 44304 | http://synhak.org }\\[1cm]
    \fi
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
\newcommand{\StampBox}[1]{
  \begin{wrapfigure}{r}{5cm}
    \vspace{-20pt}
    \framebox[4.5cm]{\raisebox{0pt}[2cm]\\{\small #1}}
    \vspace{-20pt}
  \end{wrapfigure}
}
\makeatother

\ifcompact
\else
\makeatletter
\ifgit \fancyfoot[C]{\versioninfo} \fi
\makeatother
\fi
