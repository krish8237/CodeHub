# C++ execution container with enhanced security
FROM gcc:11-slim

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

# Remove potentially dangerous binaries and libraries
RUN rm -f /usr/bin/wget /usr/bin/curl /usr/bin/nc /usr/bin/netcat \
    && rm -f /usr/bin/gdb /usr/bin/objdump /usr/bin/strace

# Create wrapper script for secure compilation
RUN echo '#!/bin/bash\ng++ -fstack-protector-strong -D_FORTIFY_SOURCE=2 -fPIE -pie -Wl,-z,relro -Wl,-z,now "$@"' > /usr/local/bin/g++-secure \
    && chmod +x /usr/local/bin/g++-secure

# Switch to non-root user
USER coderunner
WORKDIR /app/code

# Set environment variables for security
ENV CXXFLAGS="-fstack-protector-strong -D_FORTIFY_SOURCE=2"
ENV LDFLAGS="-Wl,-z,relro -Wl,-z,now"

# Default command
CMD ["g++"]