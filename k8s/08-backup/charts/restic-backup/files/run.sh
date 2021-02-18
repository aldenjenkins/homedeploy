#!/bin/bash -xe
run_restic () {
    NAME=${1}; shift
    BUCKET=${1}; shift
    TARGET=${1}; shift
    telegram -t ${TELEGRAM_TOKEN} -c ${TELEGRAM_CLIENT} "${NAME}: backup started"
    REPO_EXISTS=$(rclone lsjson ${BUCKET}/config | jq length)
    if [ ${REPO_EXISTS} -ne 1 ];
    then
        restic \
            --cache-dir /cache/${NAME} \
            --password-file /secret/RESTIC_PASSWORD \
            --repo rclone:${BUCKET} \
            --verbose=2 \
            init
        telegram -t ${TELEGRAM_TOKEN} -c ${TELEGRAM_CLIENT} "${NAME}: remote repo initialized"
    fi
    restic \
        --cache-dir /cache/${NAME} \
        --password-file /secret/RESTIC_PASSWORD \
        --repo rclone:${BUCKET} \
        --verbose=2 \
        backup ${TARGET} \
        | tee /tmp/execution.txt

    if [ 0 -eq ${PIPESTATUS[0]} ]
    then
        export STATUS="success"
        export RC=0
    else
        export STATUS="failure"
        export RC=1
    fi
    telegram -t "${TELEGRAM_TOKEN}" -c "${TELEGRAM_CLIENT}" -f /tmp/execution.txt "${NAME}: backup ${STATUS}"
}

run_restic $@