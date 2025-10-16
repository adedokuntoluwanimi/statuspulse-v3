pipeline {
    agent any

    environment {
        REPO_NAME = "statuspulse-v3"
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')  // Jenkins Docker Hub credentials
        BACKEND_IMAGE = "adedokuntoluwanimi/statuspulse-backend"
        FRONTEND_IMAGE = "adedokuntoluwanimi/statuspulse-frontend"
        EC2_HOST = "3.238.13.247"
        EC2_USER = "ubuntu"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    dir('backend') {
                        echo "Building backend Docker image..."
                        sh """
                        docker build -t $BACKEND_IMAGE:latest .
                        """
                    }
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                script {
                    dir('frontend') {
                        echo "Building frontend Docker image..."
                        sh """
                        docker build -t $FRONTEND_IMAGE:latest .
                        """
                    }
                }
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                script {
                    echo "Logging into Docker Hub and pushing images..."
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push $BACKEND_IMAGE:latest
                        docker push $FRONTEND_IMAGE:latest
                        docker logout
                        """
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    echo "Deploying containers on EC2..."

                    sshagent(credentials: ['ec2-ssh']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST "
                            set -eux

                            # Ensure application directory exists
                            sudo mkdir -p /opt/statuspulse
                            sudo chown ubuntu:ubuntu /opt/statuspulse

                            # Create docker-compose.yml if missing
                            if [ ! -f /opt/statuspulse/docker-compose.yml ]; then
                                cat > /opt/statuspulse/docker-compose.yml <<'YML'
version: "3.9"
services:
  backend:
    image: adedokuntoluwanimi/statuspulse-backend:latest
    container_name: statuspulse-backend
    ports:
      - "8081:8081"
    environment:
      - TZ=Africa/Lagos
    volumes:
      - statuspulse_db:/data
    restart: unless-stopped

  frontend:
    image: adedokuntoluwanimi/statuspulse-frontend:latest
    container_name: statuspulse-frontend
    depends_on:
      - backend
    ports:
      - "80:80"
    environment:
      - TZ=Africa/Lagos
    restart: unless-stopped

volumes:
  statuspulse_db:
    name: statuspulse_db
YML
                            fi

                            cd /opt/statuspulse
                            sudo docker compose pull
                            sudo docker compose up -d --remove-orphans
                        "
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment completed successfully."
        }
        failure {
            echo "❌ Deployment failed. Check Jenkins logs for details."
        }
    }
}

