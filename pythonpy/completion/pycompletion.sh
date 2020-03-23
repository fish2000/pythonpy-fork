_py()
{
    COMPREPLY=($(pycompleter "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

_py2()
{
    COMPREPLY=($(pycompleter2 "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

_py2.6()
{
    COMPREPLY=($(pycompleter2.6 "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

_py2.7()
{
    COMPREPLY=($(pycompleter2.7 "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

_py3()
{
    COMPREPLY=($(pycompleter3 "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

_py3.3()
{
    COMPREPLY=($(pycompleter3.3 "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}
_py3.4()
{
    COMPREPLY=($(pycompleter3.4 "${COMP_WORDS[@]}" 2>/dev/null | sed 's/.*1034h//'))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}


complete -F _py -o nospace py
complete -F _py2 -o nospace py2
complete -F _py2.6 -o nospace py2.6
complete -F _py2.7 -o nospace py2.7
complete -F _py3 -o nospace py3
complete -F _py3.3 -o nospace py3.3
complete -F _py3.4 -o nospace py3.4
