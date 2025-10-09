#!/bin/bash

# Setup reboot cron job on Kubernetes nodes
# This script SSHs into each node and sets up a cron job to reboot at 4am UTC

set -euo pipefail

# Configuration
NODE_IPS=(
    "192.168.1.49"
    "192.168.1.6" 
    "192.168.1.12"
    "192.168.1.13"
)

SSH_USER="${SSH_USER:-noelwilson}"
SSH_PASSWORD=""
CRON_TIME="0 4 * * *"  # 4am UTC daily
LOG_FILE="/tmp/setup_reboot_cron.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${1}" | tee -a "$LOG_FILE"
}

log_info() {
    log "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    log "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

# Function to prompt for SSH password
prompt_ssh_password() {
    if [[ -z "$SSH_PASSWORD" ]]; then
        echo -n "Enter SSH password for user '$SSH_USER': "
        read -s SSH_PASSWORD
        echo
        if [[ -z "$SSH_PASSWORD" ]]; then
            log_error "Password cannot be empty"
            return 1
        fi
    fi
    return 0
}

# Function to test SSH connectivity
test_ssh_connection() {
    local ip="$1"
    log_info "Testing SSH connection to $ip..."
    
    if sshpass -p "$SSH_PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$ip" "echo 'SSH connection successful'" >/dev/null 2>&1; then
        log_info "SSH connection to $ip successful"
        return 0
    else
        log_error "SSH connection to $ip failed"
        return 1
    fi
}

# Function to setup cron job on a node
setup_cron_job() {
    local ip="$1"
    log_info "Setting up cron job on $ip..."
    
    # Create the cron job command
    local cron_command="sudo reboot"
    local cron_entry="$CRON_TIME $cron_command"
    
    # SSH into the node and setup cron job
    if sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USER@$ip" << EOF
        # Check if cron job already exists
        if crontab -l 2>/dev/null | grep -q "reboot"; then
            echo "Cron job for reboot already exists"
        else
            # Add the cron job
            (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
            echo "Cron job added successfully"
        fi
        
        # Verify the cron job was added
        echo "Current crontab:"
        crontab -l
EOF
    then
        log_info "Successfully set up cron job on $ip"
        return 0
    else
        log_error "Failed to set up cron job on $ip"
        return 1
    fi
}

# Function to validate environment
validate_environment() {
    log_info "Validating environment..."
    
    # Check if sshpass is available
    if ! command -v sshpass >/dev/null 2>&1; then
        log_error "sshpass command not found. Please install sshpass:"
        log_error "  macOS: brew install hudochenkov/sshpass/sshpass"
        log_error "  Ubuntu/Debian: sudo apt-get install sshpass"
        log_error "  CentOS/RHEL: sudo yum install sshpass"
        return 1
    fi
    
    # Check if crontab command is available
    if ! command -v crontab >/dev/null 2>&1; then
        log_error "crontab command not found"
        return 1
    fi
    
    log_info "Environment validation completed"
    return 0
}

# Function to display summary
display_summary() {
    local success_count=0
    local total_count=${#NODE_IPS[@]}
    
    log_info "=== Setup Summary ==="
    log_info "Total nodes: $total_count"
    
    for ip in "${NODE_IPS[@]}"; do
        if test_ssh_connection "$ip"; then
            ((success_count++))
        fi
    done
    
    log_info "Successful connections: $success_count/$total_count"
    
    if [[ $success_count -eq $total_count ]]; then
        log_info "All nodes are accessible!"
    else
        log_warn "Some nodes are not accessible. Please check network connectivity and SSH configuration."
    fi
}

# Main execution function
main() {
    log_info "Starting Kubernetes node reboot cron job setup..."
    log_info "Log file: $LOG_FILE"
    
    # Validate environment
    if ! validate_environment; then
        log_error "Environment validation failed. Exiting."
        exit 1
    fi
    
    # Prompt for SSH password
    if ! prompt_ssh_password; then
        log_error "Failed to get SSH password. Exiting."
        exit 1
    fi
    
    # Display configuration
    log_info "Configuration:"
    log_info "  SSH User: $SSH_USER"
    log_info "  SSH Auth: Password"
    log_info "  Cron Time: $CRON_TIME (4am UTC daily)"
    log_info "  Node IPs: ${NODE_IPS[*]}"
    
    # Process each node
    local success_count=0
    local total_count=${#NODE_IPS[@]}
    
    for ip in "${NODE_IPS[@]}"; do
        log_info "Processing node: $ip"
        
        if test_ssh_connection "$ip"; then
            if setup_cron_job "$ip"; then
                ((success_count++))
            fi
        fi
        
        log_info "---"
    done
    
    # Display final summary
    log_info "=== Final Results ==="
    log_info "Successfully configured: $success_count/$total_count nodes"
    
    if [[ $success_count -eq $total_count ]]; then
        log_info "All nodes have been successfully configured with reboot cron jobs!"
    else
        log_warn "Some nodes failed to configure. Check the log for details."
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Setup cron job to reboot Kubernetes nodes at 4am UTC daily.
Uses password authentication for SSH connections.

OPTIONS:
    -h, --help          Show this help message
    -u, --user USER     SSH user (default: noelwilson)
    -p, --password PASS SSH password (will prompt if not provided)
    -t, --test          Test SSH connections only
    -s, --summary       Show connection summary only

ENVIRONMENT VARIABLES:
    SSH_USER            SSH username (default: noelwilson)
    SSH_PASSWORD        SSH password (will prompt if not set)

EXAMPLES:
    $0                          # Run with defaults, prompt for password
    $0 -u admin -p mypassword   # Use custom user and password
    $0 --test                   # Test connections only
    $0 --summary                # Show summary only

REQUIREMENTS:
    - sshpass must be installed for password authentication
    - macOS: brew install hudochenkov/sshpass/sshpass
    - Ubuntu/Debian: sudo apt-get install sshpass
    - CentOS/RHEL: sudo yum install sshpass

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--user)
            SSH_USER="$2"
            shift 2
            ;;
        -p|--password)
            SSH_PASSWORD="$2"
            shift 2
            ;;
        -t|--test)
            validate_environment
            if prompt_ssh_password; then
                display_summary
            fi
            exit 0
            ;;
        -s|--summary)
            validate_environment
            if prompt_ssh_password; then
                display_summary
            fi
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
