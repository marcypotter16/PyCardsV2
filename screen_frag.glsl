// Fragment shader (GLSL ES 1.00)
precision mediump float;

varying vec2 v_texCoord;
uniform sampler2D u_texture;

// size of one texel: vec2(1.0/width, 1.0/height)
uniform vec2 u_texelSize;

// blur parameters
uniform int u_radius;   // blur radius in texels, e.g. 8
uniform float u_sigma;  // gaussian sigma, e.g. 4.0
uniform vec2 u_direction; // (1.0, 0.0) or (0.0, 1.0)

const int MAX_RADIUS = 20; // must be >= max u_radius you expect

void main() {
    // safety clamp for radius
    int r = min(u_radius, MAX_RADIUS);

    // gaussian weights accumulation
    float twoSigmaSq = 2.0 * u_sigma * u_sigma;
    vec4 sum = vec4(0.0);
    float wsum = 0.0;

    // sample from -r to +r
    for (int i = -MAX_RADIUS; i <= MAX_RADIUS; ++i) {
        if (i < -r) continue;
        if (i > r) break;

        float fi = float(i);
        // Gaussian weight
        float w = exp(-(fi * fi) / twoSigmaSq);
        vec2 offset = u_direction * (u_texelSize * fi);
        vec2 coord = clamp(v_texCoord + offset, vec2(0.0), vec2(1.0));
        sum += texture2D(u_texture, coord) * w;
        wsum += w;
    }

    gl_FragColor = sum / wsum;
}
