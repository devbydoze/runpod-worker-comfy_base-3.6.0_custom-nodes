# Stage 1: Base image with common dependencies
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as base

# Prevents prompts from packages asking for user input during installation
ENV DEBIAN_FRONTEND=noninteractive
# Prefer binary wheels over source distributions for faster pip installations
ENV PIP_PREFER_BINARY=1
# Ensures output from python is printed immediately to the terminal without buffering
ENV PYTHONUNBUFFERED=1 
# Speed up some cmake builds
ENV CMAKE_BUILD_PARALLEL_LEVEL=8

# Install Python, git and other necessary tools
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1 \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

# Clean up to reduce image size
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install comfy-cli
RUN pip install comfy-cli

# Install ComfyUI
RUN /usr/bin/yes | comfy --workspace /comfyui install --cuda-version 11.8 --nvidia --version 0.3.26

# Change working directory to ComfyUI
WORKDIR /comfyui

# Install runpod
RUN pip install runpod requests

# Support for the network volume
ADD src/extra_model_paths.yaml ./

# Go back to the root
WORKDIR /

# Add scripts
ADD src/start.sh src/restore_snapshot.sh src/rp_handler.py test_input.json ./
RUN chmod +x /start.sh /restore_snapshot.sh

# Optionally copy the snapshot file
ADD *snapshot*.json /

# Restore the snapshot to install custom nodes
RUN /restore_snapshot.sh

# Enters comfyui directory
WORKDIR /comfyui

# Copies custom_nodes from network space
COPY src/custom_nodes ./custom_nodes/

# Proof git install
RUN apt-get update && apt-get install -y git

# Clone the repositories into the custom_nodes directory
# Step01
RUN git clone https://github.com/ramyma/A8R8_ComfyUI_nodes.git ./custom_nodes/A8R8_ComfyUI_nodes

#Step 02
RUN git clone https://github.com/giriss/comfy-image-saver ./custom_nodes/comfy-image-saver
#RUN git clone https://github.com/MieMieeeee/ComfyUI-CaptionThis ./custom_nodes/ComfyUI-CaptionThis
RUN git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes ./custom_nodes/ComfyUI_Comfyroll_CustomNodes
RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux ./custom_nodes/comfyui_controlnet_aux
RUN git clone https://github.com/cubiq/ComfyUI_essentials ./custom_nodes/ComfyUI_essentials
RUN git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus ./custom_nodes/ComfyUI_IPAdapter_plus

#Step 03
RUN git clone https://github.com/JPS-GER/ComfyUI_JPS-Nodes ./custom_nodes/jps-nodes
RUN git clone https://github.com/Extraltodeus/ComfyUI-AutomaticCFG ./custom_nodes/comfyui-automaticcfg
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts ./custom_nodes/comfyui-custom-scripts
RUN git clone https://github.com/zhuanqianfish/ComfyUI-EasyNode ./custom_nodes/ComfyUl-EasyNode
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use ./custom_nodes/comfyui-easy-use
#RUN git clone https://github.com/kijai/ComfyUI-Florence2 ./custom_nodes/ComfyUI-Florence2
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack ./custom_nodes/comfyui-impact-pack
#RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack ./custom_nodes/ComfyUI-Impact-Subpack

#Step 04
RUN git clone https://github.com/kijai/ComfyUI-KJNodes ./custom_nodes/comfyui-kjnodes
RUN git clone https://github.com/shadowcz007/comfyui-mixlab-nodes ./custom_nodes/comfyui-mixlab-nodes
RUN git clone https://github.com/glowcone/comfyui-string-converter ./custom_nodes/comfyui-string-converter
RUN git clone https://github.com/shiimizu/ComfyUI-TiledDiffusion ./custom_nodes/tiled-diffusion
RUN git clone https://github.com/rgthree/rgthree-comfy ./custom_nodes/rgthree-comfy
RUN git clone https://github.com/WASasquatch/was-node-suite-comfyui ./custom_nodes/was-node-suite-comfyui


#Dependencies and other stuff

#Step 03
# For ComfyUI Easy Node
COPY src/FISH_EasyCapture ./web/extensions/FISH_EasyCapture

# Force install custom nodes requirements
COPY custom_requirements.txt .
RUN pip install -r custom_requirements.txt

# Start container
CMD ["/start.sh"]

# Stage 2: Download models
FROM base as downloader

ARG HUGGINGFACE_ACCESS_TOKEN
ARG MODEL_TYPE

# Change working directory to ComfyUI
WORKDIR /comfyui

# Create necessary directories
RUN mkdir -p models/checkpoints models/vae

# Download checkpoints/vae/LoRA to include in image based on model type
RUN if [ "$MODEL_TYPE" = "sdxl" ]; then \
      wget -O models/checkpoints/sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors && \
      wget -O models/vae/sdxl_vae.safetensors https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors && \
      wget -O models/vae/sdxl-vae-fp16-fix.safetensors https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors; \
    elif [ "$MODEL_TYPE" = "sd3" ]; then \
      wget --header="Authorization: Bearer ${HUGGINGFACE_ACCESS_TOKEN}" -O models/checkpoints/sd3_medium_incl_clips_t5xxlfp8.safetensors https://huggingface.co/stabilityai/stable-diffusion-3-medium/resolve/main/sd3_medium_incl_clips_t5xxlfp8.safetensors; \
    elif [ "$MODEL_TYPE" = "flux1-schnell" ]; then \
      wget -O models/unet/flux1-schnell.safetensors https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors && \
      wget -O models/clip/clip_l.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors && \
      wget -O models/clip/t5xxl_fp8_e4m3fn.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors && \
      wget -O models/vae/ae.safetensors https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors; \
    elif [ "$MODEL_TYPE" = "flux1-dev" ]; then \
      wget --header="Authorization: Bearer ${HUGGINGFACE_ACCESS_TOKEN}" -O models/unet/flux1-dev.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors && \
      wget -O models/clip/clip_l.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors && \
      wget -O models/clip/t5xxl_fp8_e4m3fn.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors && \
      wget --header="Authorization: Bearer ${HUGGINGFACE_ACCESS_TOKEN}" -O models/vae/ae.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors; \
    fi

# Stage 3: Final image
FROM base as final

# Copy models from stage 2 to the final image
COPY --from=downloader /comfyui/models /comfyui/models

# Start container
CMD ["/start.sh"]
