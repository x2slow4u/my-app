pipeline {
    agent any
    
    environment {
        APP_NAME = 'my-app'
        DOCKER_REGISTRY = 'ghcr.io'
        DOCKER_USER = 'x2slow4u'
        IMAGE = "${DOCKER_REGISTRY}/${DOCKER_USER}/${APP_NAME}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Cloning ${APP_NAME} repository..."
                checkout([$class: 'GitSCM',
                    branches: [[name: 'main']],
                    userRemoteConfigs: [[
                        url: 'git@github.com:x2slow4u/my-app.git',
                        credentialsId: 'github-ssh'
                    ]]
                ])
                sh 'ls -la'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t ${APP_NAME}:${BUILD_NUMBER} .
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${APP_NAME}:latest
                    echo "Image built: ${APP_NAME}:${BUILD_NUMBER}"
                '''
            }
        }

        stage('Test Image') {
            steps {
                sh '''
                    echo "Testing image..."
                    docker run --rm ${APP_NAME}:${BUILD_NUMBER} echo "Container works!"
                '''
            }
        }

        stage('Tag for GHCR') {
            steps {
                sh '''
                    echo "Tagging image for GitHub Container Registry..."
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${IMAGE}:${BUILD_NUMBER}
                    docker tag ${APP_NAME}:latest ${IMAGE}:latest
                    echo "Tags created:"
                    docker images | grep ${APP_NAME}
                '''
            }
        }

        stage('Push to GHCR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-ghcr',
                    usernameVariable: 'GH_USERNAME',
                    passwordVariable: 'GH_TOKEN'
                )]) {
                    sh '''
                        echo "Logging into GitHub Container Registry..."
                        echo ${GH_TOKEN} | docker login ghcr.io -u ${GH_USERNAME} --password-stdin

                        echo "Pushing image: ${IMAGE}:${BUILD_NUMBER}"
                        docker push ${IMAGE}:${BUILD_NUMBER}

                        echo "Pushing image: ${IMAGE}:latest"
                        docker push ${IMAGE}:latest

                        echo "Push completed"
                    '''
                }
            }
        }

        stage('Deploy with Compose') {
            steps {
                sh '''
                    echo "Starting services with Docker Compose..."
                    docker-compose up -d
                    sleep 5
                    docker-compose ps
                '''
            }
        }

        stage('Integration Test') {
            steps {
                sh '''
                    echo "Testing web service..."
                    curl -f http://localhost:5000/ || exit 1
                    curl -f http://localhost:5000/health || exit 1
                    curl -f http://localhost:5000/db || exit 1
                    echo "All tests passed!"
                '''
            }
        }

//         stage('Stop Services') {
//             steps {
//                 sh '''
//                     echo "Stopping services..."
//                     docker-compose down
//                 '''
//             }
//         }

        stage('Clean Up') {
            steps {
                sh '''
                    echo "Cleaning up..."
                    docker logout ghcr.io || true
                    echo "Cleanup completed"
                '''
            }
        }
    }

    post {
        success {
            echo "PIPELINE SUCCESSFUL"
            echo "Image: ${IMAGE}:${BUILD_NUMBER}"
            echo "URL: https://github.com/${DOCKER_USER}/${APP_NAME}/pkgs/container/${APP_NAME}"
        }
        failure {
            echo "PIPELINE FAILED"
            echo "Build number: ${BUILD_NUMBER}"
        }
        always {
            echo "Pipeline finished. Build: ${BUILD_NUMBER}, Result: ${currentBuild.result}"
        }
    }
}