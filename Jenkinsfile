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
                withCredentials([
                    string(credentialsId: 'bible-study-api-key', variable: 'API_KEY'),
                    string(credentialsId: 'bible-study-domain', variable: 'DOMAIN'),
                ]) {
                    sh '''
                        printf 'API_KEY=%s\nDOMAIN=%s\nSITE_TITLE=Библейский кружок\nSITE_SUBTITLE=Комментарий для XXI века\n' "$API_KEY" "$DOMAIN" > .env
                    '''
                    sh 'docker compose up -d --build --force-recreate'
                }
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
