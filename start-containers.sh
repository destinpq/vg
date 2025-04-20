#!/bin/bash
# Script to build and start the containers with proper error handling

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Starting Video Generation Application ===${NC}"

# Function to check if Docker is installed
check_docker() {
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
  fi
  
  if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
  fi
}

# Function to build the containers
build_containers() {
  echo -e "${BLUE}Building backend container...${NC}"
  docker-compose build backend
  
  echo -e "${BLUE}Building frontend container...${NC}"
  docker-compose build frontend
}

# Function to start the containers
start_containers() {
  echo -e "${BLUE}Starting containers...${NC}"
  docker-compose up -d
  
  echo -e "${GREEN}Containers started successfully!${NC}"
  echo -e "${BLUE}Backend API is available at:${NC} http://localhost:5001"
  echo -e "${BLUE}Frontend is available at:${NC} http://localhost:3000"
}

# Function to check container logs for errors
check_logs() {
  echo -e "${BLUE}Checking backend logs for errors...${NC}"
  if docker-compose logs backend | grep -i "error"; then
    echo -e "${YELLOW}⚠️ Errors found in backend logs. Please check the logs for details.${NC}"
  else
    echo -e "${GREEN}No errors found in backend logs.${NC}"
  fi
  
  echo -e "${BLUE}Checking frontend logs for errors...${NC}"
  if docker-compose logs frontend | grep -i "error"; then
    echo -e "${YELLOW}⚠️ Errors found in frontend logs. Please check the logs for details.${NC}"
  else
    echo -e "${GREEN}No errors found in frontend logs.${NC}"
  fi
}

# Main execution
check_docker

# Stop any running containers
echo -e "${BLUE}Stopping any running containers...${NC}"
docker-compose down

# Build and start the containers
build_containers
start_containers

# Wait for containers to initialize
echo -e "${YELLOW}Waiting for containers to initialize...${NC}"
sleep 10

# Check container status
echo -e "${BLUE}Checking container status...${NC}"
docker-compose ps

# Check logs for errors
check_logs

# Display container info
echo -e "\n${GREEN}=== Container Info ===${NC}"
echo -e "${BLUE}Backend container ID:${NC} $(docker-compose ps -q backend)"
echo -e "${BLUE}Frontend container ID:${NC} $(docker-compose ps -q frontend)"

echo -e "\n${GREEN}=== Done! ===${NC}"
echo -e "To view logs in real-time, run: docker-compose logs -f"
echo -e "To stop containers, run: docker-compose down" 