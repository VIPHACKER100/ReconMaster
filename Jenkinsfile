// ReconMaster Jenkins Pipeline
// This is an example Jenkinsfile for automated reconnaissance
// Configure Jenkins credentials and environment variables before use

pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        GO_VERSION = '1.21'
        RECON_DOMAIN = credentials('recon-domain')
        WEBHOOK_URL = credentials('discord-webhook')
        DOCKER_IMAGE = 'reconmaster:latest'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timestamps()
        timeout(time: 2, unit: 'HOURS')
    }
    
    triggers {
        // Run daily at midnight
        cron('H 0 * * *')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git clean -fdx'
            }
        }
        
        stage('Setup Environment') {
            parallel {
                stage('Python Setup') {
                    steps {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
                
                stage('Go Setup') {
                    steps {
                        sh '''
                            export GOPATH=$HOME/go
                            export PATH=$PATH:$GOPATH/bin
                            go version
                        '''
                    }
                }
            }
        }
        
        stage('Install Tools') {
            steps {
                sh '''
                    chmod +x scripts/install_tools.sh
                    ./scripts/install_tools.sh
                '''
            }
        }
        
        stage('Run Tests') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    . venv/bin/activate
                    pip install -r requirements-dev.txt
                    pytest tests/ -v --cov=reconmaster --cov-report=xml
                    flake8 reconmaster.py
                '''
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }
        
        stage('Security Scan') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    . venv/bin/activate
                    pip install bandit safety
                    bandit -r reconmaster.py -f json -o bandit-report.json || true
                    safety check --json > safety-report.json || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(env.DOCKER_IMAGE)
                }
            }
        }
        
        stage('Run Reconnaissance') {
            parallel {
                stage('Standard Scan') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            python reconmaster.py \
                                -d ${RECON_DOMAIN} \
                                --daily \
                                --webhook ${WEBHOOK_URL} \
                                --i-understand-this-requires-authorization
                        '''
                    }
                }
                
                stage('Docker Scan') {
                    steps {
                        script {
                            docker.image(env.DOCKER_IMAGE).inside {
                                sh '''
                                    python reconmaster.py \
                                        -d ${RECON_DOMAIN} \
                                        --daily \
                                        --webhook ${WEBHOOK_URL} \
                                        --i-understand-this-requires-authorization
                                '''
                            }
                        }
                    }
                }
            }
        }
        
        stage('Process Results') {
            steps {
                sh '''
                    # Generate summary
                    if [ -f recon_results/*/summary.json ]; then
                        cat recon_results/*/summary.json | jq '.' > scan-summary.json
                    fi
                    
                    # Compress results
                    tar -czf recon-results-${BUILD_NUMBER}.tar.gz recon_results/
                '''
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'recon-results-*.tar.gz', fingerprint: true
                archiveArtifacts artifacts: 'scan-summary.json', allowEmptyArchive: true
            }
        }
        
        stage('Publish Reports') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'recon_results',
                    reportFiles: '*/full_report.html',
                    reportName: 'Reconnaissance Report'
                ])
            }
        }
        
        stage('Diff Analysis') {
            when {
                expression { fileExists('.reconmaster_state.json') }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    python reconmaster.py \
                        -d ${RECON_DOMAIN} \
                        --daily \
                        --diff-only \
                        --webhook ${WEBHOOK_URL} \
                        --i-understand-this-requires-authorization
                '''
            }
        }
    }
    
    post {
        success {
            script {
                def summary = readJSON file: 'scan-summary.json'
                def message = """
                ✅ ReconMaster Scan Completed Successfully
                
                Target: ${env.RECON_DOMAIN}
                Build: #${env.BUILD_NUMBER}
                
                Statistics:
                - Subdomains: ${summary.statistics.subdomains_found}
                - Live Hosts: ${summary.statistics.live_hosts}
                - Vulnerabilities: ${summary.statistics.vulnerabilities}
                - Endpoints: ${summary.statistics.endpoints_discovered}
                
                View Report: ${env.BUILD_URL}Reconnaissance_Report/
                """
                
                // Send notification
                sh """
                    curl -X POST ${env.WEBHOOK_URL} \
                        -H "Content-Type: application/json" \
                        -d '{"content": "${message}"}'
                """
            }
        }
        
        failure {
            sh """
                curl -X POST ${env.WEBHOOK_URL} \
                    -H "Content-Type: application/json" \
                    -d '{"content": "❌ ReconMaster scan failed for ${env.RECON_DOMAIN}\\nBuild: #${env.BUILD_NUMBER}\\nView: ${env.BUILD_URL}"}'
            """
        }
        
        always {
            cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: 'venv/', type: 'INCLUDE'],
                    [pattern: '.cache/', type: 'INCLUDE']
                ]
            )
        }
    }
}
