FROM python:3.8.6

# 设置工作目录
WORKDIR /app

# 替换为国内 Debian 镜像，加速 apt 安装，解决连接失败问题
RUN set -eux; \
    sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-writer \
        fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .

# 安装Python依赖
# 合并了您的多源安装逻辑，并进行了简化。
# 首先尝试升级pip，然后按顺序尝试从不同源安装requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple || \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.doubanio.com/simple || \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

# 复制整个项目（除了 .dockerignore 过滤掉的）
COPY . .

# 设置环境变量（可选）
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "aerich upgrade && uvicorn app.main:app --host 0.0.0.0 --port 8003"]
