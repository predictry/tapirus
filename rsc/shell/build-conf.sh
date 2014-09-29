#!/bin/bash

function buildConf(){

    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

    NGINX_NGINX_CONFIG=${DIR}/../conf/nginx-conf.conf
    NGINX_DEFAULT_CONFIG=${DIR}/../conf/nginx.default
    RC_LOCAL=${DIR}/../conf/rc.local

    if [ -f "$NGINX_NGINX_CONFIG" ]; then
        rm $NGINX_NGINX_CONFIG
    fi

    if [ -f "$NGINX_DEFAULT_CONFIG" ]; then
        rm $NGINX_DEFAULT_CONFIG
    fi

    if [ -f "$RC_LOCAL" ]; then
        rm RC_LOCAL
    fi

    n=$(echo `nproc`)

    #NGINX NGINX CONFIG

    echo "
    user www-data;
    pid /run/nginx.pid;
    worker_processes auto;
    worker_rlimit_nofile 400000;

    events {

        #worker_connections 1024;
        #worker_connections 8192;
        worker_connections 40000;
        use epoll;
        multi_accept on;

    }

    http {

        #logs
        error_log /var/log/nginx/error.log crit;
        access_log off;

        client_body_buffer_size 10K;
        client_header_buffer_size 1k;
        client_max_body_size 8m;
        large_client_header_buffers 2 1k;

        client_body_timeout 12;
        client_header_timeout 12;
        keepalive_timeout 30;
        send_timeout 10;

        # copies data between one FD and other from within the kernel
        # faster then read() + write()
        sendfile on;

        # send headers in one peace, its better then sending them one by one
        tcp_nopush on;

        # don't buffer data sent, good for small data bursts in real time
        tcp_nodelay on;

        # allow the server to close connection on non responding client, this will free up memory
        reset_timedout_connection on;

        #for security
        server_tokens off;

        #gzip             on;
        #gzip_comp_level  2;
        #gzip_min_length  1000;
        #gzip_proxied     expired no-cache no-store private auth;
        #gzip_types       text/plain application/x-javascript text/xml text/css application/xml;

        #default
        gzip              on;
        gzip_http_version 1.0;
        gzip_proxied      any;
        gzip_min_length   500;
        gzip_disable      \"MSIE [1-6]\.\";
        gzip_types        text/plain text/xml text/css
                          text/comma-separated-values
                          text/javascript
                          application/x-javascript
                          application/atom+xml;

        upstream app_servers {

        " >> $NGINX_NGINX_CONFIG


    for (( i=1; i<=$n; i++ ))
    do
        echo "      server unix:/tmp/unix_predictry_socket_${i}.sock fail_timeout=0;" >> $NGINX_NGINX_CONFIG
    done

    echo "
        }

        #security
        # limit the number of connections per single IP
        #limit_conn_zone \$binary_remote_addr zone=conn_limit_per_ip:10m;

        # limit the number of requests for a given session
        #limit_req_zone \$binary_remote_addr zone=req_limit_per_ip:10m rate=5r/s;

        # Configuration for Nginx
        server {

            #http auth
            auth_basic \"Restricted\";
            auth_basic_user_file /etc/nginx/.htpasswd;

            #security
            #limit_conn conn_limit_per_ip 10;
            #limit_req zone=req_limit_per_ip burst=10 nodelay;

            # Running port
            listen 80;

            # Settings to serve static files
            location ^~ /static/  {

                # Example:
                # root /full/path/to/application/static/file/dir;
                # root /app/static/;

            }

            # Serve a static file (ex. favico)
            # outside /static directory
            location = /favico.ico  {
                #root /app/favico.ico;

            }

            # Proxy connections to the application servers
            # app_servers
            location / {

                proxy_pass         http://app_servers;
                proxy_redirect     off;
                proxy_set_header   Host \$host;
                proxy_set_header   X-Real-IP \$remote_addr;
                proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
                proxy_set_header   X-Forwarded-Host \$server_name;

            }
        }

        #virtual hosts

        #include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/default;
    }
    " >> $NGINX_NGINX_CONFIG


    #NGINX DEFAULT CONFIG

    echo "
    # another virtual host using mix of IP-, name-, and port-based configuration

    server {
        listen 8000;
        #listen healthcheck:8000;
        server_name healthcheck;
        root /usr/share/nginx/html;
        index index.html index.htm;

        location / {
            try_files \$uri \$uri/ =404;
        }
    }
    " >> $NGINX_DEFAULT_CONFIG

    echo "
    #!/bin/sh -e
    #
    # rc.local
    #
    # This script is executed at the end of each multiuser runlevel.
    # Make sure that the script will "exit 0" on success or any other
    # value on error.
    #
    # In order to enable or disable this script just change the execution
    # bits.
    #
    # By default this script does nothing.

    APP=/apps/tapirus/app/rsc/shell/bin
    DEAMON=start-server.sh

    cd \$APP
    bash \$DEAMON

    exit 0" >> $RC_LOCAL

}

buildConf