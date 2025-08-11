#!/bin/bash

# TAK Server AWS EC2 Deployment Script
# This script helps automate the deployment of TAK Server to AWS EC2

set -e

# Color output functions
color() {
    STARTCOLOR="\e[$2";
    ENDCOLOR="\e[0m";
    export "$1"="$STARTCOLOR%b$ENDCOLOR" 
}
color info 96m
color success 92m 
color warning 93m 
color danger 91m 

printf $success "\n🚀 TAK Server AWS EC2 Deployment Helper\n"
printf $info "========================================\n"

# Check if we're running on EC2
if curl -s http://169.254.169.254/latest/meta-data/instance-id &>/dev/null; then
    printf $success "✅ Running on AWS EC2 instance\n"
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    printf $info "Instance ID: $INSTANCE_ID\n"
    printf $info "Public IP: $PUBLIC_IP\n"
else
    printf $warning "⚠️  Not running on EC2 - this script is designed for EC2 deployment\n"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker
install_docker() {
    printf $info "\n📦 Installing Docker...\n"
    
    # Remove old versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Update package index
    sudo apt-get update
    
    # Install dependencies
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        net-tools \
        unzip \
        zip

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Add user to docker group
    sudo usermod -aG docker $USER
    
    printf $success "✅ Docker installed successfully\n"
    printf $warning "⚠️  You may need to log out and back in for docker group changes to take effect\n"
}

# Function to setup firewall
setup_firewall() {
    printf $info "\n🔥 Configuring UFW firewall...\n"
    
    # Enable UFW
    sudo ufw --force enable
    
    # Allow SSH
    sudo ufw allow 22/tcp comment 'SSH'
    
    # Allow TAK Server ports
    sudo ufw allow 8089/tcp comment 'TAK SSL Client'
    sudo ufw allow 8443/tcp comment 'TAK Web Interface'
    sudo ufw allow 8444/tcp comment 'TAK Certificate Auth'
    sudo ufw allow 8446/tcp comment 'TAK API'
    sudo ufw allow 9000/tcp comment 'TAK Streaming'
    sudo ufw allow 9001/tcp comment 'TAK Federation'
    
    printf $success "✅ Firewall configured\n"
    sudo ufw status numbered
}

# Function to create environment file
create_env_file() {
    printf $info "\n📝 Creating environment configuration...\n"
    
    # Get public IP if on EC2
    if [ ! -z "$PUBLIC_IP" ]; then
        DEFAULT_IP=$PUBLIC_IP
    else
        DEFAULT_IP="localhost"
    fi
    
    read -p "Enter your public IP or domain name [$DEFAULT_IP]: " USER_IP
    USER_IP=${USER_IP:-$DEFAULT_IP}
    
    read -p "Enter country code [US]: " COUNTRY
    COUNTRY=${COUNTRY:-US}
    
    read -p "Enter state [CA]: " STATE
    STATE=${STATE:-CA}
    
    read -p "Enter city [San Francisco]: " CITY
    CITY=${CITY:-"San Francisco"}
    
    read -p "Enter organization [TAK]: " ORG
    ORG=${ORG:-TAK}
    
    cat << EOF > .env
# TAK Server Configuration
COUNTRY=$COUNTRY
STATE=$STATE
CITY=$CITY
ORGANIZATIONAL_UNIT=$ORG
ORGANIZATION=$ORG

# Server IP/Domain
PUBLIC_IP=$USER_IP
EOF
    
    printf $success "✅ Environment file created\n"
}

# Function to update CoreConfig.xml
update_config() {
    printf $info "\n⚙️  Updating CoreConfig.xml...\n"
    
    if [ -f "CoreConfig.xml" ]; then
        # Backup original
        cp CoreConfig.xml CoreConfig.xml.backup
        
        # Update IP addresses in CoreConfig.xml
        if [ ! -z "$USER_IP" ]; then
            sed -i "s/HOSTIP/$USER_IP/g" CoreConfig.xml
        fi
        
        printf $success "✅ CoreConfig.xml updated\n"
    else
        printf $warning "⚠️  CoreConfig.xml not found - will use default\n"
    fi
}

# Function to setup health monitoring
setup_monitoring() {
    printf $info "\n📊 Setting up health monitoring...\n"
    
    cat << 'EOF' > health-check.sh
#!/bin/bash
LOG_FILE="/home/ubuntu/health-check.log"
if curl -k -s https://localhost:8443 > /dev/null; then
    echo "$(date): TAK Server is healthy" >> $LOG_FILE
else
    echo "$(date): TAK Server is down! Restarting..." >> $LOG_FILE
    cd ~/tak-server && docker compose restart >> $LOG_FILE 2>&1
fi
EOF
    
    chmod +x health-check.sh
    
    # Add to crontab if not already there
    (crontab -l 2>/dev/null | grep -v "health-check.sh"; echo "*/5 * * * * $(pwd)/health-check.sh") | crontab -
    
    printf $success "✅ Health monitoring configured (runs every 5 minutes)\n"
}

# Function to setup backup script
setup_backup() {
    printf $info "\n💾 Setting up automated backups...\n"
    
    mkdir -p ~/tak-backups
    
    cat << 'EOF' > backup-tak.sh
#!/bin/bash
BACKUP_DIR="$HOME/tak-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="tak-backup-$DATE.tar.gz"

echo "$(date): Starting backup..." >> $HOME/backup.log

# Stop containers
cd ~/tak-server
docker compose down >> $HOME/backup.log 2>&1

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    tak/ \
    .env \
    CoreConfig.xml \
    docker-compose.yml 2>> $HOME/backup.log

# Restart containers
docker compose up -d >> $HOME/backup.log 2>&1

# Keep only last 7 days of backups
find $BACKUP_DIR -name "tak-backup-*.tar.gz" -mtime +7 -delete

echo "$(date): Backup completed: $BACKUP_FILE" >> $HOME/backup.log
EOF
    
    chmod +x backup-tak.sh
    
    # Add to crontab for daily backup at 2 AM
    (crontab -l 2>/dev/null | grep -v "backup-tak.sh"; echo "0 2 * * * $(pwd)/backup-tak.sh") | crontab -
    
    printf $success "✅ Automated daily backups configured (2 AM)\n"
}

# Function to display final information
show_completion_info() {
    printf $success "\n🎉 TAK Server AWS Deployment Complete!\n"
    printf $info "==========================================\n"
    
    if [ ! -z "$PUBLIC_IP" ]; then
        printf $info "🌐 Web Interface: https://$PUBLIC_IP:8443\n"
        printf $info "🔗 API Access: https://$PUBLIC_IP:8446\n"
        printf $info "📱 Client Port: $PUBLIC_IP:8089\n"
    fi
    
    printf $info "\n📋 Next Steps:\n"
    printf $info "1. Wait for setup.sh to complete (if running)\n"
    printf $info "2. Import admin.p12 certificate to your browser\n"
    printf $info "3. Access web interface and create users\n"
    printf $info "4. Generate client certificates for ATAK/iTAK\n"
    printf $info "5. Test connectivity with your devices\n"
    
    printf $info "\n🔧 Useful Commands:\n"
    printf $info "- Check status: docker ps\n"
    printf $info "- View logs: docker logs -f tak-server-tak-1\n"
    printf $info "- Restart: docker compose restart\n"
    printf $info "- Backup now: ./backup-tak.sh\n"
    
    printf $warning "\n⚠️  Security Reminders:\n"
    printf $warning "- Change default passwords immediately\n"
    printf $warning "- Restrict SSH access to your IP only\n"
    printf $warning "- Keep certificates secure\n"
    printf $warning "- Monitor logs regularly\n"
}

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d "scripts" ]; then
        printf $danger "❌ This doesn't appear to be the tak-server directory\n"
        printf $info "Please run this script from the root of the tak-server repository\n"
        exit 1
    fi
    
    # Check for TAK release file
    if ! ls takserver-docker-*.zip 1> /dev/null 2>&1; then
        printf $warning "⚠️  No TAK release ZIP file found\n"
        printf $info "Please download the official TAK release from https://tak.gov/products/tak-server\n"
        printf $info "and place it in this directory before continuing\n"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Install Docker if not present
    if ! command_exists docker; then
        install_docker
        printf $warning "⚠️  Please log out and back in, then run this script again\n"
        exit 0
    fi
    
    # Check if docker works without sudo
    if ! docker ps &>/dev/null; then
        printf $warning "⚠️  Docker requires sudo. Adding user to docker group...\n"
        sudo usermod -aG docker $USER
        printf $warning "⚠️  Please log out and back in, then run this script again\n"
        exit 0
    fi
    
    # Setup firewall
    setup_firewall
    
    # Create environment file
    create_env_file
    
    # Update configuration
    update_config
    
    # Setup monitoring and backups
    setup_monitoring
    setup_backup
    
    # Ask if user wants to run setup now
    printf $info "\n🚀 Ready to run TAK Server setup!\n"
    read -p "Run setup.sh now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        printf $info "Running setup.sh...\n"
        chmod +x scripts/setup.sh
        ./scripts/setup.sh
    else
        printf $info "You can run setup later with: ./scripts/setup.sh\n"
    fi
    
    show_completion_info
}

# Run main function
main "$@"