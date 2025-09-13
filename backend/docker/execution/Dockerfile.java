# Java execution container with enhanced security
FROM openjdk:17-slim

# Install security tools
RUN apt-get update && apt-get install -y \
    timeout \
    coreutils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security with restricted permissions
RUN useradd -m -u 1000 -s /bin/bash coderunner \
    && usermod -L coderunner

# Set strict resource limits
RUN echo "coderunner soft nproc 16" >> /etc/security/limits.conf \
    && echo "coderunner hard nproc 16" >> /etc/security/limits.conf \
    && echo "coderunner soft nofile 32" >> /etc/security/limits.conf \
    && echo "coderunner hard nofile 32" >> /etc/security/limits.conf \
    && echo "coderunner soft fsize 10485760" >> /etc/security/limits.conf \
    && echo "coderunner hard fsize 10485760" >> /etc/security/limits.conf

# Create execution directory with proper permissions
RUN mkdir -p /app/code \
    && chown coderunner:coderunner /app/code \
    && chmod 755 /app/code

# Remove potentially dangerous binaries
RUN rm -f /usr/bin/wget /usr/bin/curl /usr/bin/nc /usr/bin/netcat

# Create Java security policy file
RUN echo 'grant {\n\
    permission java.io.FilePermission "/app/code/-", "read,write,delete";\n\
    permission java.io.FilePermission "/tmp/-", "read,write,delete";\n\
    permission java.lang.RuntimePermission "exitVM";\n\
    permission java.util.PropertyPermission "*", "read";\n\
};' > /app/code/security.policy

# Switch to non-root user
USER coderunner
WORKDIR /app/code

# Set environment variables for security
ENV JAVA_OPTS="-Xmx128m -Xms32m -XX:MaxMetaspaceSize=64m -Djava.security.manager -Djava.security.policy=/app/code/security.policy"

# Default command
CMD ["java"]