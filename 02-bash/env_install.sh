#!/usr/bin/env bash
#
# env_install.sh - set up a minimal Python development environment.
#
# Steps: detect the OS, make sure python3 and pip are installed, install
# Jupyter Notebook, and on macOS run `brew doctor`.
#
# Usage: ./env_install.sh [--dry-run] [--verbose] [--quiet] [--uninstall] [--help]

# Strict mode: stop on the first error, on unset variables and on pipeline failures
set -euo pipefail

# ---------------------------------------------------------------------------
# Settings (can be changed with command-line flags)
# ---------------------------------------------------------------------------
DRY_RUN=false
VERBOSE=false
QUIET=false
UNINSTALL=false
LOG_FILE="$(dirname "$0")/env_install.log"

# ANSI colors used by the print functions
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

# Write a timestamped line to the log file (audit trail for debugging)
log() {
    printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

# Feature 1: pretty print a message with a blank line before and after it
pretty_print() {
    local message="$1"
    local color="${2:-$GREEN}"
    if [ "$QUIET" = false ]; then
        printf "\n${color}%s${RESET}\n\n" "$message"
    fi
    log "INFO: $message"
}

warn() {
    printf "\n${YELLOW}WARNING: %s${RESET}\n\n" "$1"
    log "WARNING: $1"
}

error() {
    printf "\n${RED}ERROR: %s${RESET}\n\n" "$1" >&2
    log "ERROR: $1"
}

# Print extra details only when --verbose is set
debug() {
    if [ "$VERBOSE" = true ]; then
        printf "  -> %s\n" "$1"
    fi
}

# Run a command, or only show it in dry-run mode. Logs success or failure.
run() {
    log "RUN: $*"
    if [ "$DRY_RUN" = true ]; then
        printf "  [dry-run] %s\n" "$*"
        return 0
    fi
    debug "running: $*"
    if "$@"; then
        log "OK: $*"
    else
        local status=$?
        log "FAILED ($status): $*"
        error "Command failed: $*"
        return "$status"
    fi
}

usage() {
    cat <<EOF
Usage: $0 [options]

  --dry-run     show what would be done without changing anything
  --verbose     print more details
  --quiet       print only warnings and errors
  --uninstall   remove what this script installed (Jupyter Notebook)
  --help        show this help
EOF
}

parse_args() {
    for arg in "$@"; do
        case "$arg" in
            --dry-run)   DRY_RUN=true ;;
            --verbose)   VERBOSE=true ;;
            --quiet)     QUIET=true ;;
            --uninstall) UNINSTALL=true ;;
            --help|-h)   usage; exit 0 ;;
            *)           error "Unknown option: $arg"; usage; exit 1 ;;
        esac
    done
}

# Feature 2: detect the operating system using the OSTYPE variable
detect_os() {
    case "${OSTYPE:-unknown}" in
        darwin*)            OS="macos" ;;
        linux-gnu*|linux*)  OS="linux" ;;
        msys*|cygwin*)      OS="windows" ;;
        *)                  OS="unknown" ;;
    esac
    pretty_print "Detected operating system: $OS (OSTYPE=${OSTYPE:-unset})"
}

# Install a package with the right package manager for the current OS
install_package() {
    local package="$1"
    case "$OS" in
        macos)
            if ! command -v brew >/dev/null 2>&1; then
                error "Homebrew is required on macOS: https://brew.sh"
                exit 1
            fi
            run brew install "$package"
            ;;
        linux)
            run sudo apt-get update
            run sudo apt-get install -y "$package"
            ;;
        *)
            error "Automatic installation is not supported on '$OS'. Please install $package manually."
            exit 1
            ;;
    esac
}

# Feature 3: install python3 if missing, otherwise show its version
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        pretty_print "Python is installed: $(python3 --version 2>&1)"
    else
        warn "python3 not found, installing it..."
        if [ "$OS" = "macos" ]; then
            install_package python
        else
            install_package python3
        fi
    fi
}

# Feature 4: make sure pip is available and show its version
check_pip() {
    if python3 -m pip --version >/dev/null 2>&1; then
        pretty_print "pip version: $(python3 -m pip --version)"
    else
        warn "pip not found, installing it..."
        if [ "$OS" = "linux" ]; then
            install_package python3-pip
        else
            run python3 -m ensurepip --upgrade
        fi
    fi
}

# Feature 5: install Jupyter Notebook (the command depends on the OS)
install_jupyter() {
    pretty_print "Installing Jupyter Notebook..."
    case "$OS" in
        macos) install_package jupyterlab ;;   # Homebrew ships notebook with jupyterlab
        *)     run python3 -m pip install --user notebook ;;
    esac
    pretty_print "Jupyter Notebook installed. Start it with: jupyter notebook"
}

# Feature 6: on macOS, check that Homebrew is healthy
brew_health_check() {
    if [ "$OS" = "macos" ]; then
        pretty_print "Running brew doctor..."
        # brew doctor returns a non-zero code for simple warnings: do not stop the script
        if ! run brew doctor; then
            warn "brew doctor reported some issues, see the output above."
        fi
    fi
}

# Bonus: undo what this script installed
uninstall() {
    pretty_print "Uninstalling Jupyter Notebook..."
    case "$OS" in
        macos) run brew uninstall jupyterlab ;;
        *)     run python3 -m pip uninstall -y notebook ;;
    esac
    pretty_print "Uninstall complete."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"
    log "===== env_install.sh started (dry-run=$DRY_RUN) ====="
    pretty_print "Starting environment setup..."

    detect_os

    if [ "$UNINSTALL" = true ]; then
        uninstall
        exit 0
    fi

    check_python
    check_pip
    install_jupyter
    brew_health_check

    pretty_print "Environment setup complete! Log file: $LOG_FILE"
}

main "$@"
