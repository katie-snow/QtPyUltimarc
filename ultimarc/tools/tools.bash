#
# bash completion for ultimarc tools
# See: https://debian-administration.org/article/317/An_introduction_to_bash_completion_part_2
#
# Usage: run `. ultimarc/tools/tools.bash` or add to bash profile.
#
_python()
{
    local cur prev tools stdopts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"


    # These are the specific tools we support
    tools="--help list usb-button"
    # These are the standard options all tools support.
    stdopts="--help --debug --log-file --bus --address"

    #
    #  Complete the arguments to some of the basic commands.
    #  For additional complex option branching examples, see:
    #   https://raw.githubusercontent.com/all-of-us/raw-data-repository/devel/rdr_service/tools/tool_libs/tools.bash
    #
    case "${prev}" in
        python)
           COMPREPLY=( $(compgen -W "-m" -- ${cur}) )
           return 0
           ;;
        -m)
           COMPREPLY=( $(compgen -W "tools" -- ${cur}) )
           return 0
           ;;
        tools)
            COMPREPLY=( $(compgen -W "${tools}" -- ${cur}) )
            return 0
            ;;
        list)
            # These are options specific to this tool.
            local toolopts="--descriptors"
            COMPREPLY=( $(compgen -W "${stdopts} ${toolopts}" -- ${cur}) )
            return 0
            ;;
        usb-button)
            # These are options specific to this tool.
            local toolopts="--set-color --get-color --load-config --export-config"
            COMPREPLY=( $(compgen -W "${stdopts} ${toolopts}" -- ${cur}) )
            return 0
            ;;
        *)
        ;;
    esac

   COMPREPLY=($(compgen -W "${tools}" -- ${cur}))
   return 0
}
complete -F _python python
complete -F _python rtool

