FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libglu1-mesa \
    libxi6 \
    libxrender1 \
    libxrandr2 \
    libxinerama1 \
    libxcursor1 \
    libxkbcommon0 \
    xvfb \
    git \
    wget \
    python3 \
    python3-pip \
    python3-dev \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz -O /tmp/blender-4.3.2-linux-x64.tar.xz \
    && tar -xf /tmp/blender-4.3.2-linux-x64.tar.xz -C /opt/ \
    && ln -sf /opt/blender-4.3.2-linux-x64/blender /usr/local/bin/blender

RUN pip install gradio

RUN git clone https://github.com/robmcrosby/BlenderUSDZ.git /tmp/BlenderUSDZ

RUN xvfb-run blender --background --python-expr "\
    import bpy; \
    bpy.ops.preferences.addon_install(filepath='/tmp/BlenderUSDZ'); \
    bpy.ops.preferences.addon_enable(module='io_scene_usd'); \
    bpy.ops.wm.save_userpref()"

ENV APP_ROOT=/a_square/app \
    CACHE_ROOT=/a_square/.cache \
    PORT=7860

WORKDIR ${APP_ROOT}
COPY src/ ${APP_ROOT}/src/

EXPOSE ${PORT}

CMD ["python3", "-m", "src.__init__"]