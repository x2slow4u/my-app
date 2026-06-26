pipeline {
    agent any

    parameters {
        string(name: 'APP_NAME', defaultValue: 'my-app', description: 'Имя application и Docker image')
        string(name: 'GITHUB_OWNER', defaultValue: 'your-github-username', description: 'GitHub username или organization')
        string(name: 'REPOSITORY_URL', defaultValue: 'git@github.com:your-github-username/my-app.git', description: 'SSH URL GitHub repository')
    }

    environment {
        APP_NAME = "${params.APP_NAME}"
        DOCKER_REGISTRY = 'ghcr.io'
        DOCKER_USER = "${params.GITHUB_OWNER}"
        IMAGE = "${DOCKER_REGISTRY}/${DOCKER_USER}/${APP_NAME}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Клонирование repository ${APP_NAME}..."
                checkout([$class: 'GitSCM',
                    branches: [[name: 'main']],
                    userRemoteConfigs: [[
                        url: "${params.REPOSITORY_URL}",
                        credentialsId: 'github-ssh'
                    ]]
                ])
                sh 'ls -la'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Сборка Docker image..."
                    docker build -t ${APP_NAME}:${BUILD_NUMBER} .
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${APP_NAME}:latest
                    echo "Docker image собран: ${APP_NAME}:${BUILD_NUMBER}"
                '''
            }
        }

        stage('Test Image') {
            steps {
                sh '''
                    echo "Проверка Docker image..."
                    docker run --rm ${APP_NAME}:${BUILD_NUMBER} echo "Container работает!"
                '''
            }
        }

        stage('Tag for GHCR') {
            steps {
                sh '''
                    echo "Создание tags для GitHub Container Registry..."
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${IMAGE}:${BUILD_NUMBER}
                    docker tag ${APP_NAME}:latest ${IMAGE}:latest
                    echo "Tags созданы:"
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
                        echo "Login в GitHub Container Registry..."
                        echo ${GH_TOKEN} | docker login ghcr.io -u ${GH_USERNAME} --password-stdin

                        echo "Push image: ${IMAGE}:${BUILD_NUMBER}"
                        docker push ${IMAGE}:${BUILD_NUMBER}

                        echo "Push image: ${IMAGE}:latest"
                        docker push ${IMAGE}:latest

                        echo "Push завершен"
                    '''
                }
            }
        }

        stage('Deploy with Compose') {
            steps {
                sh '''
                    echo "Запуск services через Docker Compose..."
                    docker-compose up -d
                    sleep 5
                    docker-compose ps
                '''
            }
        }

        stage('Integration Test') {
            steps {
                sh '''
                    echo "Проверка web service..."
                    curl -f http://localhost:5000/ || exit 1
                    curl -f http://localhost:5000/health || exit 1
                    curl -f http://localhost:5000/db || exit 1
                    echo "Все tests пройдены!"
                '''
            }
        }

        stage('Test Monitoring') {
            steps {
                sh '''
                    echo "Проверка Prometheus..."
                    curl -f http://localhost:9090/-/healthy || exit 1

                    echo "Ожидание готовности Grafana..."
                    sleep 10

                    echo "Проверка Grafana..."
                    curl -f http://localhost:3000/api/health || exit 1

                    echo "Monitoring services healthy!"
                '''
            }
        }

         stage('Stop Services') {
             steps {
                 sh '''
                     echo "Остановка services..."
                     docker-compose down
                 '''
             }
         }

        stage('Clean Up') {
            steps {
                sh '''
                    echo "Очистка..."
                    docker logout ghcr.io || true
                    echo "Очистка завершена"
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
            echo "Pipeline завершен. Build: ${BUILD_NUMBER}, Result: ${currentBuild.result}"
        }
    }
}
