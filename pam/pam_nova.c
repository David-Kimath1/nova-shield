/*
 * NOVA-SHIELD PAM Module
 * Integrates face authentication into Linux login
 */

#include <security/pam_modules.h>
#include <security/pam_ext.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SOCKET_PATH "/tmp/nova_shield.sock"

/* Forward declarations */
int send_auth_request(const char *username);
int wait_for_auth_response();

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,
                                   int argc, const char **argv) {
    const char *username = NULL;
    int retval;
    int auth_result;
    
    /* Get username */
    retval = pam_get_user(pamh, &username, NULL);
    if (retval != PAM_SUCCESS || username == NULL) {
        pam_syslog(pamh, LOG_ERR, "Cannot get username");
        return PAM_AUTH_ERR;
    }
    
    pam_syslog(pamh, LOG_INFO, "NOVA-SHIELD: Authenticating user %s", username);
    
    /* Send authentication request to NOVA-SHIELD daemon */
    auth_result = send_auth_request(username);
    
    if (auth_result == 1) {
        pam_syslog(pamh, LOG_INFO, "NOVA-SHIELD: Authentication successful");
        
        /* Check if we need to fall back to password */
        const char *password = NULL;
        if (flags & PAM_DISALLOW_NULL_AUTHTOK) {
            retval = pam_get_authtok(pamh, PAM_AUTHTOK, &password, NULL);
            if (retval == PAM_SUCCESS && password != NULL) {
                /* Password fallback */
                return PAM_SUCCESS;
            }
        }
        
        return PAM_SUCCESS;
    } else if (auth_result == 0) {
        pam_syslog(pamh, LOG_WARNING, "NOVA-SHIELD: Authentication failed");
        return PAM_AUTH_ERR;
    } else {
        pam_syslog(pamh, LOG_ERR, "NOVA-SHIELD: Service unavailable");
        return PAM_AUTHINFO_UNAVAIL;
    }
}

int send_auth_request(const char *username) {
    int sock;
    struct sockaddr_un addr;
    char buffer[256];
    ssize_t n;
    
    sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock < 0) {
        return -1;
    }
    
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);
    
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(sock);
        return -1;
    }
    
    /* Send username */
    snprintf(buffer, sizeof(buffer), "AUTH:%s", username);
    if (write(sock, buffer, strlen(buffer)) < 0) {
        close(sock);
        return -1;
    }
    
    /* Wait for response */
    n = read(sock, buffer, sizeof(buffer) - 1);
    close(sock);
    
    if (n > 0) {
        buffer[n] = '\0';
        return strcmp(buffer, "GRANTED") == 0 ? 1 : 0;
    }
    
    return -1;
}

PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags,
                              int argc, const char **argv) {
    return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags,
                                int argc, const char **argv) {
    return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_open_session(pam_handle_t *pamh, int flags,
                                   int argc, const char **argv) {
    return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_close_session(pam_handle_t *pamh, int flags,
                                    int argc, const char **argv) {
    return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_chauthtok(pam_handle_t *pamh, int flags,
                                int argc, const char **argv) {
    return PAM_SUCCESS;
}