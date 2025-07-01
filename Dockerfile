FROM python:3.8.6

# 设置工作目录
WORKDIR /app

# 关键步骤: 更新apt缓存并安装LibreOffice Writer和中文字体
# 这对于处理Word文档中的中文至关重要，防止PDF乱码
RUN apt-get update && apt-get install -y \
    # 只安装Writer组件，而不是整个LibreOffice套件
    libreoffice-writer \
    # 安装推荐的中文字体，保证中文字符能正确显示
    fonts-noto-cjk \
    # [优化] 不安装“推荐”的非必需软件包，显著减小镜像体积
    --no-install-recommends \
    # [优化] 在同一层(RUN)中清理apt缓存，减小最终镜像大小
    && rm -rf /var/lib/apt/lists/*

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
