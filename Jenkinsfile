pipeline {
  agent any

  environment {
    REPO_NAME      = "statuspulse-v3"
    BACKEND_IMAGE  = "adedokuntoluwanimi/statuspulse-backend"
    FRONTEND_IMAGE = "adedokuntoluwanimi/statuspulse-frontend"
  }

  stages {
    stage('Checkout') {
      steps {
        echo "Pulling latest code from GitHub..."
        checkout scm
      }
    }

    stage('Build Docker Images') {
      steps {
        script {
          echo "Building backend and frontend Docker images..."
          sh """
            docker build -t $BACKEND_IMAGE:latest ./backend
            docker build -t $FRONTEND_IMAGE:latest ./frontend
          """
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        script {
          echo "Pushing Docker images to Docker Hub..."
          withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
            sh '''
              echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
              docker push $BACKEND_IMAGE:latest
              docker push $FRONTEND_IMAGE:latest
              docker logout || true
            '''
          }
        }
      }
    }

    stage('Deploy to EC2') {
      steps {
        script {
          echo "Deploying containers on EC2..."
          sh '''
            ssh -o StrictHostKeyChecking=no ubuntu@3.238.13.247 '
              cd /opt/statuspulse &&
              sudo docker compose pull &&
              sudo docker compose up -d --remove-orphans
            '
          '''
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

