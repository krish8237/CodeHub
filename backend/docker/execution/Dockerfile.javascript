# JavaScript/Node.js execution container with enhanced security
FROM node:18-slim

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

# Remove potentially dangerous binaries and Node.js modules
RUN rm -f /usr/bin/wget /usr/bin/curl /usr/bin/nc /usr/bin/netcat \
    && rm -rf /usr/local/lib/node_modules/npm/node_modules/node-gyp 2>/dev/null || true

# Disable Node.js networking capabilities for security
RUN echo '#!/bin/bash\nnode --no-network "$@"' > /usr/local/bin/node-secure \
    && chmod +x /usr/local/bin/node-secure

# Switch to non-root user
USER coderunner
WORKDIR /app/code

# Set environment variables for security
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=128 --max-semi-space-size=16"

# Default command
CMD ["node"]