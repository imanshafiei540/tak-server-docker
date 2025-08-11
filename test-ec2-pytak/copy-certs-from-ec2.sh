#!/bin/bash

# Copy TAK certificates from EC2 to local machine
# Usage: ./copy-certs-from-ec2.sh your-key.pem 10.212.2.206

set -e

# Color output functions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check arguments
if [ $# -ne 2 ]; then
    print_error "Usage: $0 <ssh-key.pem> <ec2-ip-address>"
    echo "Example: $0 my-key.pem 10.212.2.206"
    exit 1
fi

SSH_KEY="$1"
EC2_IP="$2"

print_info "TAK Certificate Copier for EC2"
echo "================================="
print_info "SSH Key: $SSH_KEY"
print_info "EC2 IP: $EC2_IP"
echo

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_error "SSH key file not found: $SSH_KEY"
    exit 1
fi

# Check SSH key permissions
if [ "$(stat -f %A "$SSH_KEY")" != "400" ] && [ "$(stat -f %A "$SSH_KEY")" != "600" ]; then
    print_warning "SSH key permissions should be 600 or 400"
    print_info "Fixing permissions..."
    chmod 600 "$SSH_KEY"
fi

# Create certs directory if it doesn't exist
mkdir -p certs

# Test connectivity first
print_info "Testing SSH connectivity to EC2..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@"$EC2_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
    print_success "SSH connectivity confirmed"
else
    print_error "Cannot connect to EC2 instance. Check:"
    echo "  - Security groups allow SSH (port 22)"
    echo "  - SSH key is correct"
    echo "  - EC2 instance is running"
    echo "  - IP address is correct"
    exit 1
fi

# Check if TAK server directory exists
print_info "Checking TAK server installation..."
if ssh -i "$SSH_KEY" ubuntu@"$EC2_IP" "[ -d ~/tak-server ]" 2>/dev/null; then
    print_success "TAK server directory found"
else
    print_error "TAK server directory not found on EC2"
    print_info "Make sure you've deployed TAK server first"
    exit 1
fi

# Check if certificates exist
print_info "Checking for certificates on EC2..."
CERTS_EXIST=$(ssh -i "$SSH_KEY" ubuntu@"$EC2_IP" "ls ~/tak-server/tak/certs/files/user1.* 2>/dev/null | wc -l" || echo "0")

if [ "$CERTS_EXIST" -lt 2 ]; then
    print_warning "User1 certificates not found. Creating them..."
    
    # Create user1 certificate
    ssh -i "$SSH_KEY" ubuntu@"$EC2_IP" "cd ~/tak-server && docker exec -it tak-server-tak-1 bash -c 'cd /opt/tak/certs && ./makeCert.sh client user1'" || {
        print_error "Failed to create certificates"
        exit 1
    }
    
    print_success "Certificates created successfully"
else
    print_success "Certificates found on EC2"
fi

# Copy certificates
print_info "Copying certificates from EC2..."

# Copy user1.pem
if scp -i "$SSH_KEY" ubuntu@"$EC2_IP":~/tak-server/tak/certs/files/user1.pem ./certs/ >/dev/null 2>&1; then
    print_success "user1.pem copied"
else
    print_error "Failed to copy user1.pem"
    exit 1
fi

# Copy user1.key
if scp -i "$SSH_KEY" ubuntu@"$EC2_IP":~/tak-server/tak/certs/files/user1.key ./certs/ >/dev/null 2>&1; then
    print_success "user1.key copied"
else
    print_error "Failed to copy user1.key"
    exit 1
fi

# Copy ca.pem
if scp -i "$SSH_KEY" ubuntu@"$EC2_IP":~/tak-server/tak/certs/files/ca.pem ./certs/ >/dev/null 2>&1; then
    print_success "ca.pem copied"
else
    print_error "Failed to copy ca.pem"
    exit 1
fi

# Set proper permissions
chmod 644 certs/*.pem
chmod 600 certs/*.key

print_success "Certificate permissions set"

# Verify certificates
print_info "Verifying certificates..."
if openssl x509 -in certs/user1.pem -noout -text >/dev/null 2>&1; then
    print_success "user1.pem is valid"
else
    print_error "user1.pem is invalid"
    exit 1
fi

if openssl x509 -in certs/ca.pem -noout -text >/dev/null 2>&1; then
    print_success "ca.pem is valid"
else
    print_error "ca.pem is invalid"
    exit 1
fi

# Show certificate info
print_info "Certificate details:"
echo "  Subject: $(openssl x509 -in certs/user1.pem -noout -subject | cut -d= -f2-)"
echo "  Expires: $(openssl x509 -in certs/user1.pem -noout -enddate | cut -d= -f2)"

# List final files
print_success "All certificates copied successfully!"
echo
print_info "Files in ./certs/:"
ls -la certs/

echo
print_info "Next steps:"
echo "1. Install pytak: pip3 install pytak"
echo "2. Update IP in pytak_test_ec2.py: $EC2_IP"
echo "3. Run test: python3 pytak_test_ec2.py"
echo "4. Check WebTAK: https://$EC2_IP:8443/webtak/index.html"