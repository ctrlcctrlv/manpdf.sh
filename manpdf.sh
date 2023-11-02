#!/bin/bash
# manpdf.sh — Instead of displaying man pages in a terminal, pipe them to this script to convert them to PDF and open them in Okular.

RWLT_PY="$(dirname "${BASH_SOURCE[0]}")/rwlt.py"
RWLT_PY="$(readlink -f "$RWLT_PY")"
>&2 echo "RWLT_PY=$RWLT_PY"

manpdf_check_deps() {
    declare -l -A DEPS
    DEPS=()
    for dep in pandoc pdflatex okular python; do
        DEPS[$dep]="`command -v $dep`"
    done

    let i=0
    for dep in "${!DEPS[@]}"; do
        i=$((i+1))
        if [ "${DEPS[$dep]}" == "" ]; then
            echo "Missing dependency: $dep"
            return $i
        fi
    done
}

manpdf() {
    pushd /tmp
    T=`mktemp`
    (man -Thtml $1 | pandoc -f html -t latex  --standalone -o "$T".tex) && {
        {
            python "$RWLT_PY" "$T".tex "$T".temp.tex longtable && \
                mv "$T".temp.tex "$T".tex
        } || {
            >&2 echo "rwlt.py failed"
            true
        }
        CMD='pdflatex -interaction=nonstopmode -shell-escape "$T.tex"'
        eval $CMD
        eval $CMD
        [ -f "$T.pdf" ] && okular "$T.pdf" || man "$1"
        popd
    }
    {
        local time_left=10
        local prompt='Delete $T.tex $T.pdf? [y/N] $time_left…'
        while [ $time_left -gt 0 -a -z "$REPLY" ]; do
            sleep 1
            time_left=$((time_left-1))
            >&2 echo -ne "\r$(eval echo $prompt)"
        done &
        COUNTDOWN_PID=$!
        read -r -t 10 -n 1 -p "$(eval echo $prompt)" REPLY
        [[ $REPLY =~ ^[Yy]$ ]] && rm -v -f "$T.tex" "$T.pdf"
        kill $COUNTDOWN_PID
        >&2 echo
    }
}

manpdf_check_deps || exit $?
manpdf "$@"
