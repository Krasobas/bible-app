pipeline {
    agent { label 'agent1' }

    environment {
        API_KEY = credentials('bible-study-api-key')
        DOMAIN  = credentials('bible-study-domain')
    }

    stages {
        stage('Build Image') {
            steps {
                sh 'docker build -t bible-study-app:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose up -d --build --force-recreate'
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
