

# disable recursive dependency resolution when building shelduck itself
# shelduck import string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import require.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./event/fire.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import notrace.sh


bobshell_die() {
  # https://github.com/biox/pa/blob/main/pa
  printf '%s: %s.\n' "$(basename "$0")" "${*:-error}" >&2
  exit 1
}


# use isset OPTVARNAME
bobshell_isset() {
	eval "test \"\${$1+defined}\" = defined"
}

#  
bobshell_isset_1() {
	eval "test \"\${1+defined}\" = defined"
}

bobshell_isset_2() {
	eval "test \"\${2+defined}\" = defined"
}

bobshell_isset_3() {
	eval "test \"\${3+defined}\" = defined"
}

bobshell_command_available() {
	command -v "$1" > /dev/null
}

# fun: bobshell_putvar VARNAME NEWVARVALUE
# txt: установка значения переменной по динамическому имени
# DEPRECATED: use bobshell_ar_set
bobshell_putvar() {
  eval "$1=\"\$2\""
}



# fun bobshell_getvar VARNAME [DEFAULTVALUE]
# use: echo "$(getvar MSG)"
# txt: считывание значения переменной по динамическому имени
# DEPRECATED: use bobshell_var_get
bobshell_getvar() {
	if bobshell_isset "$1"; then
  		eval "printf %s \"\$$1\""
	elif bobshell_isset_2 "$@"; then
		printf %s "$2"
	else
		bobshell_errcho "bobshell_getvar: $1: parameter not set"
		return 1
	fi
}


bobshell_require_not_empty() {
	if [ -z "${1:-}" ]; then
		shift
		bobshell_die "$@"
	fi
}

bobshell_require_empty() {
	if [ -z "${1:-}" ]; then
		shift
		bobshell_die "$@"
	fi
}


bobshell_is_bash() {
	test -n "${BASH_VERSION:-}"
}

bobshell_is_zsh() {
	test -n "${ZSH_VERSION:-}"
}

bobshell_is_ksh() {
	test -n "${KSH_VERSION:-}"
}

bobshell_list_functions() {
	if bobshell_is_bash; then
		compgen -A function
	elif [ -n "${0:-}" ] && [ -f "${0}" ]; then
		sed --regexp-extended 's/^( *function)? *([A-Za-z0_9_]+) *\( *\) *\{ *$/\2/g' "$0"
	fi
}

bobshell_log() {
	bobshell_log_message="$*"
	printf '%s: %s\n' "$0" "$bobshell_log_message" >&2
	unset bobshell_log_message
}

bobshell_rename_var() {
	if [ "$1" = "$2" ]; then
		return
	fi
	eval "$2=\$$1"
	unset "$1"
}

bobshell_vars() {
	bobshell_vars_list=$(set | sed -n 's/^\([A-Za-z_][A-Za-z_0-9]*\)=.*$/\1/pg' | sort -u)
	for bobshell_vars_item in $bobshell_vars_list; do
		if bobshell_isset "$bobshell_vars_item"; then
			printf '%s ' "$bobshell_vars_item"
		fi
	done
	unset bobshell_vars_list
}

# bobshell_not_empty "$@"
bobshell_not_empty() {
	test set = "${1+set}" 
}

#bobshell_map

# fun: bobshell_foreach ITEM... -- COMMAND [ARG...]
# bobshell_foreach() {
# 	bobshell_foreach_items=
# 	bobshell_foreach_command=
# 	while bobshell_not_empty "$@"; do
# 		if [ '--' = "$1" ]; then
# 			shift
# 			set -- "$@"
# 			break
# 		fi
# 		bobshell_foreach_item=$(bobshell_quote "$1")
# 		bobshell_foreach_items="$bobshell_foreach_items $1"
# 		shift
# 	done

# 	bobshell_require_not_empty "$bobshell_foreach_command" "bobshell_foreach: command not set"

# 	for bobshell_foreach_item in $bobshell_foreach_items; do
# 		"$@" "$bobshell_foreach_item"
# 	done
# 	unset bobshell_foreach_item

# 	unset bobshell_foreach_items bobshell_foreach_command
# }

bobshell_error() {
	bobshell_errcho "$@"
	return 1
}

bobshell_errcho() {
	printf '%s\n' "$*" >&2
}

bobshell_printf_stderr() {
	printf '%s\n' "$*" >&2
}

bobshell_subshell() {
	( "$@" )
}

bobshell_last_arg() {
	bobshell_require_isset_1 'bobshell_last_arg: at least one positional argument expected'
	while bobshell_isset_2 "$@"; do
		shift
	done
	printf %s "$1"
}

trap '{ set +x; } 2> /dev/null; bobshell_exit_trap' EXIT
bobshell_exit_trap() {
	_bobshell_exit_trap__code=$?
	if [ true = "${BOBSHELL_EXIT_TRAP_TRACE:-false}" ]; then
		set -x
	fi

	# shellcheck disable=SC2181
	if [ 0 -eq "$_bobshell_exit_trap__code" ]; then
		bobshell_event_fire bobshell_success_exit_event
	else
		bobshell_event_fire bobshell_error_exit_event
	fi
	bobshell_event_fire bobshell_exit_event
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import util.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import resource/copy.sh


# env: BOBSHELL_INSTALL_NAME
bobshell_install_init() {
	# https://www.gnu.org/prep/standards/html_node/Directory-Variables.html#Directory-Variables
	
	if [ -z "$BOBSHELL_INSTALL_NAME" ] && [ -n "$BOBSHELL_APP_NAME" ]; then
		BOBSHELL_INSTALL_NAME="$BOBSHELL_APP_NAME"
	fi

	: "${BOBSHELL_INSTALL_DESTDIR:=}"
	: "${BOBSHELL_INSTALL_ROOT:=}"
	if [ -n "${BOBSHELL_INSTALL_ROOT:-}" ]; then
		BOBSHELL_INSTALL_ROOT=$(realpath "$BOBSHELL_INSTALL_ROOT")
	fi

	# https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.html
	: "${BOBSHELL_INSTALL_SYSTEM_BINDIR=${BOBSHELL_INSTALL_BINDIR-$BOBSHELL_INSTALL_ROOT/opt/bin}}"
	: "${BOBSHELL_INSTALL_SYSTEM_CONFDIR=${BOBSHELL_INSTALL_CONFDIR-$BOBSHELL_INSTALL_ROOT/etc/opt}}"
	: "${BOBSHELL_INSTALL_SYSTEM_DATADIR=${BOBSHELL_INSTALL_DATADIR-$BOBSHELL_INSTALL_ROOT/opt}}"
	: "${BOBSHELL_INSTALL_SYSTEM_LOCALSTATEDIR=${BOBSHELL_INSTALL_LOCALSTATEDIR-$BOBSHELL_INSTALL_ROOT/var/opt}}"
	: "${BOBSHELL_INSTALL_SYSTEM_CACHEDIR=${BOBSHELL_INSTALL_CACHEDIR-$BOBSHELL_INSTALL_ROOT/var/cache/opt}}"
	: "${BOBSHELL_INSTALL_SYSTEM_SYSTEMDDIR=${BOBSHELL_INSTALL_SYSTEMDDIR-$BOBSHELL_INSTALL_ROOT/etc/systemd/system}}"
	: "${BOBSHELL_INSTALL_SYSTEM_PROFILE=${BOBSHELL_INSTALL_PROFILE-$BOBSHELL_INSTALL_ROOT/etc/profile}}"

	# https://wiki.archlinux.org/title/XDG_Base_Directory
	: "${BOBSHELL_INSTALL_USER_BINDIR=${BOBSHELL_INSTALL_BINDIR-$BOBSHELL_INSTALL_ROOT$HOME/.local/bin}}"
	: "${BOBSHELL_INSTALL_USER_CONFDIR=${BOBSHELL_INSTALL_CONFDIR-$BOBSHELL_INSTALL_ROOT$HOME/.config}}"
	: "${BOBSHELL_INSTALL_USER_DATADIR=${BOBSHELL_INSTALL_DATADIR-$BOBSHELL_INSTALL_ROOT$HOME/.local/share}}"
	: "${BOBSHELL_INSTALL_USER_LOCALSTATEDIR=${BOBSHELL_INSTALL_LOCALSTATEDIR-$BOBSHELL_INSTALL_ROOT$HOME/.local/state}}"
	: "${BOBSHELL_INSTALL_USER_CACHEDIR=${BOBSHELL_INSTALL_CACHEDIR-$BOBSHELL_INSTALL_ROOT$HOME/.cache}}"
	: "${BOBSHELL_INSTALL_USER_SYSTEMDDIR=${BOBSHELL_INSTALL_SYSTEMDDIR-$BOBSHELL_INSTALL_ROOT$HOME/.config/systemd/user}}"
	: "${BOBSHELL_INSTALL_USER_PROFILE=${BOBSHELL_INSTALL_PROFILE-$BOBSHELL_INSTALL_ROOT$HOME/.profile}}"

	if [ -z "${BOBSHELL_INSTALL_ROLE:-}" ]; then
		if bobshell_is_root; then
			BOBSHELL_INSTALL_ROLE=SYSTEM
		else
			BOBSHELL_INSTALL_ROLE=USER
		fi
	fi


	if [ SYSTEM = "$BOBSHELL_INSTALL_ROLE" ]; then
		BOBSHELL_INSTALL_BINDIR="$BOBSHELL_INSTALL_SYSTEM_BINDIR"
		BOBSHELL_INSTALL_CONFDIR="$BOBSHELL_INSTALL_SYSTEM_CONFDIR"
		BOBSHELL_INSTALL_DATADIR="$BOBSHELL_INSTALL_SYSTEM_DATADIR"
		BOBSHELL_INSTALL_LOCALSTATEDIR="$BOBSHELL_INSTALL_SYSTEM_LOCALSTATEDIR"
		BOBSHELL_INSTALL_CACHEDIR="$BOBSHELL_INSTALL_SYSTEM_CACHEDIR"
		BOBSHELL_INSTALL_SYSTEMDDIR="$BOBSHELL_INSTALL_SYSTEM_SYSTEMDDIR"
		BOBSHELL_INSTALL_PROFILE="$BOBSHELL_INSTALL_SYSTEM_PROFILE"
	else
		BOBSHELL_INSTALL_BINDIR="$BOBSHELL_INSTALL_USER_BINDIR"
		BOBSHELL_INSTALL_CONFDIR="$BOBSHELL_INSTALL_USER_CONFDIR"
		BOBSHELL_INSTALL_DATADIR="$BOBSHELL_INSTALL_USER_DATADIR"
		BOBSHELL_INSTALL_LOCALSTATEDIR="$BOBSHELL_INSTALL_USER_LOCALSTATEDIR"
		BOBSHELL_INSTALL_CACHEDIR="$BOBSHELL_INSTALL_USER_CACHEDIR"
		BOBSHELL_INSTALL_SYSTEMDDIR="$BOBSHELL_INSTALL_USER_SYSTEMDDIR"
		BOBSHELL_INSTALL_PROFILE="$BOBSHELL_INSTALL_USER_PROFILE"
	fi

		
	: "${BOBSHELL_INSTALL_SYSTEMCTL:=systemctl}"
}






# fun: bobshell_install_service SRCLOCATOR DESTNAME
# use: bobshell_install_service file:target/myservice myservice.service
bobshell_install_service() {
	bobshell_install_service_dir="$BOBSHELL_INSTALL_DESTDIR$BOBSHELL_INSTALL_SYSTEMDDIR"
	mkdir -p "$bobshell_install_service_dir"
	bobshell_resource_copy "$1" "file:$bobshell_install_service_dir/$2"

	
	if [ 0 = "$(id -u)" ]; then
		bobshell_install_service_arg=
	else
		bobshell_install_service_arg='--user'
	fi
	$BOBSHELL_INSTALL_SYSTEMCTL $bobshell_install_service_arg daemon-reload
	$BOBSHELL_INSTALL_SYSTEMCTL $bobshell_install_service_arg enable "$2"
}








# fun: bobshell_install_put SRC DIR DESTNAME MODE
bobshell_install_put() {
	mkdir -p "$BOBSHELL_INSTALL_DESTDIR$2"
	bobshell_resource_copy "$1" "file:$BOBSHELL_INSTALL_DESTDIR$2/$3"
	chmod "$4" "$BOBSHELL_INSTALL_DESTDIR$2/$3"
}

# fun: bobshell_install_binary SRC DESTNAME
# use: bobshell_install_binary target/exesrc.sh mysuperprog
bobshell_install_put_executable() {
	bobshell_install_put "$1" "$BOBSHELL_INSTALL_BINDIR" "$2" u=rwx,go=rx
}

bobshell_install_put_config() {
	bobshell_install_put "$1" "$BOBSHELL_INSTALL_CONFDIR/$BOBSHELL_INSTALL_NAME" "$2" u=rw,go=r
}

bobshell_install_put_data() {
	bobshell_install_put "$1" "$BOBSHELL_INSTALL_DATADIR/$BOBSHELL_INSTALL_NAME" "$2" u=rw,go=r
}

bobshell_install_put_localstate() {
	bobshell_install_put "$1" "$BOBSHELL_INSTALL_LOCALSTATEDIR/$BOBSHELL_INSTALL_NAME" "$2" u=rw,go=r
}

bobshell_install_put_cache() {
	bobshell_install_put "$1" "$BOBSHELL_INSTALL_CACHEDIR/$BOBSHELL_INSTALL_NAME" "$2" u=rw,go=r
}









# fun: bobshell_install_find SYSTEMCANDIDATE USERCANDIDATE
bobshell_install_find() {
	if bobshell_is_not_root && [ -f "$BOBSHELL_INSTALL_DESTDIR$2" ]; then
		printf %s "$2"
		return
	fi

	if [ -f "$BOBSHELL_INSTALL_DESTDIR$1" ]; then
		printf %s "$1"
		return
	fi

	return 1
}

bobshell_install_find_executable() {
	bobshell_install_find "$BOBSHELL_INSTALL_SYSTEM_BINDIR/$1" "$BOBSHELL_INSTALL_USER_BINDIR/$1"
}

bobshell_install_find_config() {
	bobshell_install_find "$BOBSHELL_INSTALL_SYSTEM_CONFDIR/$BOBSHELL_INSTALL_NAME/$1" "$BOBSHELL_INSTALL_USER_CONFDIR/$BOBSHELL_INSTALL_NAME/$1"
}

bobshell_install_find_data() {
	bobshell_install_find "$BOBSHELL_INSTALL_SYSTEM_DATADIR/$BOBSHELL_INSTALL_NAME/$1" "$BOBSHELL_INSTALL_USER_DATADIR/$BOBSHELL_INSTALL_NAME/$1"
}

bobshell_install_find_localstate() {
	bobshell_install_find "$BOBSHELL_INSTALL_SYSTEM_LOCALSTATEDIR/$BOBSHELL_INSTALL_NAME/$1" "$BOBSHELL_INSTALL_USER_LOCALSTATEDIR/$BOBSHELL_INSTALL_NAME/$1"
}

bobshell_install_find_cache() {
	bobshell_install_find "$BOBSHELL_INSTALL_SYSTEM_CACHEDIR/$BOBSHELL_INSTALL_NAME/$1" "$BOBSHELL_INSTALL_USER_CACHEDIR/$BOBSHELL_INSTALL_NAME/$1"
}

















# fun: bobshell_install_get FUN NAME DEST
bobshell_install_get() {
	bobshell_install_get_dest="$3"
	set -- "$1" "$2"
	if bobshell_install_get_found=$("$@"); then
		bobshell_resource_copy "file:$bobshell_install_get_found" "$bobshell_install_get_dest"
		return
	else
		return 1
	fi
}

# fun: bobshell_install_get_executable NAME DEST
bobshell_install_get_executable() {
	bobshell_install_get bobshell_install_find_executable "$1" "$2"
}

# fun: bobshell_install_get_config NAME DEST
bobshell_install_get_config() {
	bobshell_install_get bobshell_install_find_config "$1" "$2"
}

bobshell_install_get_data() {
	bobshell_install_get bobshell_install_find_data "$1" "$2"
}

bobshell_install_get_localstate() {
	bobshell_install_get bobshell_install_find_localstate "$1" "$2"
}

bobshell_install_get_cache() {
	bobshell_install_get bobshell_install_find_cache "$1" "$2"
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh

# fun: bobshell_is_file LOCATOR [FILEPATHVAR]
bobshell_locator_is_file() {
	if bobshell_starts_with "$1" /; then
		if [ -n "${2:-}" ]; then
			bobshell_putvar "$2" "$1"
		fi
	elif bobshell_remove_prefix "$1" file:// "${2:-}"; then
		true
	else
		bobshell_remove_prefix "$1" file: "${2:-}";
	fi
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh

bobshell_locator_is_remote() {
	bobshell_remove_prefix "$1" http:// "${2:-}" \
	  || bobshell_remove_prefix "$1" https:// "${2:-}" \
	  || bobshell_remove_prefix "$1" ftp:// "${2:-}"\
	  || bobshell_remove_prefix "$1" ftps:// "${2:-}"
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh

bobshell_locator_is_stdin() {
	#set -- bobshell_remove_prefix "$1" stdin:
	bobshell_remove_prefix "$1" stdin: "${2:-}"
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh

bobshell_locator_is_stdout() {
	bobshell_remove_prefix "$1" stdout: "${2:-}"
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../resource/copy.sh


bobshell_locator_parse() {
	if bobshell_starts_with "$1" /; then
		bobshell_locator_parse_type='file'
		bobshell_locator_parse_ref="$1"
	elif ! bobshell_split_first "$1" : bobshell_locator_parse_type bobshell_locator_parse_ref; then
		return 1
	fi

	case "$bobshell_locator_parse_type" in
		(val | var | eval | stdin | stdout | url)
			true
			;;
		(file)
			if bobshell_remove_prefix "$bobshell_locator_parse_ref" /// bobshell_locator_parse_ref; then
				bobshell_locator_parse_ref="/$bobshell_locator_parse_ref"
			elif bobshell_remove_prefix "$bobshell_locator_parse_ref" // bobshell_locator_parse_ref; then
				true
			elif bobshell_remove_prefix "$bobshell_locator_parse_ref" / bobshell_locator_parse_ref; then
				bobshell_locator_parse_ref="/$bobshell_locator_parse_ref"
			else
				true
			fi
			;;
		(http | https | ftp | ftps) 
			bobshell_locator_parse_type=url
			bobshell_locator_parse_ref="$1"
			;;
		(*)
			return 1
	esac
	
	if [ -n "${2:-}" ]; then
		bobshell_resource_copy_val_to_var "$bobshell_locator_parse_type" "$2"
	fi
	if [ -n "${3:-}" ]; then
		bobshell_resource_copy_val_to_var "$bobshell_locator_parse_ref" "$3"
	fi
}






# https://stackoverflow.com/a/32158604
# https://howardhinnant.github.io/date_algorithms.html

# disable recursive dependency resolution when building shelduck itself
# shelduck import ../misc/awk.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh

bobshell_file_date_lib='


function civil_to_days(year, month, day) {
	year -= (month <= 2) ? 1 : 0;
	era = int((year >= 0 ? year : year - 399) / 400);
	year_of_era = year - era*400; # [0, 399]
	day_of_year = int((153*(month > 2 ? month-3 : month+9) + 2)/5) + day-1;  # [0, 365]
	day_of_era = year_of_era * 365 + int(year_of_era/4) - int(year_of_era/100) + day_of_year;  # [0, 146096]
	result = 146097*era + day_of_era - 719468
	return result;
}


function offset_to_minutes(offset) {
	offset_minutes=int(offset);
	result = int(offset_minutes/100)*60 + (offset_minutes%100);
	
	return result;
}

function format_date(format, year, month, day, hour, minute, second, nano, offset_minutes) {

	# parse format and output
	format_length = split(format, format_chars, "")
	if(0 == format_length) {
		print("error parsing ls output") > "/dev/stderr"
		exit
	}


	i=1;
	while(i<format_length) {
		current_char=format_chars[i];
		if("%" == current_char) {
			i++;
			if(i>format_length) {
				print("malformed format") > "/dev/stderr"
				exit 1
			}
			current_char=format_chars[i];
			if("%" == current_char) {
				printf("%")
			} else if("s" == current_char) {
				seconds_since_epoch=60*(60*(24*civil_to_days(year, month, day) + hour) + minute - offset_minutes) + second;
				printf("%d", seconds_since_epoch)
			} else if("Y" == current_char) {
				printf("%04d", year)
			} else if("m" == current_char) {
				printf("%02d", month)
			} else if("d" == current_char) {
				printf("%02d", day)
			} else if("H" == current_char) {
				printf("%02d", hour)
			} else if("M" == current_char) {
				printf("%02d", minute)
			} else if("S" == current_char) {
				printf("%02d", seconds)
			} else {
				printf("unsupported format %s", current_char) > "/dev/stderr"
				exit 1
			}
			i++
		} else {
			printf(current_char);
			i++
		}
	}
}

'




# fun: bobshell_file_date FORMAT FILE
# txt: print file modification date
#      if time is earlier then half year ago, there is no time information
#      if time is after half year ago, minute-precision is available
bobshell_file_date_ls() {
	if ! bobshell_isset _bobshell_file_date__offset; then
		_bobshell_file_date__offset="$(date +%z)"
	fi

	_bobshell_file_date_ls=$(LC_ALL=C ls -dl "$2")
	bobshell_awk var:_bobshell_file_date_ls var:_bobshell_file_date_ls__result \
			-v debug=1 \
			-v current_month="$(date +%m)" \
			-v current_year="$(date +%Y)" \
			-v offset="$_bobshell_file_date__offset:" \
			-v format="$1" \
			"$bobshell_file_date_lib"'

{

	# month
	if     ("Jan" == $6) { month= 1; }
	else if("Feb" == $6) { month= 2; }
	else if("Mar" == $6) { month= 3; }
	else if("Apr" == $6) { month= 4; }
	else if("May" == $6) { month= 5; }
	else if("Jun" == $6) { month= 6; }
	else if("Jul" == $6) { month= 7; }
	else if("Aug" == $6) { month= 8; }
	else if("Sep" == $6) { month= 9; }
	else if("Oct" == $6) { month=10; }
	else if("Nov" == $6) { month=11; }
	else if("Dec" == $6) { month=12; }
	else {
		print("error parsing ls output") > "/dev/stderr"
		exit 1
	}

	# day
	day=int($7)

	# year or time
	if ($8 ~ /^[[:digit:]]{4}$/) {
		year = int($8)
		hour = 0
		minute = 0
		offset_minutes = 0
	} else if ($8 ~ /^[[:digit:]]{2}:[[:digit:]]{2}$/) {
		hour = substr($8, 1, 2);
		minute = substr($8, 4, 2);
		
		if(month <= int(current_month)) {
			year = int(current_year)
		} else {
			year = int(current_year) - 1;
		}
		offset_minutes = offset_to_minutes(offset)
	} else {
		printf("error parsing ls output") > "/dev/stderr"
		exit 1
	}

	printf("%s", format_date(format, year, month, day, hour, minute, 0, 0, offset_minutes))

}'
	unset _bobshell_file_date_ls

	bobshell_result_set true "$_bobshell_file_date_ls__result"
	unset _bobshell_file_date_ls__result
}

bobshell_file_date_diff() {
	if ! bobshell_isset _bobshell_file_date__offset; then
		_bobshell_file_date__offset="$(date +%z)"
	fi

	_bobshell_file_date_diff__src=$(printf '%s' 35de218667274492878d89dad9ce0d9cb8a3d80d169e4f36b5ad93e4dfc900123e695dd496ab44359f620d59435a35fa0f5e4af8e22f4a4eb1e3888a6ea41af | LC_ALL=C diff -ua "$2" - | head -1)
	bobshell_awk var:_bobshell_file_date_diff__src var:_bobshell_file_date_diff__result \
			-F '	' \
			-v format="$1" "$bobshell_file_date_lib"'{
	year   = int(substr($2, 1, 4))
	month  = int(substr($2, 6, 2))
	day    = int(substr($2, 9, 2))
	hour   = int(substr($2, 12, 2))
	minute = int(substr($2, 15, 2))
	second = int(substr($2, 18, 2))
	nano   = int(substr($2, 21, 9))
	offset = int(substr($2, 31, 5))

	printf("%s", format_date(format, year, month, day, hour, minute, second, nano, offset_to_minutes(offset)))
}'
	unset _bobshell_file_date_diff__src

	bobshell_result_set true "$_bobshell_file_date_diff__result"
	unset _bobshell_file_date_diff__result
}

bobshell_file_date() {
	_bobshell_file_date_format="%s"
	while bobshell_isset_1 "$@"; do
		case "$1" in
			(-f|--format)
				_bobshell_file_date_format="$2"
				shift 2
				;;
			(-*)
				bobshell_die "bobshell_file_date: unsupported option: $1"
				;; 
			(*) break
		esac
	done

	if ! [ -r "$1" ]; then
		bobshell_result_set false
		return
	fi

	if ! bobshell_command_available diff || [ -d "$1" ]; then
		bobshell_file_date_ls "$_bobshell_file_date_format" "$1"
	else
		bobshell_file_date_diff "$_bobshell_file_date_format" "$1"
	fi
	unset _bobshell_file_date_format
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/parse.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../resource/copy.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../str/quote.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../url.sh



# fun: bobshell_resource_copy SOURCE DESTINATION
bobshell_resource_copy() {
	bobshell_locator_parse "$1" bobshell_resource_copy_source_type      bobshell_resource_copy_source_ref
	bobshell_locator_parse "$2" bobshell_resource_copy_destination_type bobshell_resource_copy_destination_ref


	bobshell_resource_copy_command="bobshell_resource_copy_${bobshell_resource_copy_source_type}_to_${bobshell_resource_copy_destination_type}"
	if ! bobshell_command_available "$bobshell_resource_copy_command"; then
		bobshell_die "bobshell_resource_copy: unsupported copy $bobshell_resource_copy_source_type to $bobshell_resource_copy_destination_type"
	fi

	"$bobshell_resource_copy_command" "$bobshell_resource_copy_source_ref" "$bobshell_resource_copy_destination_ref"
	
	unset bobshell_resource_copy_source_type bobshell_resource_copy_source_ref
	unset bobshell_resource_copy_destination_type bobshell_resource_copy_destination_ref
}


bobshell_resource_copy_to_val()           { bobshell_die 'cannot write to val resource'; }
bobshell_resource_copy_eval()             { bobshell_die 'eval resource cannot be destination'; }
bobshell_resource_copy_to_stdin()         { bobshell_die 'cannot write to stdin resource'; }
bobshell_resource_copy_stdout()           { bobshell_die 'cannot read from stdout resource'; }
bobshell_resource_copy_to_url()           { bobshell_die 'cannot write to stdin resource'; }



bobshell_resource_copy_val_to_val()       { test "$1" != "$2" && bobshell_resource_copy_to_val; }
bobshell_resource_copy_val_to_var()       {
	bobshell_str_quote "$1"	
	eval "$2=$bobshell_result_1"
}
bobshell_resource_copy_val_to_eval()      { eval "$1"; }
bobshell_resource_copy_val_to_stdin()     { bobshell_resource_copy_to_stdin; }
bobshell_resource_copy_val_to_stdout()    { printf %s "$1"; }
bobshell_resource_copy_val_to_file()      { printf %s "$1" > "$2"; }
bobshell_resource_copy_val_to_url()       { bobshell_resource_copy_to_url; }



bobshell_resource_copy_var_to_val()       { bobshell_resource_copy_to_val; }
bobshell_resource_copy_var_to_var()       { test "$1" != "$2" && eval "$2=\"\$$1\""; }
bobshell_resource_copy_var_to_eval()      { eval "bobshell_resource_copy_var_to_eval \"\$$1\""; }
bobshell_resource_copy_var_to_stdin()     { bobshell_resource_copy_to_stdin; }
bobshell_resource_copy_var_to_stdout()    { eval "printf %s \"\$$1\""; }
bobshell_resource_copy_var_to_file()      { eval "printf %s \"\$$1\"" > "$2"; }
bobshell_resource_copy_var_to_url()       { bobshell_resource_copy_to_url; }



bobshell_resource_copy_eval_to_val()      { bobshell_resource_copy_eval; }
bobshell_resource_copy_eval_to_var()      { bobshell_resource_copy_eval; }
bobshell_resource_copy_eval_to_eval()     { bobshell_resource_copy_eval; }
bobshell_resource_copy_eval_to_stdin()    { bobshell_resource_copy_eval; }
bobshell_resource_copy_eval_to_stdout()   { bobshell_resource_copy_eval; }
bobshell_resource_copy_eval_to_file()     { bobshell_resource_copy_eval; }
bobshell_resource_copy_eval_to_url()      { bobshell_resource_copy_eval; }



bobshell_resource_copy_stdin_to_val()     { bobshell_resource_copy_to_val; }
bobshell_resource_copy_stdin_to_var()     { eval "$2=\$(cat)"; }
bobshell_resource_copy_stdin_to_eval()    {
	bobshell_resource_copy_stdin_to_var "$1" bobshell_resource_copy_stdin_to_eval_data
	bobshell_resource_copy_var_to_eval bobshell_resource_copy_stdin_to_eval_data ''
	unset bobshell_resource_copy_stdin_to_eval_data; 
}
bobshell_resource_copy_stdin_to_stdin()   { bobshell_resource_copy_to_stdin; }
bobshell_resource_copy_stdin_to_stdout()  { cat; }
bobshell_resource_copy_stdin_to_file()    { cat > "$2"; }
bobshell_resource_copy_stdin_to_url()     { bobshell_resource_copy_to_url; }



bobshell_resource_copy_stdout_to_val()    { bobshell_resource_copy_stdout; }
bobshell_resource_copy_stdout_to_var()    { bobshell_resource_copy_stdout; }
bobshell_resource_copy_stdout_to_eval()   { bobshell_resource_copy_stdout; }
bobshell_resource_copy_stdout_to_stdin()  { bobshell_resource_copy_stdout; }
bobshell_resource_copy_stdout_to_stdout() { bobshell_resource_copy_stdout; }
bobshell_resource_copy_stdout_to_file()   { bobshell_resource_copy_stdout; }
bobshell_resource_copy_stdout_to_url()    { bobshell_resource_copy_to_url; }


bobshell_resource_copy_file_to_val()      { bobshell_resource_copy_to_val; }
bobshell_resource_copy_file_to_var()      { eval "$2=\$(cat '$1'; printf z); $2=\${$2%z}"; }
bobshell_resource_copy_file_to_eval()     {
	bobshell_resource_copy_file_to_var "$1" bobshell_resource_copy_file_to_eval_data
	bobshell_resource_copy_var_to_eval bobshell_resource_copy_file_to_eval_data ''
	unset bobshell_resource_copy_file_to_eval_data; 
}
bobshell_resource_copy_file_to_stdin()    { bobshell_resource_copy_to_stdin; }
bobshell_resource_copy_file_to_stdout()   { cat "$1"; }
bobshell_resource_copy_file_to_file()     { test "$1" != "$2" && { mkdir -p "$(dirname "$2")" && rm -rf "$2" && cp -f "$1" "$2";}; }
bobshell_resource_copy_file_to_url()      { bobshell_resource_copy_to_url; }



bobshell_resource_copy_url_to_val()       { bobshell_resource_copy_to_val; }
bobshell_resource_copy_url_to_var()       { eval "$2"'=$(bobshell_fetch_url '"'""$1""'"')'; }
bobshell_resource_copy_url_to_eval()      {
	bobshell_resource_copy_url_to_var "$1" _bobshell_resource_copy_url_to_eval
	eval "$_bobshell_resource_copy_url_to_eval"
	unset _bobshell_resource_copy_url_to_eval 
}
bobshell_resource_copy_url_to_stdin()     { bobshell_resource_copy_to_stdin; }
bobshell_resource_copy_url_to_stdout()    { bobshell_fetch_url "$1"; }
bobshell_resource_copy_url_to_file()      { bobshell_fetch_url "$1" > "$2"; }
bobshell_resource_copy_url_to_url()       { bobshell_resource_copy_to_url; }






# disable recursive dependency resolution when building shelduck itself
# shelduck import ./read.sh

bobshell_result_check() {
	if [ '0' = "${bobshell_result_size:-0}" ]; then
		bobshell_die "bobshell_result_check: no result"
	fi
	case "$bobshell_result_1" in
		(true)  ;;
		(false) return 1 ;;
		(*) bobshell_die "bobshell_result_check: error parsing result as boolean: $bobshell_result_1"
	esac
	bobshell_result_read _bobshell_result_check__unused "$@"
	unset _bobshell_result_check__unused
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import resource/copy.sh


bobshell_scope_names() {
	for bobshell_scope_names_scope in "$@"; do
		bobshell_scope_names_all=$(set | sed -n "s/^\($bobshell_scope_names_scope[A-Za-z_0-9]*\)=.*$/\1/pg" | sort -u)
		for bobshell_scope_names_item in $bobshell_scope_names_all; do
			if bobshell_isset "$bobshell_scope_names_item"; then
				printf ' %s' "$bobshell_scope_names_item"
			fi
		done
	done
	unset bobshell_scope_names_all bobshell_scope_names_scope bobshell_scope_names_item
}



bobshell_scope_unset() {
	for bobshell_scope_unset_name in $(bobshell_scope_names "$@"); do
		unset "$bobshell_scope_unset_name"
	done
	unset bobshell_scope_unset_name
}



bobshell_scope_export() {
	for bobshell_scope_export_name in $(bobshell_scope_names "$@"); do
		export "$bobshell_scope_export_name"
	done
	unset bobshell_scope_export_name
}



bobshell_scope_env() {
	bobshell_scope_env_result=
	for bobshell_scope_env_name in $(bobshell_scope_names "$1"); do
		bobshell_scope_env_result="$bobshell_scope_env_result$bobshell_scope_env_name="
		bobshell_scope_env_value=$(bobshell_getvar "$bobshell_scope_env_name")
		bobshell_scope_env_value=$(bobshell_quote "$bobshell_scope_env_value")
		bobshell_scope_env_result="$bobshell_scope_env_result$bobshell_scope_env_value$bobshell_newline"
	done
	bobshell_resource_copy var:bobshell_scope_env_result "$2"
	unset bobshell_scope_env_result bobshell_scope_env_name bobshell_scope_env_value
}


# fun: bobshell_scope_copy SRCSCOPE DESTSCOPE
bobshell_scope_copy() {
	for bobshell_scope_copy_name in $(bobshell_scope_names "$1"); do
		bobshell_scope_copy_value=$(bobshell_getvar "$bobshell_scope_copy_name")
		bobshell_remove_prefix "$bobshell_scope_copy_name" "$1" bobshell_scope_copy_name
		bobshell_putvar "$2$bobshell_scope_copy_name" "$bobshell_scope_copy_value"
	done
	unset bobshell_scope_copy_name bobshell_scope_copy_value
}


# fun: bobshell_scope_mirror SRCSCOPE DESTSCOPE
bobshell_scope_mirror() {
	bobshell_scope_unset "$2"
	bobshell_scope_copy "$@"
}






# STRING MANUPULATION

# disable recursive dependency resolution when building shelduck itself
# shelduck import base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./regex/match.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./str/replace.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./str/quote.sh


# use: bobshell_starts_with hello he && echo "$rest" # prints llo
bobshell_starts_with() {
	bobshell_starts_with_str="$1"
	shift
	while bobshell_isset_1 "$@"; do
		case "$bobshell_starts_with_str" in
			("$1"*) 
				unset bobshell_starts_with_str			
				return 0
		esac
		shift
	done
	unset bobshell_starts_with_str
	return 1
}

# use: bobshell_starts_with hello he rest && echo "$rest" # prints llo
bobshell_remove_prefix() {
	if [ -z "$2" ]; then
		return 0
	fi
	set -- "$1" "$2" "$3" "${1#"$2"}"
	if [ "$1" = "$4" ]; then
		return 1
	fi
	if [ -n "$3" ]; then
		bobshell_putvar "$3" "$4"
	fi	
}

# use: bobshell_starts_with hello he rest && echo "$rest" # prints llo
bobshell_ends_with() {
	bobshell_isset_3 "$@" && bobshell_die "bobshell_ends_with takes 2 arguments, 3 given, did you mean bobshell_remove_suffix?" || true
	case "$1" in
		(*"$2") return 0
	esac
	return 1
}

bobshell_remove_suffix() {
	if [ -z "$2" ]; then
		return 0
	fi
	set -- "$1" "$2" "$3" "${1%"$2"}"
	if [ "$1" = "$4" ]; then
		return 1
	fi
	if [ -n "$3" ]; then
		bobshell_putvar "$3" "$4"
	fi
}


# fun: bobshell_contains STR SUBSTR
bobshell_contains() {
	case "$1" in
		(*"$2"*) return 0
	esac
	return 1
}


# fun: bobshell_split_first STR SUBSTR [PREFIX [SUFFIX]]
bobshell_split_first() {
	set -- "$1" "$2" "${3:-}" "${4:-}" "${1#*"$2"}"
	if [ "$1" = "$5" ]; then
		return 1
	fi
	if [ -n "${3:-}" ]; then
		bobshell_putvar "$3" "${1%%"$2"*}"
	fi
	if [ -n "${4:-}" ]; then
		bobshell_putvar "$4" "$5"
	fi
}

# fun: bobshell_split_last STR SUBSTR [PREFIX [SUFFIX]]
bobshell_split_last() {
	set -- "$1" "$2" "${3:-}" "${4:-}" "${1%"$2"*}"
	if [ "$1" = "$5" ]; then
		return 1
	fi
	if [ -n "${3:-}" ]; then
		bobshell_putvar "$3" "$5"
	fi
	if [ -n "${4:-}" ]; then
		bobshell_putvar "$4" "${1##*"$2"}"
	fi
}


# txt: заменить в $1 все вхождения строки $2 на строку $3
# use: replace_substring hello e E
# DEPRECATED: str_replace
bobshell_replace() {
	bobshell_str_replace "$@"
	printf %s "$bobshell_result_1"
}






# fun: bobshell_substr STR RANGE OUTPUTVAR
bobshell_substr() {
	bobshell_die "not implemented"
	
	set -- "$1"
	bobshell_substr_result=$(printf %s "$1" | cut -c "$2-$3")
	col2="$(printf 'foo    bar  baz\n' | cut -c 8-12)"

	unset bobshell_substr_result
}



# txt: regex should be in the basic form (https://www.gnu.org/software/grep/manual/html_node/Basic-vs-Extended.html)
#      ^ is implicitly prepended to regexp
#      https://stackoverflow.com/questions/35693980/test-for-regex-in-string-with-a-posix-shell#comment86337738_35694108
# DEPRECATED
bobshell_basic_regex_match() {
	bobshell_regex_match "$@"
}

bobshell_extended_regex_match() {
	printf %s "$1" | grep --silent --extended-regex "$2"
}

# fun: shelduck_for_each_line STR SEPARATOR VAR COMMAND
# txt: supports recursion
bobshell_for_each_part() {
	while [ -n "$1" ]; do
		if ! bobshell_split_first \
				"$1" \
				"$2" \
				bobshell_for_each_part_current \
				bobshell_for_each_part_rest; then
			# shellcheck disable=SC2034
			# part used in eval
			bobshell_for_each_part_current="$1"
			bobshell_for_each_part_rest=
		fi
		bobshell_for_each_part_separator="$2"
		bobshell_for_each_part_varname="$3"
		shift 3
		bobshell_for_each_part_command="$*"
		set -- "$bobshell_for_each_part_rest" "$bobshell_for_each_part_separator" "$bobshell_for_each_part_varname" "$@"
		bobshell_putvar "$bobshell_for_each_part_varname" "$bobshell_for_each_part_current"
		$bobshell_for_each_part_command
	done
	unset bobshell_for_each_part_rest bobshell_for_each_part_separator bobshell_for_each_part_varname bobshell_for_each_part_command "$3"
}




bobshell_assing_new_line() {
	bobshell_putvar "$1" '
'
}

bobshell_newline='
'

# DEPRECATED: use bobshell_str_quote
bobshell_quote() {
	bobshell_str_quote "$@"
	printf %s "$bobshell_result_1"
}


# fun: bobshell_join SEPARATOR [ITEM...]
bobshell_join() {
	bobshell_join_separator="$1"
	shift
	for bobshell_join_item in "$@"; do
		printf %s "$bobshell_join_item"
		break
	done
	shift
	for bobshell_join_item in "$@"; do
		printf %s "$bobshell_join_separator"
		printf %s "$bobshell_join_item"
	done
}



bobshell_strip_left() {
	bobshell_strip_left_value="$1"
	while true; do
		case "$bobshell_strip_left_value" in 
			([[:space:]]*)
				bobshell_strip_left_value="${bobshell_strip_left_value#?}" ;;
			(*) break ;;
		esac
	done
	printf %s "$bobshell_strip_left_value"
}

bobshell_strip_right() {
	bobshell_strip_right_value="$1"
	while true; do
		case "$bobshell_strip_right_value" in 
			(*[[:space:]])
				bobshell_strip_right_value="${bobshell_strip_right_value%?}" ;;
			(*) break ;;
		esac
	done
	printf %s "$bobshell_strip_right_value"
}

bobshell_strip() {
	bobshell_strip_value=$(bobshell_strip_left "$1")
	bobshell_strip_right "$bobshell_strip_value"
}

bobshell_upper_case() {
	printf %s "$*" | awk 'BEGIN { getline; print toupper($0) }'
}

bobshell_lower_case() {
	printf %s "$*" | awk 'BEGIN { getline; print tolower($0) }'
}





# shellcheck disable=SC2148

# disable recursive dependency resolution when building shelduck itself
# shelduck import ./base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./string.sh


bobshell_fetch_url() {
	if bobshell_remove_prefix "$1" 'file://' bobshell_fetch_url_path; then
		# shellcheck disable=SC2154
		# bobshell_remove_prefix sets variable bobshell_fetch_url_path indirectly
		cat "$bobshell_fetch_url_path"
		unset bobshell_fetch_url_path
	elif bobshell_command_available curl; then
		bobshell_fetch_url_with_curl "$1"
	elif bobshell_command_available wget; then
		bobshell_fetch_url_with_wget "$1"
	else
		bobshell_die 'error: neither curl nor wget installed'
	fi
}

# fun: bobshell_base_url http://domain/dir/file # prints http://domain/dir/
bobshell_base_url() {
	printf %s/ "${1%/*}"
}


# fun: bobshell_resolve_url URL [BASEURL]
bobshell_resolve_url() {
	# todo by default BASEURL is $(realpath "$(pwd)")
	if bobshell_starts_with "$1" /; then
		bobshell_resolve_url_path=$(realpath "$1")
		printf 'file://%s' "$bobshell_resolve_url_path"
	elif bobshell_remove_prefix "$1" file:// bobshell_resolve_url_path; then
		bobshell_resolve_url_path=$(realpath "$bobshell_resolve_url_path")
		printf 'file://%s' "$bobshell_resolve_url_path"
	elif bobshell_starts_with "$1" http:// \
	  || bobshell_starts_with "$1" https:// \
	  || bobshell_starts_with "$1" ftp:// \
	  || bobshell_starts_with "$1" ftps:// \
			; then
		printf %s "$1"
	else
		if bobshell_isset_2 "$@"; then
			bobshell_resolve_url_base="$2"	
			while bobshell_remove_suffix "$bobshell_resolve_url_base" / bobshell_resolve_url_base; do
				true
			done
		else
			bobshell_resolve_url_base=$(pwd)
		fi

		bobshell_resolve_url_value="$1"
		while bobshell_remove_prefix "$bobshell_resolve_url_value" './' bobshell_resolve_url_value; do
			true
		done


		while bobshell_remove_prefix "$bobshell_resolve_url_value" '../' bobshell_resolve_url_value; do
			if ! bobshell_split_last "$bobshell_resolve_url_base" / bobshell_resolve_url_base; then
				bobshell_die "bobshell_resolve_url: base=$bobshell_resolve_url_base, url=$bobshell_resolve_url_value"
			fi
		done

		printf '%s/%s' "$bobshell_resolve_url_base" "$bobshell_resolve_url_value"
		unset bobshell_resolve_url_base bobshell_resolve_url_value
	fi
}

bobshell_fetch_url_with_curl() {
	curl --fail --silent --show-error --location "$1"
}

bobshell_fetch_url_with_wget() {
	wget --no-verbose --output-document -
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import git.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import resource/copy.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./eval.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./var/get.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./result/check.sh

bobshell_current_seconds() {
	date +%s
}



# fun: save_output VARIABLE COMMAND [ARG...]
bobshell_save_output() {
	save_output_var="$1"
	shift
	save_output=$("$@")
	bobshell_putvar "$save_output_var" "$save_output"
	unset save_output_var save_output
}



bobshell_eval_output() {
	# stdout:cat
	# stdin:cat
	# todo: copy_resource "stdout:$*" "eval:"
	bobshell_eval_output=$("$@")
	eval "$bobshell_eval_output"
	unset bobshell_eval_output
}


# txt: read -sr 
bobshell_read_secret() {
	# https://github.com/biox/pa/blob/main/pa
	[ -t 0 ] && stty -echo
	read -r "$1"
	[ -t 0 ] &&  stty echo
}



bobshell_run_url() {
	if bobshell_command_available "$1"; then
		"$@"
	elif [ -z "$1" ]; then
		"$@"
	elif bobshell_ends_with "$1" '.git'; then
		bobshell_run_url_git "$@"
	else
		bobshell_die "bobshell_run_url: unrecognized parameters: $(boshell_quote "$@")"
	fi
}

bobshell_run_url_git() {
	bobshell_run_url_git_dir=$(mktemp -d)
	chmod u+rwx "$bobshell_run_url_git_dir"
	bobshell_git clone "$1" "$bobshell_run_url_git_dir"
	"$bobshell_run_url_git_dir/run" "$@"
}

# txt: выполнить команду, восстановить после неё значения переменных окружения
# use: X=1; Y=2; preserve_environment 'eval' 'X=2, Z=3'; echo "$X, $Y, $Z" # gives 1, 2, 3
bobshell_preserve_env() {
	_bobshell_preserve_env=
	for _x in $(set | sed -n "s/^\([A-Za-z_][A-Za-z0-9_]*\)=.*$/\1/pg"); do
		bobshell_var_get "$_x"
		if ! bobshell_result_check _v; then
			continue
		fi
		bobshell_str_quote "$_v"
		_v="$bobshell_result_1"
		_bobshell_preserve_env="$_bobshell_preserve_env
bobshell_preserve_env_item_load $_x $_v"
		unset _v
	done
	unset _x
	"$@"
	eval "$_bobshell_preserve_env"
	unset _bobshell_preserve_env
}

bobshell_preserve_env_item_load() {
	if bobshell_isset "$1"; then
		_x=$(bobshell_getvar "$1")
		if [ "$_x" = "$2" ]; then
			return
		fi
		bobshell_putvar "$1" "$2"
	fi
}


bobshell_is_root() {
	test 0 = "$(id -u)"
}

bobshell_is_not_root() {
	test 0 != "$(id -u)"
}

# fun: shelduck_eval_with_args SCRIPT [ARGS...]
# todo 
shelduck_eval_with_args() { 
	shelduck_eval_with_args_script="$1"
	shift
	eval "$shelduck_eval_with_args_script"
}


bobshell_uid() {
	id -u
}

bobshell_gid() {
	id -g
}


bobshell_user_name() {
	printf %s "$USER" # todo
}



bobshell_user_home() {
	printf %s "$HOME" # todo
}

bobshell_get_file_mtime() {

	# LC_TIME=en_US.UTF-8 ls -ld ./pom.xml | sed -n 's/^.* \([A-Z][a-z]\{2\} \+[0-9]\+\).*$/\1/p'
	#LC_TIME=en_US.UTF-8 ls -ld ./pom.xml | sed -n 's/^.* \(\(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec\) \+[0-9]\+ \+\).*$/\1/p'

	LC_TIME=en_US.UTF-8 ls -ld ./pom.xml | sed -n 's/^.* \(\(Jan\|Feb\|Mar\|Apr\|May\|Jun\|Jul\|Aug\|Sep\|Oct\|Nov\|Dec\) \+[1-9]\+ \+[0-9]\+\:[0-9]\+\).*$/\1/p'
	# 

	bobshell_get_file_mtime_dirname=$(dirname "$1")
	bobshell_get_file_mtime_basename=$(basename "$1")
	find "$bobshell_get_file_mtime_dirname" -maxdepth 1 -name "$bobshell_get_file_mtime_basename" -printf "%Ts"
	unset bobshell_get_file_mtime_dirname bobshell_get_file_mtime_basename
}

# bobshell_line_in_file: 
bobshell_line_in_file() {
	true
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh

bobshell_str_replace() {
  	# https://freebsdfrau.gitbook.io/serious-shell-programming/string-functions/replace_substringall
	_bobshell_replace__rest="$1"
	_bobshell_replace__result=
	while bobshell_split_first "$_bobshell_replace__rest" "$2" _bobshell_replace_left _bobshell_replace__rest; do
		_bobshell_replace__result="$_bobshell_replace__result$_bobshell_replace_left$3"
	done
	_bobshell_replace__result="$_bobshell_replace__result$_bobshell_replace__rest"
	bobshell_result_set "$_bobshell_replace__result"
	unset _bobshell_replace__rest _bobshell_replace__result _bobshell_replace_left 
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../regex/match.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./replace.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./quote.sh


bobshell_str_quote() {
	_bobshell_str_quote__separator=
	_bobshell_str_quote__result=
	while bobshell_isset_1 "$@"; do
		if [ -z "$1" ]; then
			_bobshell_str_quote__result="$_bobshell_str_quote__result$_bobshell_str_quote__separator''"
		elif bobshell_regex_match "$1" '[-A-Za-z0-9_/=\.]\+'; then
			_bobshell_str_quote__result="$_bobshell_str_quote__result$_bobshell_str_quote__separator$1"
		else
			bobshell_str_replace "$1" "'" "'"'"'"'"'"'"'"
			_bobshell_str_quote__result="$_bobshell_str_quote__result$_bobshell_str_quote__separator'$bobshell_result_1'"
		fi
		_bobshell_str_quote__separator=' '
		shift
	done
	unset _bobshell_str_quote__separator
	bobshell_result_set "$_bobshell_str_quote__result"
	unset _bobshell_str_quote__result
}






bobshell_append_val_to_var() {
	eval "$2=\"\${$2:-}\$1\""
}






bobshell_code_defun() {
	printf '%s() {\n' "$1"
	shift
	printf '%s\n' "$@"
	printf '}'
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../code/defun.sh

bobshell_defun() {
	_bobshell_defun__script=$(bobshell_code_defun "$@")
	eval "$_bobshell_defun__script"
	unset _bobshell_defun__script
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh

bobshell_var_get() {
	if bobshell_isset "$1"; then
		eval "bobshell_result_set true \"\$$1\""
	else
		bobshell_result_set false
	fi
}






bobshell_var_set() {
	eval "$1=\"\$2\""
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh

bobshell_var_default() {
	if ! bobshell_isset "$1"; then
		bobshell_var_set "$@"
	fi
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/check.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./get.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./set.sh

bobshell_var_append() {
	bobshell_var_get "$1"
	if ! bobshell_result_check _bobshell_var_append__value; then
		return
	fi
	_bobshell_var_append__value="$_bobshell_var_append__value$2"
	bobshell_var_set "$1" "$_bobshell_var_append__value"
	bobshell_result_set true "$_bobshell_var_append__value"
	unset _bobshell_var_append__value
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../misc/defun.sh

bobshell_event_compile() {
	_bobshell_event_compile__name="$1"
	shift
	_bobshell_event_compile__code=$(bobshell_getvar "$_bobshell_event_compile__name" '')
	if bobshell_isset "${_bobshell_event_compile__name}_template"; then
		_bobshell_event_compile__template=$(bobshell_getvar "${_bobshell_event_compile__name}_template")
		_bobshell_event_compile__code=$(bobshell_replace "$_bobshell_event_compile__template" '{}' "$_bobshell_event_compile__code")
		unset _bobshell_event_compile__template
	fi
	bobshell_defun "$_bobshell_event_compile__name" "${_bobshell_event_compile__code:-true}"
	unset _bobshell_event_compile__code
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./compile.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../misc/defun.sh

bobshell_event_fire() {
	if ! bobshell_command_available "$1"; then
		bobshell_event_compile "$1"
	fi
	"$@"
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../append/val_to_var.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../string.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./compile.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../misc/defun.sh

bobshell_event_listen() {
	_bobshell_event_listen__name="$1"
	shift
	if [ -z "${*:-}" ]; then
		return
	fi
	bobshell_append_val_to_var "$bobshell_newline$bobshell_newline$*$bobshell_newline" "$_bobshell_event_listen__name"

	# shellcheck disable=SC2016
	bobshell_defun "$_bobshell_event_listen__name" "bobshell_event_compile $_bobshell_event_listen__name
$_bobshell_event_listen__name \"\$@\""
	unset _bobshell_event_listen__name
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../resource/copy.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_stdin.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_stdout.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_file.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../redirect/io.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../redirect/input.sh

# fun: bobshell_awk INPUT OUTPUT AWKARGS...
bobshell_awk() {
	bobshell_isset_3 "$@" || bobshell_die 'bobshell_awk: 3 arguments required'
	
	bobshell_awk__input="$1"
	shift

	bobshell_awk__output="$1"
	shift
	
	if bobshell_locator_is_file "$bobshell_awk__input" bobshell_awk__input_file; then
		if [ "$bobshell_awk__input" = "$bobshell_awk__output" ]; then
			bobshell_redirect_output var:_bobshell_awk__buffer awk "$@" "$bobshell_awk__input_file"
			bobshell_resource_copy_var_to_file _bobshell_awk__buffer "$bobshell_awk__input_file"
			unset _bobshell_awk__buffer
		else
			bobshell_redirect_output "$bobshell_awk__output" awk "$@" "$bobshell_awk__input_file"
		fi
		unset bobshell_awk__input_file
	else
		bobshell_redirect_io "$bobshell_awk__input" "$bobshell_awk__output" awk "$@"
		unset bobshell_awk__input bobshell_awk__output
	fi
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh

bobshell_equals_any() {
	if ! bobshell_isset_2 "$@"; then
		return 1
	elif ! bobshell_isset_3 "$@"; then
		if [ "$1" = "$2" ]; then
			return 0
		else
			return 1
		fi
	fi
	bobshell_equals_value="$1"
	shift
	while bobshell_isset_1 "$@"; do
		if [ "$bobshell_equals_value" = "$1" ];  then
			return
		fi
		shift
	done
	unset bobshell_equals_value
	return 1
}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../resource/copy.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_stdin.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_stdout.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_val.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_file.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../event/listen.sh

bobshell_event_listen bobshell_error_exit_event bobshell_redirect_input_exit_event_listener
bobshell_redirect_input_exit_event_listener() {
	if bobshell_isset bobshell_redirect_input_dd_pid; then
		echo 'exit event: kill dd' >&2
		kill "$bobshell_redirect_input_dd_pid"
	fi
}

# fun: bobshell_redirect_input INPUT COMMAND [ARGS...]
bobshell_redirect_input() {
	if bobshell_locator_is_stdin "$1"; then
		shift
		"$@"
	elif bobshell_locator_is_file "$1" _bobshell_redirect_input__file; then
		shift
		"$@" < "$_bobshell_redirect_input__file"
		unset _bobshell_redirect_input__file
	else
		_bobshell_redirect_input__temp=$(mktemp -d) # todo common temp dir for all would be more performant
		chmod u+rwx "$_bobshell_redirect_input__temp"
		mkfifo "$_bobshell_redirect_input__temp/1" "$_bobshell_redirect_input__temp/2"
		dd "if=$_bobshell_redirect_input__temp/1" "of=$_bobshell_redirect_input__temp/2" status=none &
		bobshell_redirect_input_dd_pid=$!
		bobshell_resource_copy "$1" "$_bobshell_redirect_input__temp/1"
		shift
		unset bobshell_redirect_input_dd_pid
		"$@" < "$_bobshell_redirect_input__temp/2"
		rm -rf "$_bobshell_redirect_input__temp"
		unset _bobshell_redirect_input__temp
	fi
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ./input.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./output.sh

# fun: bobshell_redirect INPUT OUTPUT COMMAND [ARGS...]
bobshell_redirect_io() {
	_bobshell_redirect_io__src="$1"
	shift
	bobshell_redirect_input "$_bobshell_redirect_io__src" bobshell_redirect_output "$@"
	unset _bobshell_redirect_io__src
}









# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../resource/copy.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_stdin.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_stdout.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_var.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../locator/is_file.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../event/listen.sh


bobshell_event_listen bobshell_error_exit_event bobshell_redirect_output_exit_event_listener
bobshell_redirect_output_exit_event_listener() {
	if bobshell_isset bobshell_redirect_output_dd_pid; then
		echo 'exit event: kill dd' >&2
		kill "$bobshell_redirect_output_dd_pid"
	fi
}


# fun: bobshell_redirect_output OUTPUT COMMAND [ARGS...]
bobshell_redirect_output() {
	if bobshell_locator_is_stdout "$1"; then
		shift
		"$@"
	elif bobshell_locator_is_file "$1" _bobshell_redirect_output__file; then
		shift
		"$@" > "$_bobshell_redirect_output__file"
		unset _bobshell_redirect_output__file
	else
		# use https://stackoverflow.com/a/21635000 hack to avoid subshells
		_bobshell_redirect_output="$1"
		shift
		_bobshell_redirect_output__temp=$(mktemp -d)
		chmod u+rwx "$_bobshell_redirect_output__temp"
		mkfifo "$_bobshell_redirect_output__temp/1" "$_bobshell_redirect_output__temp/2"
		dd "if=$_bobshell_redirect_output__temp/1" "of=$_bobshell_redirect_output__temp/2" status=none &
		bobshell_redirect_output_dd_pid=$!
		"$@" > "$_bobshell_redirect_output__temp/1"
		bobshell_resource_copy "file://$_bobshell_redirect_output__temp/2" "$_bobshell_redirect_output"
		unset bobshell_redirect_output_dd_pid
		rm -rf "$_bobshell_redirect_output__temp"
		unset _bobshell_redirect_output__temp _bobshell_redirect_output
	fi
}








bobshell_regex_match() {
	_bobshell_regex_match=$(expr "$1" : "$2")
	if [ "$_bobshell_regex_match" = "${#1}" ]; then
		unset _bobshell_regex_match
		return
	else
		unset _bobshell_regex_match
		return 1
	fi
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../resource/copy.sh

# fun: bobshell_result_get VAR ...
bobshell_result_read() {

	if [ "$#" -gt "${bobshell_result_size:-0}" ]; then
		bobshell_die "number of resulting variables ($#) is greater than number of available values (${bobshell_result_size:-0}) "
	fi

	if   [ 1 = "$#" ]; then
		bobshell_resource_copy_var_to_var bobshell_result_1 "$1"
	elif [ 2 = "$#" ]; then
		bobshell_resource_copy_var_to_var bobshell_result_1 "$1"
		bobshell_resource_copy_var_to_var bobshell_result_2 "$2"
	elif [ 3 = "$#" ]; then
		bobshell_resource_copy_var_to_var bobshell_result_1 "$1"
		bobshell_resource_copy_var_to_var bobshell_result_2 "$2"
		bobshell_resource_copy_var_to_var bobshell_result_3 "$3"
	elif [ 4 = "$#" ]; then
		bobshell_resource_copy_var_to_var bobshell_result_1 "$1"
		bobshell_resource_copy_var_to_var bobshell_result_2 "$2"
		bobshell_resource_copy_var_to_var bobshell_result_3 "$3"
		bobshell_resource_copy_var_to_var bobshell_result_4 "$4"
	elif [ 5 = "$#" ]; then
		bobshell_resource_copy_var_to_var bobshell_result_1 "$1"
		bobshell_resource_copy_var_to_var bobshell_result_2 "$2"
		bobshell_resource_copy_var_to_var bobshell_result_3 "$3"
		bobshell_resource_copy_var_to_var bobshell_result_4 "$4"
		bobshell_resource_copy_var_to_var bobshell_result_5 "$5"
	else
		for _bobshell_result_read__i in $(seq "$#"); do
			bobshell_resource_copy_var_to_var "bobshell_result_$_bobshell_result_read__i" "$1"
			shift
			if ! bobshell_isset_1 "$@"; then
				break
			fi
		done
		unset _bobshell_result_read__i
	fi

}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/unset.sh


# fun: bobshell_result_set [ITEMS...]
bobshell_result_set() {
	if [ "${bobshell_result_size:-0}" -lt 4 ] && [ "$#" -lt 4 ]; then
		if   [ 0 = "$#" ]; then
			bobshell_result_size=0
			unset bobshell_result_1 bobshell_result_2 bobshell_result_3
			return
		elif [ 1 = "$#" ]; then
			bobshell_result_size=1
			bobshell_result_1="$1"
			unset bobshell_result_2 bobshell_result_3
			return
		elif [ 2 = "$#" ]; then
			bobshell_result_size=2
			bobshell_result_1="$1"
			bobshell_result_2="$2"
			unset bobshell_result_3
			return
		elif [ 3 = "$#" ]; then
			bobshell_result_size=3
			bobshell_result_1="$1"
			bobshell_result_2="$2"
			bobshell_result_3="$3"
			return
		fi
	fi

	bobshell_result_unset
	bobshell_result_size=0
	while bobshell_isset_1 "$@"; do
		bobshell_result_size=$(( 1 + bobshell_result_size ))
		bobshell_putvar "bobshell_result_$bobshell_result_size" "$1"
		shift
	done
}






bobshell_result_unset() {
	if   [ 0 = "${bobshell_result_size:-0}" ]; then
		unset bobshell_result_size
	elif [ 1 = "$bobshell_result_size" ]; then
		unset bobshell_result_size bobshell_result_1
	elif [ 2 = "$bobshell_result_size" ]; then
		unset bobshell_result_size bobshell_result_1 bobshell_result_2
	elif [ 3 = "$bobshell_result_size" ]; then
		unset bobshell_result_size bobshell_result_1 bobshell_result_2 bobshell_result_3
	else
		while [ 0 -lt "$bobshell_result_size" ]; do
			unset "bobshell_result_$bobshell_result_size"
			bobshell_result_size=$(( bobshell_result_size - 1 ))
		done
		unset bobshell_result_size
	fi	
}





# use: notrace echo hello
# txt: выполнить команду, скрывая трассировку от set -x
bobshell_notrace() {
	{ "$@"; } 2> /dev/null
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../str/quote.sh

# disable recursive dependency resolution when building shelduck itself
# shelduck import ../event/listen.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../event/fire.sh

# disable recursive dependency resolution when building shelduck itself
# shelduck import ../var/default.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../var/append.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ./parse.sh


bobshell_event_listen bobshell_cli_setup_start_event '
	unset _bobshell_cli_setup__help

	unset _bobshell_cli_setup__arg_listener

	unset _bobshell_cli_setup__var
	_bobshell_cli_setup__param=false
	_bobshell_cli_setup__flag=false
	
	_bobshell_cli_setup__default_unset=false
	unset _bobshell_cli_setup__default_value

	unset _bobshell_cli_setup__flag_value
	_bobshell_cli_setup__append=false
	_bobshell_cli_setup__separator=	
'

bobshell_event_listen bobshell_cli_setup_clear_event '
	unset _bobshell_cli_setup__help

	unset _bobshell_cli_setup__arg_listener

	unset _bobshell_cli_setup__var
	unset _bobshell_cli_setup__param
	unset _bobshell_cli_setup__flag
	
	unset _bobshell_cli_setup__default_unset
	unset _bobshell_cli_setup__default_value

	unset _bobshell_cli_setup__flag_value
	unset _bobshell_cli_setup__append
	unset _bobshell_cli_setup__separator
	
'

# shellcheck disable=SC2016
bobshell_event_listen bobshell_cli_setup_arg_event '
	case "$1" in
		(h|help|usage)
			_bobshell_cli_setup__help="$2" ;;

		(l|listener)
			_bobshell_cli_setup__arg_listener="$2" ;;

		(v|var|variable)
			_bobshell_cli_setup__var="$2" ;;

		(p|param)
			_bobshell_cli_setup__param=true ;;
		(f|flag)
			_bobshell_cli_setup__flag=true ;;

		(u|default-unset)
			_bobshell_cli_setup__default_unset=true ;;
		(d|default-value)
			_bobshell_cli_setup__default_value="$2" ;;


		(f|flag-value)
			_bobshell_cli_setup__flag_value="$2" ;;
		(a|append)
			_bobshell_cli_setup__append=true ;;
		(s|separator)
			_bobshell_cli_setup__separator="$2" ;;
		
		(*) bobshell_die "bobshell_cli_setup: unknown argument: $1"
	esac
'


bobshell_cli_setup_params='h help usage  l listener   v var variable  d default-value  f flag-value  s separator'
bobshell_cli_setup_flags='p param  f flag  u default-unset  a append'




# fun: bobshell_cli_setup
# use: bobshell_cli_setup SCOPE --usage 'blabla usage' --param --var=VARNAME --default-unset
#
# use: bobshell_cli_setup SCOPE --param --listener='var_param="$1"' p param
# use: bobshell_cli_setup SCOPE --flag  --listener='var_flag=true'  f flag
#
# use: bobshell_cli_setup SCOPE --param --var=VARNAME (--default-unset|--default-value=blablavalue) --append
# use: bobshell_cli_setup SCOPE --param --var=VARNAME (--default-unset|--default-value=blablavalue) --append
# use: bobshell_cli_setup SCOPE --flag  --var=VARNAME [--default-value=false] [--flag-value=true]
#
#
# Usage: [COMMON OPTIONS] (PARAM OPTIONS|FLAG OPTIONS) [ARGS]
# COMMON OPTIONS:
#     -h, -?, --help, --usage
#       show usage and exit
#
#     -p, --param
#       flag indicating param
#     -f, --flag
#       flag indicating flag
#
#     -l, --listener=LISTENERSCRIPT
#       define argument listener (param or flag)
#
#     -v, --var, --variable=VARIABLENAME
#       variable name to store flag value or param value
#     --default-value=VALUE
#       default 'false' for flags, undefined for params
#     --default-unset
#       default true for params, n/a for flags
#     --flag-value=FLAGVALUE
#       value to write to variable if flag is passed, default true, implies --flag, not compatible with --param
#     
#
#
# FLAG OPTIONS:

#
#
#
#
#
#
#
#
bobshell_cli_setup() {
	_bobshell_cli_setup__scope="$1"
	shift


	bobshell_cli_parse bobshell_cli_setup "$@"

	# VALIDATE NAMED ARGUMENTS
	if [ false = "$_bobshell_cli_setup__param" ] && [ false = "$_bobshell_cli_setup__flag" ]; then
		bobshell_die "bobshell_cli_setup: either --param or --flag required"
	fi

	if [ true = "$_bobshell_cli_setup__param" ] && [ true = "$_bobshell_cli_setup__flag" ]; then
		bobshell_die "bobshell_cli_setup: both --param or --flag forbidden"
	fi

	if ! bobshell_isset _bobshell_cli_setup__arg_listener && ! bobshell_isset _bobshell_cli_setup__var; then
		bobshell_die "bobshell_cli_setup: either --listener or --var required"
	fi

	if bobshell_isset _bobshell_cli_setup__arg_listener && bobshell_isset _bobshell_cli_setup__var; then
		bobshell_die "bobshell_cli_setup: both --listener and --var forbidden"
	fi

	if bobshell_isset _bobshell_cli_setup__var; then
		if ! bobshell_regex_match "$_bobshell_cli_setup__var" '[A-Za-z_][A-Za-z0-9_]*'; then
			bobshell_die "bobshell_cli_setup: malformed var name: $_bobshell_cli_setup__var"
		fi

	fi

	if bobshell_isset _bobshell_cli_setup__default_value && [ true = "$_bobshell_cli_setup__default_unset" ]; then
		bobshell_die "bobshell_cli_setup: both --default-value and --default-unset forbidden"
	fi

	if [ false = "$_bobshell_cli_setup__flag" ] && bobshell_isset _bobshell_cli_setup__flag_value; then
		bobshell_die "bobshell_cli_setup: --flag-value without --flag"
	fi

	# LISTENER --listener
	if bobshell_isset _bobshell_cli_setup__arg_listener; then
		bobshell_event_listen "$_bobshell_cli_setup__scope"_arg_event "$_bobshell_cli_setup__arg_listener"
	fi

	# VALIDATE POSITIONAL ARGUMENTS
	shift "$bobshell_cli_shift"
	if ! bobshell_isset_1 "$@"; then
		bobshell_die "bobshell_cli_setup: at least one positional argument expected"
	fi
	for _bobshell_cli_setup__i in "$@"; do
		if ! bobshell_regex_match "$_bobshell_cli_setup__i" '[A-Za-z0-9][-A-Za-z0-9]*'; then
			bobshell_die "bobshell_cli_setup: malformed option: $_bobshell_cli_setup__i"
		fi
	done
	unset _bobshell_cli_setup__i

	# 	
	if [ true = "$_bobshell_cli_setup__param" ]; then
		bobshell_var_default "$_bobshell_cli_setup__scope"_params ''
		bobshell_var_append  "$_bobshell_cli_setup__scope"_params " $*"
		
	elif [ true = "$_bobshell_cli_setup__flag" ]; then
		bobshell_var_default "$_bobshell_cli_setup__scope"_flags ''
		bobshell_var_append  "$_bobshell_cli_setup__scope"_flags  " $*"
	else
		bobshell_die 'dev assertion failed'
	fi


	# shellcheck disable=SC2016
	bobshell_event_listen "$_bobshell_cli_setup__scope"_help_event '
printf %s "  "
_bobshell_cli_setup_help_event__separator=
for x in '"$*"'; do
	printf "%s" "$_bobshell_cli_setup_help_event__separator"
	_bobshell_cli_setup_help_event__separator=", "
	if [ 1 = ${#x} ]; then
		printf -- "-%s" "$x"
	else
		printf -- "--%s" "$x"
	fi
done
unset _bobshell_cli_setup_help_event__separator
if [ true = '"$_bobshell_cli_setup__param"' ]; then
	printf "%s" =VALUE 
fi
printf "\n"
'
	if bobshell_isset _bobshell_cli_setup__help; then
		bobshell_str_quote "$_bobshell_cli_setup__help"
		bobshell_event_listen "$_bobshell_cli_setup__scope"_help_event '
printf "    %s\n" '"$bobshell_result_1"
	fi


	if bobshell_isset _bobshell_cli_setup__arg_listener; then
		# shellcheck disable=SC2016
		bobshell_event_listen "$_bobshell_cli_setup__scope"_arg_event '
if bobshell_equals_any "$1" '"$*"'; then
	'"$_bobshell_cli_setup__arg_listener"'
fi'

	elif bobshell_isset _bobshell_cli_setup__var; then


		if bobshell_isset _bobshell_cli_setup__default_value; then
			bobshell_str_quote "$_bobshell_cli_setup__default_value"
			bobshell_event_listen "$_bobshell_cli_setup__scope"_start_event "$_bobshell_cli_setup__var=$bobshell_result_1"
		elif [ true = "$_bobshell_cli_setup__default_unset" ]; then
			bobshell_event_listen "$_bobshell_cli_setup__scope"_start_event "unset $_bobshell_cli_setup__var"
		elif [ true = "$_bobshell_cli_setup__flag" ]; then
			bobshell_event_listen "$_bobshell_cli_setup__scope"_start_event "$_bobshell_cli_setup__var=false"
		elif [ true = "$_bobshell_cli_setup__param" ]; then
			bobshell_event_listen "$_bobshell_cli_setup__scope"_start_event "unset $_bobshell_cli_setup__var"
		fi

		if [ true = "$_bobshell_cli_setup__param" ]; then
			if bobshell_isset _bobshell_cli_setup__flag_value; then
				bobshell_die "bobshell_cli_setup: --param and --flag-value"
			fi

			if [ true = "$_bobshell_cli_setup__append" ]; then
				bobshell_str_quote "$_bobshell_cli_setup__separator"
				bobshell_result_read _bobshell_cli_setup__quoted_separator

				# shellcheck disable=SC2016
				bobshell_event_listen "$_bobshell_cli_setup__scope"_arg_event '
if bobshell_equals_any "$1" '"$*"'; then
	if [ -n "${'"$_bobshell_cli_setup__var"':-}" ]; then
		'"$_bobshell_cli_setup__var"'="${'"$_bobshell_cli_setup__var"':-}"'"$_bobshell_cli_setup__quoted_separator"'
	fi
	'"$_bobshell_cli_setup__var"'="${'"$_bobshell_cli_setup__var"':-}$2"
fi'
			else
				# shellcheck disable=SC2016
				bobshell_event_listen "$_bobshell_cli_setup__scope"_arg_event '
if bobshell_equals_any "$1" '"$*"'; then
	'"$_bobshell_cli_setup__var"'="$2"
fi'				
				unset _bobshell_cli_setup__quoted_separator
			fi
			unset _bobshell_cli_setup__param_value

		elif [ true = "$_bobshell_cli_setup__flag" ]; then
			if bobshell_isset _bobshell_cli_setup__flag_value; then
				_bobshell_cli_setup__actual_flag_value="$_bobshell_cli_setup__flag_value"
			else
				_bobshell_cli_setup__actual_flag_value=true
			fi

			bobshell_str_quote "$_bobshell_cli_setup__actual_flag_value"
			bobshell_result_read _bobshell_cli_setup__quoted_actual_flag_value

			if [ true = "$_bobshell_cli_setup__append" ]; then
				bobshell_str_quote "$_bobshell_cli_setup__separator"
				bobshell_result_read _bobshell_cli_setup__quoted_separator


				# shellcheck disable=SC2016
				bobshell_event_listen "$_bobshell_cli_setup__scope"_arg_event '
if bobshell_equals_any "$1" '"$*"'; then
	if [ -n "${'"$_bobshell_cli_setup__var"':-}" ]; then
		'"$_bobshell_cli_setup__var"'="${'"$_bobshell_cli_setup__var"':-}"'"$_bobshell_cli_setup__quoted_separator"'
	fi
	'"$_bobshell_cli_setup__var"'="${'"$_bobshell_cli_setup__var"'}"'"$_bobshell_cli_setup__quoted_actual_flag_value"'
fi'
				unset _bobshell_cli_setup__quoted_separator
			else
				bobshell_str_quote "$_bobshell_cli_setup__actual_flag_value$_bobshell_cli_setup__separator"
				# shellcheck disable=SC2016
				bobshell_event_listen "$_bobshell_cli_setup__scope"_arg_event '
if bobshell_equals_any "$1" '"$*"'; then
	'"$_bobshell_cli_setup__var"'="'"$bobshell_result_1"'"
fi'
			fi
			unset _bobshell_cli_setup__actual_flag_value _bobshell_cli_setup__quoted_actual_flag_value
		else
			bobshell_die "dev assertion faled"
		fi
		bobshell_event_listen "${_bobshell_cli_setup__scope}_clear" "unset $_bobshell_cli_setup__var" 
	else
		bobshell_die "bobshell_cli_setup: both --listener and --var forbidden"
	fi

	# CLEAR
	unset _bobshell_cli_setup__scope
	bobshell_event_fire bobshell_cli_setup_clear_event

}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/check.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../event/fire.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../misc/equals_any.sh

# disable recursive dependency resolution when building shelduck itself
# shelduck import ./help.sh

# fun: bobshell_cli_parse SCOPE [args...]
# use: bobshell_cli_parse hoid_task_user_cli "$@"
#      bobshell_array_call bobshell_result set --
bobshell_cli_parse() {
	bobshell_cli_shift=0
	_bobshell_cli_parse__scope="$1"
	shift

	bobshell_var_get "$_bobshell_cli_parse__scope"_params
	if ! bobshell_result_check _bobshell_cli_parse__params; then
		_bobshell_cli_parse__params=
	fi

	bobshell_var_get "$_bobshell_cli_parse__scope"_flags
	if ! bobshell_result_check _bobshell_cli_parse__flags; then
		_bobshell_cli_parse__flags=
	fi



	bobshell_event_fire "${_bobshell_cli_parse__scope}_start_event"

	while bobshell_isset_1 "$@"; do
		# -- end of named options, start of positional arguments
		if [ "$1" = -- ]; then
			bobshell_cli_shift=$(( bobshell_cli_shift + 1 ))
			shift
			break
		fi

		# obvious error
		if [ "$1" = - ]; then
			bobshell_cli_parse__error "unexpected argument: $1"
		fi
		
		# 
		if bobshell_remove_prefix "$1" -- _bobshell_cli_parse__x; then
			if bobshell_split_first "$_bobshell_cli_parse__x" '=' _bobshell_cli_parse__name _bobshell_cli_parse__value; then
				# shellcheck disable=SC2086
				if ! bobshell_equals_any "$_bobshell_cli_parse__name" $_bobshell_cli_parse__params; then
					bobshell_cli_parse__error "unknown param: --$_bobshell_cli_parse__name"
				fi
				bobshell_event_fire "$_bobshell_cli_parse__scope"_arg_event "$_bobshell_cli_parse__name" "$_bobshell_cli_parse__value"
				bobshell_cli_shift=$(( bobshell_cli_shift + 1 ))
				shift
				unset _bobshell_cli_parse__name _bobshell_cli_parse__value
			else
				# shellcheck disable=SC2086
				if bobshell_equals_any "$_bobshell_cli_parse__x" $_bobshell_cli_parse__params; then
					if ! bobshell_isset_2 "$@"; then
						bobshell_cli_parse__error "param argument expected: $1"
					fi
					bobshell_event_fire "$_bobshell_cli_parse__scope"_arg_event "$_bobshell_cli_parse__x" "$2"
					bobshell_cli_shift=$(( bobshell_cli_shift + 2 ))
					shift 2
				elif bobshell_equals_any "$_bobshell_cli_parse__x" $_bobshell_cli_parse__flags; then
					bobshell_event_fire "$_bobshell_cli_parse__scope"_arg_event "$_bobshell_cli_parse__x"
					bobshell_cli_shift=$(( bobshell_cli_shift + 1 ))
					shift
				else
					bobshell_cli_parse__error "unknown arg: $1"
				fi
			fi
			unset _bobshell_cli_parse__x
		elif bobshell_remove_prefix "$1" - _bobshell_cli_parse__x; then
			while [ -n "$_bobshell_cli_parse__x" ]; do
				_bobshell_cli_parse__rest="${_bobshell_cli_parse__x#?}"
				_bobshell_cli_parse__arg="${_bobshell_cli_parse__x%"$_bobshell_cli_parse__rest"}"
				# shellcheck disable=SC2086
				if bobshell_equals_any "$_bobshell_cli_parse__arg" $_bobshell_cli_parse__params; then
					if [ -n "$_bobshell_cli_parse__rest" ]; then
						bobshell_event_fire "${_bobshell_cli_parse__scope}_arg_event" "$_bobshell_cli_parse__arg" "$_bobshell_cli_parse__rest"
						bobshell_cli_shift=$(( bobshell_cli_shift + 1 ))
						shift
						break
					elif bobshell_isset_2 "$@"; then
						if ! bobshell_isset_2 "$@"; then
							bobshell_cli_parse__error "param argument expected: $1"
						fi
						bobshell_event_fire "${_bobshell_cli_parse__scope}_arg_event" "$_bobshell_cli_parse__arg" "$2"
						bobshell_cli_shift=$(( bobshell_cli_shift + 2 ))
						shift 2
						break
					else
						bobshell_cli_parse__error "unknown argument: -$_bobshell_cli_parse__arg"
					fi
				elif bobshell_equals_any "$_bobshell_cli_parse__arg" $_bobshell_cli_parse__flags; then
					bobshell_event_fire "${_bobshell_cli_parse__scope}_arg_event" "$_bobshell_cli_parse__arg"
					if [ -z "$_bobshell_cli_parse__rest" ]; then
						bobshell_cli_shift=$(( bobshell_cli_shift + 1 ))
						shift
					fi
				else
					bobshell_cli_parse__error "unknown argument: -$_bobshell_cli_parse__arg"
				fi
				_bobshell_cli_parse__x="$_bobshell_cli_parse__rest"
			done
			unset _bobshell_cli_parse__x
		else
			break
		fi
	done
	unset _bobshell_cli_parse__scope _bobshell_cli_parse__params _bobshell_cli_parse__flags

	bobshell_result_set true "$@"
}

bobshell_cli_parse__error() {
	_bobshell_cli_parse__error__message=$(bobshell_cli_help "$_bobshell_cli_parse__scope")
	_bobshell_cli_parse__error__message="bobshell_cli_parse $_bobshell_cli_parse__scope: $*

$_bobshell_cli_parse__error__message"
	bobshell_die "$_bobshell_cli_parse__error__message"
}










bobshell_cli_help() {
	printf '%s\n' "Usage: bobshell_cli_parse $1 [OPTIONS] ARGS

Options:"
	bobshell_event_fire "$1"_help_event

}







# disable recursive dependency resolution when building shelduck itself
# shelduck import ../var/get.sh

# bobshell_map_get mapname key 
bobshell_map_get() {
	_bobshell_map_get__hash=$(printf %s "$2" | sed 's/[^A-Za-z_0-9]/_/g') # todo optimize somehow

	bobshell_var_get "${1}_bag_$_bobshell_map_get__hash"
	if ! bobshell_result_check _bobshell_map_get__bag; then
		unset _bobshell_map_get__hash
		bobshell_result_set false
		return
	fi

	for _bobshell_map_get__ref in $_bobshell_map_get__bag; do
		bobshell_var_get "${1}_key_$_bobshell_map_get__ref"
		bobshell_result_check _bobshell_map_get__key

		if [ "$2" = "$_bobshell_map_get__key" ]; then
			unset _bobshell_map_get__hash _bobshell_map_get__bag

			bobshell_var_get "${1}_val_$_bobshell_map_get__ref"
			unset _bobshell_map_get__ref
			bobshell_result_check _bobshell_map_get__value

			bobshell_result_set true "$_bobshell_map_get__value"
			unset _bobshell_map_get__value
			return
		fi
		unset _bobshell_map_get__key
	done

	unset _bobshell_map_get__hash _bobshell_map_get__bag
	bobshell_result_set false
}






# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/check.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../var/get.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../var/set.sh

# bobshell_map_put mapname key value 
bobshell_map_put() {
	_bobshell_map_put__hash=$(printf %s "$2" | sed 's/[^A-Za-z_0-9]/_/g') # todo optimize somehow

	bobshell_var_get "${1}_bag_$_bobshell_map_put__hash"
	if bobshell_result_check _bobshell_map_put__bag; then
		for _bobshell_map_put__ref in $_bobshell_map_put__bag; do
			bobshell_var_get "${1}_key_$_bobshell_map_put__ref"
			bobshell_result_check _bobshell_map_put__key
			if [ "$_bobshell_map_put__key" = "$2" ]; then
				bobshell_var_set "${1}_val_$_bobshell_map_put__ref" "$3"
				unset _bobshell_map_put__hash _bobshell_map_put__bag _bobshell_map_put__ref _bobshell_map_put__key
				return
			fi
		done
		: "${_bobshell_map__counter:=0}"
		_bobshell_map__counter=$(( 1 + _bobshell_map__counter ))
		_bobshell_map_put__ref="$_bobshell_map__counter"
		_bobshell_map_put__bag="$_bobshell_map_put__bag $_bobshell_map_put__ref"
		unset _bobshell_map_put__refs _bobshell_map_put__ref _bobshell_map_put__key
	else
		: "${_bobshell_map__counter:=0}"
		_bobshell_map__counter=$(( 1 + _bobshell_map__counter ))
		_bobshell_map_put__ref="$_bobshell_map__counter"
		_bobshell_map_put__bag="$_bobshell_map_put__ref"
	fi

	bobshell_var_set "${1}_bag_$_bobshell_map_put__hash" "$_bobshell_map_put__bag"
	unset _bobshell_map_put__hash _bobshell_map_put__bag

	bobshell_var_set "${1}_key_$_bobshell_map_put__ref" "$2"
	bobshell_var_set "${1}_val_$_bobshell_map_put__ref" "$3"
	unset _bobshell_map_put__ref
}








# disable recursive dependency resolution when building shelduck itself
# shelduck import ../base.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/set.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../result/check.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../map/get.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../map/put.sh

# disable recursive dependency resolution when building shelduck itself
# shelduck import ../cli/parse.sh
# disable recursive dependency resolution when building shelduck itself
# shelduck import ../cli/setup.sh


bobshell_cli_setup bobshell_cache_get_cli --param --var=_bobshell_cache_get__ttl --default-value=none  t ttl

# fun: bobshell_shift_exec SHIFTNUM IGNORED ... COMMAND [ARGS...]
bobshell_shift_exec() {
	shift "$1"
	shift
	"$@"
}

# fun: bobshell_cache_get KEY LOADERCMD [ARGS ...]
bobshell_cache_get() {
	bobshell_cli_parse bobshell_cache_get_cli "$@"
	shift "$bobshell_cli_shift"

	_bobshell_cache_get__key="$1"
	shift

	bobshell_map_get bobshell_cache_data "$_bobshell_cache_get__key"
	if bobshell_result_check _bobshell_cache_get__value; then
		bobshell_map_get bobshell_cache_deadline "$_bobshell_cache_get__key"
		if ! bobshell_result_check _bobshell_cache_get__deadline || [ "$(date +%s)" -lt "$_bobshell_cache_get__deadline" ]; then
			bobshell_result_set "$_bobshell_cache_get__value"
			unset _bobshell_cache_get__key _bobshell_cache_get__value _bobshell_cache_get__deadline
			return
		fi
	fi

	set "$_bobshell_cache_get__key" "$_bobshell_cache_get__ttl" "$@" # save local state before recursive call
	bobshell_shift_exec 2 "$@"
	bobshell_result_read _bobshell_cache_get__value
	_bobshell_cache_get__key="$1"
	_bobshell_cache_get__ttl="$2"
	bobshell_map_put bobshell_cache_data "$_bobshell_cache_get__key" "$_bobshell_cache_get__value"

	if [ none != "$_bobshell_cache_get__ttl" ]; then
		_bobshell_cache_get__deadline=$(date +%s)
		_bobshell_cache_get__deadline=$(( _bobshell_cache_get__deadline + _bobshell_cache_get__ttl ))
		unset _bobshell_cache_get__ttl
		bobshell_map_put bobshell_cache_deadline "$_bobshell_cache_get__key" "$_bobshell_cache_get__deadline"
	fi
	unset _bobshell_cache_get__deadline _bobshell_cache_get__key

	bobshell_result_set "$_bobshell_cache_get__value"
	unset _bobshell_cache_get__value
}
























# see https://github.com/ajdiaz/bashdoc


# fun: shelduck CLIARGS...
# api: public
# env: SHELDUCK_BASE_URL
#      SHELDUCK_LIBRARY_PATH
#      SHELDUCK_URL_RULES
shelduck() {
	bobshell_require_not_empty "${1:-}" 'shelduck: subcommad expected, see shelduck usage'
	case "$1" in
		(usage|import|resolve|run)
				_shelduck__subcommand="$1"
				shift
				"shelduck_$_shelduck__subcommand" "$@"
				unset _shelduck__subcommand
				;;
		(*) printf 'unknown subcommand %s, see shelduck usage' "$1"
	esac
}

# api: private
shelduck_ensure_base_url() {
	# guess base url
	if [ -z "${shelduck_base_url:-}" ]; then
		if [ -n "${SHELDUCK_BASE_URL:-}" ]; then
			shelduck_base_url="$SHELDUCK_BASE_URL"
		else
			shelduck_base_url=$(pwd)
			shelduck_base_url="file://$shelduck_base_url"
		fi
	fi
}



# fun: shelduck_run URL [ARGS...]
# api: private
shelduck_run() {
	# parse cli
	bobshell_isset_1 "$@" || bobshell_die '"shelduck run" requires at least 1 argument'
	shelduck_run_url=$(shelduck_fix_url "$1")
	shift
	shelduck_run_args="$(bobshell_quote "$@")"


	# save vars before recursive_call
	set -- "$shelduck_run_args" # save latest run args, since recursive imports use it # todo needed?
	
	# delegate to shelduck_exec
	shelduck_exec '' "$shelduck_run_url" "$shelduck_run_args"
	unset shelduck_run_url shelduck_run_args

	# restore state after recursive call
	shelduck_run_args="$1"

}


shelduck_fix_url() {
	if [ -z "$1" ]; then
		bobshell_die "shelduck: invalid url"
	fi

	shelduck_ensure_base_url
	if bobshell_locator_is_remote "$1" || bobshell_locator_is_file "$1" || ! bobshell_locator_parse "$1"; then
		shelduck_fix_url=$(bobshell_resolve_url "$1" "$shelduck_base_url")
		if [ -n "${SHELDUCK_URL_RULES:-}" ]; then
			shelduck_fix_url=$(shelduck_apply_rules "$shelduck_fix_url" "$SHELDUCK_URL_RULES")
		fi
		printf %s "$shelduck_fix_url"
		unset shelduck_fix_url
	else
		printf %s "$1"
	fi
}



shelduck_parse_import_cli() {
	bobshell_require_not_empty "${1:-}" '"shelduck import" requires at least 1 argument.'
	shelduck_import_aliases=
	shelduck_import_url=
	while bobshell_isset_1 "$@"; do
		case "$1" in
			(-a|--alias)
				if ! bobshell_isset_2 "$@"; then
					bobshell_die "option '$1' (alias) requires argument"
				fi
				shift
				shelduck_import_cli_alias "$1"
				shift
				;;

			(--alias=*)
				bobshell_remove_prefix "$1" --alias= shelduck_analyze_cli_alias
				shift
				shelduck_import_cli_alias "$shelduck_analyze_cli_alias"
				;;

			(*)
				break
				;;
		esac
	done

	if [ -z "${1:-}" ]; then
		bobshell_die "url expected to be nonempty"
	fi
	shelduck_import_url="$1"
	
	if bobshell_isset_2 "$@"; then
		bobshell_die "unexpected argument \"$2\""
	fi
	
}


shelduck_import_cli_alias() {
	if [ -z "$1" ]; then
		bobshell_die 'alias cannot be empty'
	fi
	shelduck_import_aliases="$shelduck_import_aliases $1"
}

shelduck_import_usage() {
	printf %s 'Import library.
	
Usage: shelduck import [OPTIONS] URL

Options:

   -a, --alias ALIAS    Defina alias for functions      
'
}





# fun: shelduck_apply_rules VALUE RULES
shelduck_apply_rules() {
	shelduck_apply_rules_result="$1"
	shelduck_apply_rules_rules="${2:-}"

	while [ -n "$shelduck_apply_rules_rules" ]; do
		if ! bobshell_split_first "$shelduck_apply_rules_rules" ',' shelduck_apply_rules_rule shelduck_apply_rules_rules; then
			shelduck_apply_rules_rule="$shelduck_apply_rules_rules"
			shelduck_apply_rules_rules=
		fi
		
		shelduck_apply_rules_key=
		shelduck_apply_rules_value=
		bobshell_split_first "$shelduck_apply_rules_rule" = shelduck_apply_rules_key shelduck_apply_rules_value
		shelduck_apply_rules_result=$(bobshell_replace "$shelduck_apply_rules_result" "$shelduck_apply_rules_key" "$shelduck_apply_rules_value")
	done
	printf %s "$shelduck_apply_rules_result"

	unset shelduck_apply_rules_result
	unset shelduck_apply_rules_rules shelduck_apply_rules_rule
	unset shelduck_apply_rules_key shelduck_apply_rules_value
}




# shelduck_run and shelduck_import are very similar, but:
# - import requires url, since it checks for duplicates, whereas run does not requies url
# - import checks for duplicate urls, run not
# - import takes args from run_args
# - run takes args from command, and restores


# fun: shelduck_resolve CLIARGS...
# api: private
# env: shelduck_base_url
shelduck_import() {
	shelduck_parse_import_cli "$@"
	shelduck_import_url=$(shelduck_fix_url "$shelduck_import_url")

	# check for duplicates
	: "${shelduck_import_history:=}"
	if bobshell_contains "$shelduck_import_history" "[$shelduck_import_url]"; then
		# todo maybe base url is needed
		shelduck_print_origin "$shelduck_import_url"
		bobshell_result_read shelduck_import_origin
		shelduck_import_addition=$(shelduck_print_addition "$shelduck_import_origin" "$shelduck_import_url" "$shelduck_import_aliases")
		eval "$shelduck_import_addition"
		unset shelduck_import_origin shelduck_import_addition
		return
	fi
	shelduck_import_history="$shelduck_import_history [$shelduck_import_url]"
	
	# delegate to shelduck_exec
	shelduck_exec "$shelduck_import_aliases" "$shelduck_import_url" ''
	unset shelduck_import_aliases shelduck_import_url shelduck_analyze_cli_args

}




# fun: shelduck_exec ALIASES ABSURL ARGS
shelduck_exec() {
	shelduck_ensure_base_url


	# exec absurl ABSURL
	if [ -n "$2" ]; then
		shelduck_alias_strategy=wrap
		shelduck_print_origin "$2"
		bobshell_result_read shelduck_exec_origin
		shelduck_event_url "$2" "$shelduck_exec_origin"
		shelduck_exec_additions=$(shelduck_print_addition "$shelduck_exec_origin" "$2" "$1")

		# save state before recursive call
		set -- "$shelduck_base_url" "$1" "$2" "$3" shelduck_eval_with_args "$shelduck_exec_origin$shelduck_exec_additions"
		if [ -n "$4" ]; then
			eval "set -- \"\$@\" $4"
		fi
		
		# recursive call
		shelduck_update_base_url "$3"
		shelduck_shift_exec 4 "$@"

		# restore state after recursive call
		shelduck_base_url="$1"
		shift
	fi
	
}

# fun: shelduck_event_url URL TEXT
# txt: event listener to extend shelduck core
shelduck_event_url() {
	true
}

# fun: shelduck_shift_exec SHIFTNUM IGNORED ... COMMAND [ARGS...]
shelduck_shift_exec() {
	shift "$1"
	shift
	"$@"
}

# fun: shelduck_update_base_url URL
shelduck_update_base_url() {
	if bobshell_locator_is_file "$1" || bobshell_locator_is_remote "$1"; then
		shelduck_base_url=$(bobshell_base_url "$1")
	fi
}



# api: private
shelduck_usage() {
	printf 'Usage: shelduck SUBCOMMAND [ARGS...]\n'
	printf 'Commands:\n'
	printf '    usage\n'
	printf '    import\n'
	printf '    resolve\n'
	printf '    run\n'
}


# fun: shelduck_resolve CLIARGS...
# api: private
shelduck_resolve() {
	shelduck_ensure_base_url

	# set starting parameters
	shelduck_print_history=
	shelduck_alias_strategy="${SHELDUCK_ALIAS_STRATEGY:-wrap}"
	
	# delegate
	shelduck_print "$@"
}



# fun: shelduck_print CLIARGS...
# env: shelduck_print_history
#      shelduck_alias_strategy
# txt: parse cli and delegate to shelduck_print_tree
# api: private
shelduck_print() {

	shelduck_print_initial_base_url="$shelduck_base_url" # todo is shelduck_print_initial_base_url needed?

	# parse cli
	shelduck_parse_import_cli "$@"
	shelduck_print_url=$(shelduck_fix_url "$shelduck_import_url")
	unset shelduck_import_url
	shelduck_print_aliases="$shelduck_import_aliases"
	unset shelduck_import_aliases


	# load script
	shelduck_print_origin "$shelduck_print_url"
	bobshell_result_read shelduck_print_script
	shelduck_event_url "$shelduck_print_url" "$shelduck_print_script"
	
	# save variables to local array before subsequent (possibly recursive) calls
	set -- "$shelduck_print_script" "$shelduck_print_url" "$shelduck_print_aliases" "$shelduck_base_url" "$shelduck_print_initial_base_url"

	# check if dependency was already compiled
	if ! bobshell_contains "$shelduck_print_history" "[$2]"; then
		shelduck_print_history="$shelduck_print_history [$2]"

		shelduck_update_base_url "$shelduck_print_url"

		# recursive call
		#shelduck_print_compile_args=$(bobshell_quote "$@")
		shelduck_compile "$@"

		# restore variables from local array after recursive call
		shelduck_base_url="$4"
		shelduck_print_initial_base_url="$5"

	fi

	# print additions, if needed
	shelduck_print_addition "$@"

	shelduck_base_url="$shelduck_print_initial_base_url"
}




# fun: shelduck_compile SCRIPT URL
# txt: print recusively expanded shelduck commands, and print rewritten rest of script
# api: private
shelduck_compile() {
	shelduck_compile_input="$1"
	shift
	if bobshell_starts_with "$shelduck_compile_input" "$bobshell_newline"; then
		if bobshell_starts_with "$1" file:// https:// http:// stdin:; then
			printf '%s\n' "# shelduck: source for $1"
		fi
	fi

	shelduck_compile_before=
	shelduck_compile_after=
	while true; do
		if bobshell_remove_prefix "$shelduck_compile_input" 'shelduck import ' shelduck_compile_after; then
			shelduck_compile_input="$shelduck_compile_after"
		elif ! bobshell_split_first "$shelduck_compile_input" "${bobshell_newline}shelduck import " shelduck_compile_before shelduck_compile_after; then
			break
		else
			# print everything before the first found shelduck command
			shelduck_rewrite "$shelduck_compile_before$bobshell_newline" "$@"
			shelduck_compile_input="$shelduck_compile_after$bobshell_newline"
		fi

		

		shelduck_compile_command=
		while true; do
			if ! bobshell_split_first "$shelduck_compile_input" "${bobshell_newline}" shelduck_compile_before shelduck_compile_after; then
				shelduck_compile_command="$shelduck_compile_input"
				shelduck_compile_input=
				break
			fi

			if ! bobshell_remove_suffix "$shelduck_compile_before" '\' shelduck_compile_before; then
				shelduck_compile_command="$shelduck_compile_command$shelduck_compile_before"
				shelduck_compile_input="$bobshell_newline$shelduck_compile_after"
				break;
			fi
			
			shelduck_compile_command="$shelduck_compile_command${shelduck_compile_before}"
			shelduck_compile_input="$shelduck_compile_after"
		done
		
		# assert shelduck argument command line not empty
		if [ -z "$shelduck_compile_command" ]; then
			bobshell_die 'empty shelduck arguments'
		fi

		# before recursive call, save variables to local array
		set -- "$shelduck_compile_input" "$@"

		# recursive call, concously not double qouting
		# shellcheck disable=SC2086
		shelduck_print $shelduck_compile_command

		# after recursive call, restore variables from local array
		shelduck_compile_input="$1"
		shift
	done
				

	# print everything after last found shelduck command
	shelduck_rewrite "$shelduck_compile_input" "$@"
}





# fun: shelduck_print_origin ABSURL
# txt: prints original script without modification
# api: private
shelduck_print_origin() {
	bobshell_result_set false
	bobshell_event_fire shelduck_fetch_url_event "$1"
	if bobshell_result_check; then
		bobshell_result_set "$bobshell_result_2"
		return
	fi
	shelduck_cached_fetch_url "$1"
}




# fun: shelduck_rewrite ORIGCONTENT URL
# txt: rewrite original script (e.g. rename functions)
# api: private
shelduck_rewrite() {
	if [ rename = "${shelduck_alias_strategy:-}" ]; then
		bobshell_die "shelduck_alias_strategy: value $shelduck_alias_strategy not supported"
	fi
	shelduck_rewrite_data="$1"
	if bobshell_remove_prefix "$shelduck_rewrite_data" "#!/usr/bin/env shelduck_run$bobshell_newline" shelduck_rewrite_suffix; then
		shelduck_rewrite_data="#!/bin/sh$bobshell_newline$shelduck_rewrite_suffix"
	fi
	printf %s "$shelduck_rewrite_data"
	unset shelduck_rewrite_data shelduck_rewrite_suffix
}




# fun: shelduck_print_addition ORIGCONTENT ABSURL ALIASES
# txt: print script additional code (e.g. aliases)
# api: private
shelduck_print_addition() {

	if [ wrap != "${shelduck_alias_strategy:-}" ]; then
		# nothing to do, wrap was the only supported customization
		return
	fi

	# analyze functions (for aliases)
	regex='^ *([A-Za-z0-9_]+) *\( *\) *\{ *$' # match shell function declaration '  function_name  (   )  {  '
	shelduck_print_addition_function_names="$(printf %s "$1" | sed --silent --regexp-extended "s/$regex/\1/p")"
	unset regex
	# todo detect function name collizion and print warning if so
	

	# analyze aliases
	for arg in $3; do
		# todo assert $arg not empty
		if ! bobshell_split_first "$arg" = key value; then
			key="$arg"
			value="$arg"
		fi
		bobshell_require_not_empty "$key"   line "$arg": key   expected not to be empty
		bobshell_require_not_empty "$value" line "$arg": value expected not to be empty
		
		shelduck_print_script_function_name="$(printf %s "$shelduck_print_addition_function_names" | grep -E "^.*$value\$" || true)"
		if [ -n "$shelduck_print_script_function_name" ] && [ "$key" != "$shelduck_print_script_function_name" ]; then
			printf '\n\n'
			printf '\n # shelduck: alias for %s (from %s)' "$shelduck_print_script_function_name" "$2" 
			printf '\n%s() {' "$key"
			printf '\n	%s "$@"' "$shelduck_print_script_function_name"
			printf '\n}'
			printf '\n'
		fi
		unset key value shelduck_print_script_function_name
	done
	unset shelduck_print_addition_function_names
}



# fun: shelduck_cached_fetch_url ABSURL
# txt: download dependency given url and save to cache
# api: private
shelduck_cached_fetch_url() {
	# bypass cache if local file
	if bobshell_locator_is_file "$1" shelduck_cached_fetch_url_path; then
		bobshell_cache_get --ttl=60 "shelduck_cached_fetch_url/$1" shelduck_cached_fetch_file "$shelduck_cached_fetch_url_path"
		unset shelduck_cached_fetch_url_path
	elif bobshell_locator_is_remote "$1"; then
		bobshell_cache_get --ttl=60 "shelduck_cached_fetch_url/$1" shelduck_cached_fetch_remote "$1"
	else
		bobshell_resource_copy "$1" var:_shelduck_cached_fetch_url
		bobshell_result_set "$_shelduck_cached_fetch_url"
		unset _shelduck_cached_fetch_url
	fi
}

# fun: shelduck_cached_fetch_file FILEPATH
shelduck_cached_fetch_file() {
	if ! [ -f "$1" ]; then
		bobshell_die "shelduck: fetch error '$1': file '$1' not found"
	fi
	bobshell_resource_copy_file_to_var "$1" _shelduck_cached_fetch_file
	bobshell_result_set "$_shelduck_cached_fetch_file"
	unset _shelduck_cached_fetch_file
}

# fun: shelduck_cached_fetch_remote FILEPATH
shelduck_cached_fetch_remote() {
	# init bobshell_install_* library
	: "${SHELDUCK_INSTALL_NAME:=shelduck}"
	bobshell_scope_mirror SHELDUCK_INSTALL_ BOBSHELL_INSTALL_
	bobshell_install_init

	# key
	shelduck_cached_fetch_url_key=$(printf %s "$1" | sed 's/[\/<>:\\|?*]/-/g')


	shelduck_cached_fetch_url_path=
	if shelduck_cached_fetch_url_path=$(bobshell_install_find_cache "$shelduck_cached_fetch_url_key"); then
		bobshell_file_date --format %s "$shelduck_cached_fetch_url_path"
		if bobshell_result_check _shelduck_cached_fetch_url__timestamp; then
			_shelduck_cached_fetch_url__timestamp=$(( _shelduck_cached_fetch_url__timestamp + ${SHELDUCK_CACHE_TIMEOUT:-86400} ))
			_shelduck_cached_fetch_url__now=$(date '+%s')
			
			if [ "$_shelduck_cached_fetch_url__now" -lt "$_shelduck_cached_fetch_url__timestamp" ]; then
				bobshell_resource_copy_file_to_var "$shelduck_cached_fetch_url_path" _shelduck_cached_fetch_remote__data
				bobshell_result_set "$_shelduck_cached_fetch_remote__data"
				unset shelduck_cached_fetch_url_path _shelduck_cached_fetch_url__timestamp _shelduck_cached_fetch_url__now _shelduck_cached_fetch_remote__data
				return
			fi
			unset _shelduck_cached_fetch_url__timestamp _shelduck_cached_fetch_url__now
		fi
		unset shelduck_cached_fetch_url_path
	fi
	
	shelduck_cached_fetch_url_result=$(bobshell_fetch_url "$1" || bobshell_die "shelduck: fetch error '$1': error downloading '$1'")

	bobshell_install_put_cache var:shelduck_cached_fetch_url_result "$shelduck_cached_fetch_url_key"
	bobshell_result_set "$shelduck_cached_fetch_url_result"
}


