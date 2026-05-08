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
                        echo "API_KEY=$API_KEY" > .env
                        echo "DOMAIN=$DOMAIN" >> .env
                        echo "SITE_TITLE=Библейский кружок" >> .env
                        echo "SITE_SUBTITLE=Комментарий для XXI века" >> .env
                        docker compose up -d --build --force-recreate
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                def status = currentBuild.currentResult
                def emoji = status == 'SUCCESS' ? '✅' : status == 'FAILURE' ? '❌' : '⚠️'
                def duration = currentBuild.durationString.replace(' and counting', '')
                def buildInfo = """
${emoji} *Bible App* — #${currentBuild.number}
━━━━━━━━━━━━━━━━━━━━
📌 Status: *${status}*
🕐 Started: ${new Date(currentBuild.startTimeInMillis).format('dd.MM.yyyy HH:mm:ss')}
⏱ Duration: ${duration}
━━━━━━━━━━━━━━━━━━━━
🔗 [Open in Jenkins](${env.BUILD_URL})
                """.trim()
                telegramSend(message: buildInfo)
            }
        }
    }
}
