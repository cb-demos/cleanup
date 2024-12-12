pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
    labels:
        app: helm-cleanup
spec:
    serviceAccountName: jenkins
    containers:
    - name: cleanup
      image: gcr.io/core-flow-research/cleanup:1.1.0
      imagePullPolicy: IfNotPresent
      command:
      - cat
      tty: true
'''
        }
    }

    triggers {
        cron('H 0 * * *')
    }

    options {
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Cleanup') {
            steps {
                container('cleanup') {
                    sh 'python expired_releases.py'
                }
            }
        }
    }
}
