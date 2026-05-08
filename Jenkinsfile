pipeline {
    agent { label 'agent1' }

    stages {
        stage('Build Image') {
            steps {
                sh 'docker build -t bible-study-app:latest .'
            }
        }

        stage('Deploy') {
            steps {
                // Write .env from Jenkins credentials
                withCredentials([
                    string(credentialsId: 'bible-study-api-key', variable: 'API_KEY'),
                    string(credentialsId: 'bible-study-domain', variable: 'DOMAIN'),
                ]) {
                    sh '''
                        cat > .env <<EOF
API_KEY=${API_KEY}
DOMAIN=${DOMAIN}
SITE_TITLE=Библейский кружок
SITE_SUBTITLE=Комментарий для XXI века
EOF
                    '''
                }
                sh 'docker compose up -d --build --force-recreate'
            }
        }
    }

    post {
        failure {
            echo 'Deployment failed. Check logs: docker compose logs bible-study-app'
        }
        success {
            echo 'Deployed successfully.'
        }
    }
}
