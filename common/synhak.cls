\ProvidesClass{synhak}

\newif\iflandscape
\newif\iflogo
\newif\ifcompact
\newif\ifgit
\newif\ifletterhead
\newif\ifgitauthor

\gitauthortrue
\gittrue
\logotrue
\compactfalse
\letterheadfalse
\landscapefalse

\DeclareOption{landscape}
    {\landscapetrue}
\DeclareOption{portrait}
    {\landscapefalse}
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
\DeclareOption{gitauthor}
    {\gitauthortrue}
\DeclareOption{nogitauthor}
    {\gitauthorfalse}
\DeclareOption{letterhead}
    {\letterheadtrue}
\DeclareOption{noletterhead}
    {\letterheadfalse}
\DeclareOption{nosign}
    {\signfalse}
\DeclareOption{sign}
    {\signtrue}
\ProcessOptions

\iflandscape
    \LoadClass[landscape,11pt,letterpaper,oneside]{article}
\else
    \LoadClass[11pt,letterpaper,oneside]{article}
\fi

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
\usepackage{lmodern}
\pagestyle{fancy}

\input {\jobname.version.latex}

\renewcommand{\headrulewidth}{0pt}
\def \maketitle {%
\ifcompact
  \begin{tabularx}{\textwidth}{ X X X }
    \iflogo \includegraphics[width=3cm]{../impress/logo/logo} \fi & \pbox{5cm}{\@title} \ifgit & \versioninfo \fi \\
  \end{tabularx}
\else
  \begin{center}
  \iflogo
    \includegraphics[width=8cm]{../impress/logo/logo}\\[1cm]
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
\def \massive {%
\fontsize{5cm}{1em}
\selectfont
}

\def \enormous {%
\fontsize{3cm}{1em}
\selectfont
}

\makeatother

\makeatletter
\def \versioninfo {%
\ifgitauthor
  \GITAbrHash, \GITAuthorDate, \GITAuthorName
\else
  \GITAbrHash, \GITAuthorDate
\fi
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
