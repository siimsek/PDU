#ifndef PDU_CONTROL_H
#define PDU_CONTROL_H

#include <stdint.h>

#define PDU_PWM_TICKS 54400u
#define PDU_PWM_MAX 40800u
#define PDU_PWM_MIN 816u
#define PDU_REFERENCE 11.0f
#define PDU_SAMPLE_PERIOD 0.00001f
#define PDU_ADC_MAX 4095u
#define PDU_VIN_SCALE (32.0f / PDU_ADC_MAX)
#define PDU_VOUT_SCALE (16.0f / PDU_ADC_MAX)
#define PDU_CURRENT_SCALE (16.0f / PDU_ADC_MAX)

typedef enum {
    PDU_PI, PDU_FF_PI, PDU_TYPE_II, PDU_TYPE_III, PDU_CASCADE
} ControlMethod;

typedef struct {
    float b0, b1, a1;
} Filter;

typedef struct {
    float kp, ki_step, outer_kp, outer_ki_step;
    Filter pole, lead;
    ControlMethod method;
} ControlConfig;

typedef struct {
    float error, integral;
} PiState;

typedef struct {
    float x, y;
} FilterState;

typedef struct {
    PiState inner, outer;
    FilterState pole, lead;
    float reference;
    float pulse_density;
    float applied_duty;
    uint16_t uv_periods;
    uint8_t running, undervoltage_latched;
} ControlState;

typedef struct {
    uint16_t vin, vout, current;
    uint8_t enabled, fault;
} ControlSample;

void pdu_reset(ControlState *state);
uint16_t pdu_step(ControlState *state, const ControlConfig *cfg, ControlSample sample);

#endif
