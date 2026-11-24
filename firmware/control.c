#include "control.h"

#include <math.h>

static float clamp(float x, float low, float high)
{
    return x < low ? low : (x > high ? high : x);
}

static float pi(PiState *state, float error, float kp, float ki_step)
{
    state->integral += ki_step * (error + state->error);
    state->error = error;
    return kp * error + state->integral;
}

static float filter(FilterState *state, Filter cfg, float input)
{
    float value = cfg.b0 * input + cfg.b1 * state->x - cfg.a1 * state->y;
    state->x = input;
    state->y = value;
    return value;
}

void pdu_reset(ControlState *state)
{
    *state = (ControlState){0};
}

uint16_t pdu_step(ControlState *state, const ControlConfig *cfg, ControlSample sample)
{
    const float vin = sample.vin * PDU_VIN_SCALE;
    const float vout = sample.vout * PDU_VOUT_SCALE;
    const float current = sample.current * PDU_CURRENT_SCALE;
    const float uvlo = state->running ? 18.5f : 19.5f;
    if (!sample.enabled || sample.fault || vin < uvlo || vin > 27.0f ||
        sample.vout >= PDU_ADC_MAX || sample.current >= PDU_ADC_MAX) {
        pdu_reset(state);
        return 0;
    }
    if (!state->running) {
        state->reference = clamp(vout, 0.0f, PDU_REFERENCE);
        state->running = 1;
    }
    state->reference = clamp(state->reference + 0.0044f, 0.0f, PDU_REFERENCE);
    float error = state->reference - vout;
    const float drive = vin + 0.38f;
    const float dmax = (float)PDU_PWM_MAX / PDU_PWM_TICKS;
    const float dmin = (float)PDU_PWM_MIN / PDU_PWM_TICKS;
    float feedforward = cfg->method == PDU_PI ? 0.0f : state->reference + 0.38f;
    if (cfg->method == PDU_CASCADE) {
        float command = pi(&state->outer, error, cfg->outer_kp, cfg->outer_ki_step);
        float limited = clamp(command, 0.0f, 9.1f);
        state->outer.integral += 0.08f * (limited - command);
        // At light load, the fixed ADC sample may lie after the diode
        // stops conducting. Estimate that pulse's average from its area.
        const float on_slope = clamp(vin - vout, 0.0f, 32.0f) / 33.0e-6f;
        const float off_slope = (vout + 0.38f) / 33.0e-6f;
        const float on_time = PDU_SAMPLE_PERIOD * state->applied_duty;
        const float peak = on_slope * on_time;
        const float decay = clamp(peak / off_slope, 0.0f, PDU_SAMPLE_PERIOD - on_time);
        const float dcm_average = 0.5f * peak * (on_time + decay) / PDU_SAMPLE_PERIOD;
        const float boundary = 0.5f * on_slope * PDU_SAMPLE_PERIOD * (vout + 0.38f) / drive;
        if (current < 0.35f && boundary > 0.05f) {
            feedforward = (vout + 0.38f) * sqrtf(clamp(limited / boundary, 0.0f, 1.0f));
            error = limited - dcm_average;
        } else {
            error = limited - current;
        }
    }

    // Apply the series sections before PI so anti-windup acts on the final integrator.
    error = filter(&state->pole, cfg->pole, error);
    error = filter(&state->lead, cfg->lead, error);
    const float scale = cfg->method == PDU_PI ? 1.0f : drive;
    float command = (feedforward + pi(&state->inner, error, cfg->kp, cfg->ki_step)) / scale;
    const int final_reference = state->reference >= PDU_REFERENCE;
    const int idle = vout > state->reference + (final_reference ? 0.055f : 0.035f);
    float limited = clamp(command, 0.0f, idle ? 0.0f : dmax);
    if (!idle && final_reference && vout < state->reference - 0.16f) {
        // Large load steps need immediate coil current. Bound the requested
        // pulse by the sensed current while the hardware CBC remains independent.
        const float assist = (vout + 0.38f) / drive + 0.13f * (8.8f - current);
        const float observed = clamp(assist, 0.0f, dmax);
        limited = cfg->method == PDU_TYPE_III ? observed : limited;
    }
    state->inner.integral += 0.1f * (limited - command) * scale;

    uint16_t ticks = 0;
    // Pulse density preserves duty below the minimum realizable gate pulse.
    if (idle) {
        state->pulse_density = 0.0f;
    } else if (limited < dmin) {
        state->pulse_density += limited;
        if (state->pulse_density >= dmin) {
            state->pulse_density -= dmin;
            ticks = PDU_PWM_MIN;
        }
    } else {
        state->pulse_density = 0.0f;
        ticks = (uint16_t)(limited * PDU_PWM_TICKS + 0.5f);
    }
    state->applied_duty = (float)ticks / PDU_PWM_TICKS;
    return ticks;
}
