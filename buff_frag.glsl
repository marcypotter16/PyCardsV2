#version 330

uniform sampler2D tex;
uniform float time;      // 0.0 to 1.0 (normalized progress)
uniform float intensity;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 color = texture(tex, v_uv);

    // Skip transparent pixels
    if (color.a < 0.01) {
        fragColor = color;
        return;
    }

    // Diagonal position on card (0 to 2 range)
    float diag = v_uv.x + v_uv.y;

    // Sweep position moves from -0.5 to 2.5 over time
    // This ensures the highlight fully enters and exits the card
    float sweepPos = mix(-0.5, 2.5, time);

    // Distance from the sweep line
    float dist = abs(diag - sweepPos);

    // Create a soft highlight band (width ~0.3)
    float highlight = 1.0 - smoothstep(0.0, 0.35, dist);

    // Add some sparkle variation based on position
    float sparkle = fract(sin(dot(v_uv, vec2(12.9898, 78.233))) * 43758.5453);
    highlight *= (0.8 + 0.4 * sparkle);

    // Golden/white sheen color
    vec3 sheenColor = vec3(1.0, 0.95, 0.7);

    // Apply sheen additively
    color.rgb += highlight * sheenColor * intensity * 0.6;

    // Also boost brightness slightly in the highlight area
    color.rgb = mix(color.rgb, min(color.rgb * 1.3, vec3(1.0)), highlight * 0.3);

    fragColor = color;
}