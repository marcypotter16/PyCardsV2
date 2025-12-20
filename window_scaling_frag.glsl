#version 330

uniform sampler2D tex;
in vec2 v_uv;
out vec4 fragColor;

void main() {
    fragColor = texture(tex, v_uv);
}
