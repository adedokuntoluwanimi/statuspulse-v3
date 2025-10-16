pipeline {
    agent any

    environment {
        REPO_NAME = "statuspulse-v3"
        DOCKERHUB_USER = credentials('dockerhub-user')  // Jenkins credential ID
        DOCKERHUB_PASS = credentials('dockerhub-pass')  // Jenkins credential ID
        BACKEND_IMAGE = "adedokuntoluwanimi/statuspulse-backend"
        FRONTEND_IMAGE = "adedokuntoluwanimi/statuspulse-frontend"
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
                    echo "Pushing images to Docker Hub..."
                    sh """
                    echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin
                    docker push $BACKEND_IMAGE:latest
                    docker push $FRONTEND_IMAGE:latest
                    docker logout
                    """
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    echo "Deploying to EC2 instance..."
                    sh """
                    ssh -o StrictHostKeyChecking=no ubuntu@3.251.73.191 '
                        cd /opt/statuspulse &&
                        sudo git pull origin main &&
                        sudo docker compose pull &&
                        sudo docker compose up -d --remove-orphans
                    '
                    """
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

