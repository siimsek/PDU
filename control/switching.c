#include "control.h"
#include "gains.h"
#include "pdu_timing.h"

#include <math.h>
#include <stddef.h>
#include <stdint.h>

enum { DISABLED = 1, STALE_ADC = 2, ADC_RAIL = 4, SHORTED_S1 = 8, UVLO = 16, ADC_STUCK_LOW = 32 };
enum { CBC = 1, OVP = 2, WATCHDOG = 4, ISOLATED = 8, SOFT_UVLO = 16, BAD_SAMPLE = 32, DCM = 64, OVERLOAD_LATCH = 128, LOAD_UV_LATCH = 256, BACKUP_OCP = 512 };
enum { LOAD_CR, LOAD_CC, LOAD_CP };

typedef struct {
    double l, dcr, c, esr, cd, rd, ron, vf, diode_r;
    double max_step, sample_time, adc_latency, execute_time, jitter;
    double noise_v, noise_i, turn_on, turn_off;
    double limit_i, blank_time, ocp_delay, limit_v, ovp_delay, isolate_delay;
    double leak_g, lin_switch, fixed_duty;
    double initial_v, initial_i, sense_delay, backup_limit_i, backup_delay;
    unsigned watchdog_cycles, cbc_latch_cycles;
    uint32_t seed;
    int method;
} Model;

typedef struct {
    double vin, load;
    int kind, flags;
} Cycle;

typedef struct {
    double low_v, high_v, mean_v, low_i, high_i, rms_i, pout, loss, duty;
    double ocp_latency, ovp_latency;
    unsigned flags;
} Result;

typedef struct {
    double i, vc, vd, sense;
} State;

typedef struct {
    double i, vc, vd, sense, voltage, load;
} Slope;

static double min(double a, double b) { return a < b ? a : b; }
static double max(double a, double b) { return a > b ? a : b; }

static Slope slope(const Model *m, Cycle c, State s, int on)
{
    const double g = 1 / m->esr + 1 / m->rd + m->leak_g;
    const double source = s.i + s.vc / m->esr + s.vd / m->rd;
    double voltage;
    double load;
    if (c.kind == LOAD_CR || c.load == 0) {
        voltage = source / (g + c.load);
        load = c.load * voltage;
    } else if (c.kind == LOAD_CC) {
        // A real current sink falls out of regulation near zero terminal voltage.
        const double compliance = 0.3;
        voltage = max((source - c.load) / g, source / (g + c.load / compliance));
        load = c.load * min(1., voltage / compliance);
    } else {
        // The CPL regulates above 8 V. Below that threshold it folds back
        // continuously to zero rather than becoming a nonphysical P/V singularity.
        const double knee = 8.0;
        if (source >= g * knee + c.load / knee) {
            voltage = (source + sqrt(source * source - 4 * g * c.load)) / (2 * g);
            load = c.load / voltage;
        } else {
            voltage = source / (g + c.load / (knee * knee));
            load = voltage * c.load / (knee * knee);
        }
    }
    const double switch_v = on ? c.vin - m->ron * s.i : -m->vf - m->diode_r * s.i;
    const double di = (switch_v - m->dcr * s.i - voltage) / m->l;
    return (Slope){on || s.i > 0. ? di : 0.,
                   (voltage - s.vc) / (m->esr * m->c),
                   (voltage - s.vd) / (m->rd * m->cd),
                   (s.i - s.sense) / m->sense_delay, voltage, load};
}

static State advance(State s, Slope a, double dt)
{
    return (State){max(0., s.i + dt * a.i), s.vc + dt * a.vc,
                   s.vd + dt * a.vd, max(0., s.sense + dt * a.sense)};
}

static double noise(uint32_t *seed)
{
    *seed = *seed * UINT32_C(1664525) + UINT32_C(1013904223);
    return (double)(*seed >> 8) / 8388608. - 1.;
}

static uint16_t adc(double voltage, double scale)
{
    return (uint16_t)(min(max(voltage / scale, 0.), PDU_ADC_MAX) + 0.5);
}

int pdu_simulate(const Model *m, const Cycle *cycles, size_t count, Result *result)
{
    if (!m || !cycles || !result || m->max_step <= 0. ||
        m->sense_delay < m->max_step || m->sample_time - m->jitter < 0. ||
        m->sample_time + m->jitter + PDU_VOUT_APERTURE_S >= PDU_SAMPLE_PERIOD ||
        m->adc_latency < PDU_VOUT_APERTURE_S || m->method < 0 || m->method > PDU_CASCADE) {
        return 1;
    }
    const double period = 1e-5;
    const double never = 1e9;
    State s = {m->initial_i, m->initial_v, m->initial_v, m->initial_i};
    ControlState control = {0};
    uint16_t pwm = 0;
    uint32_t rng = m->seed;
    unsigned stale = 0, cbc_score = 0;
    int latched = 0, previous_disable = 0;
    double ovp_trip = never, ovp_fall = never, backup_cut = never;
    for (size_t k = 0; k < count; ++k) {
        const Cycle c = cycles[k];
        const double start = (double)k * period;
        const int disabled = c.flags & DISABLED;
        if (previous_disable && !disabled && s.vc < m->limit_v - .35) {
            latched = 0;
            cbc_score = 0;
            ovp_trip = never;
            ovp_fall = never;
            backup_cut = never;
        }
        if (disabled || (c.flags & UVLO) || c.vin <= 18.0) {
            pwm = 0;
            stale = 0;
            pdu_reset(&control);
        }
        stale = c.flags & STALE_ADC ? stale + 1 : 0;
        if (m->watchdog_cycles && stale >= m->watchdog_cycles) {
            latched |= WATCHDOG;
        }
        previous_disable = disabled;
        const double trigger_at = m->sample_time + m->jitter * noise(&rng);
        const double current_at = trigger_at + PDU_CURRENT_APERTURE_S;
        const double voltage_at = trigger_at + PDU_VOUT_APERTURE_S;
        const double complete_at = trigger_at + m->adc_latency + m->execute_time;
        const double command = m->fixed_duty >= 0 ? m->fixed_duty : (double)pwm / PDU_PWM_TICKS;
        const double rise = !disabled && !latched && !(c.flags & UVLO) && command > 0 ?
                            m->turn_on : never;
        double fall = command * period + m->turn_off;
        double cbc_trip = never;
        double current_cross = never;
        uint16_t next = pwm;
        int current_sampled = 0, voltage_sampled = 0, processed = 0;
        uint16_t current_sample = 0, voltage_sample = 0;
        Result r = {.low_v = never, .low_i = never, .ocp_latency = -1., .ovp_latency = -1.};
        r.duty = rise < never ? command : 0.;
        if (c.flags & UVLO || c.vin <= 18.0) {
            r.flags |= SOFT_UVLO;
        }

        for (double t = 0.; t < period - 1e-15;) {
            const double event_time = start + t;
            const double cut_at = min(ovp_fall + m->isolate_delay, backup_cut);
            const int isolated = event_time + 1e-15 >= cut_at;
            if (isolated) {
                r.flags |= ISOLATED;
                if (cut_at == backup_cut) {
                    latched |= BACKUP_OCP;
                }
            }
            int driven = t >= rise && t < fall && event_time < ovp_fall && !isolated;
            const int on = driven || ((c.flags & SHORTED_S1) && !isolated);
            const Slope a = slope(m, c, s, on);
            if (!(c.flags & STALE_ADC)) {
                if (!current_sampled && t + 1e-15 >= current_at) {
                    current_sampled = 1;
                    current_sample = adc(s.sense + m->noise_i * noise(&rng), PDU_CURRENT_SCALE);
                }
                if (!voltage_sampled && t + 1e-15 >= voltage_at) {
                    voltage_sampled = 1;
                    voltage_sample = c.flags & ADC_STUCK_LOW ? 0 :
                        adc(a.voltage + m->noise_v * noise(&rng), PDU_VOUT_SCALE);
                }
                if (!processed && t + 1e-15 >= min(complete_at, PDU_UPDATE_DEADLINE_S)) {
                    processed = 1;
                    if (complete_at >= PDU_UPDATE_DEADLINE_S) {
                        latched |= WATCHDOG;
                        next = 0;
                    } else if (k > 0) { // Discard the first DMA sequence after power-up.
                        ControlSample reading = {
                            adc(c.vin, PDU_VIN_SCALE), voltage_sample, current_sample,
                            !disabled, (latched || (c.flags & (ADC_RAIL | UVLO))) != 0
                        };
                        next = pdu_step(&control, &pdu_configs[m->method], reading);
                        if (control.undervoltage_latched) {
                            latched |= LOAD_UV_LATCH;
                        }
                        if (c.flags & ADC_RAIL) {
                            r.flags |= BAD_SAMPLE;
                        }
                    }
                }
            }
            if (driven && s.i >= m->limit_i && current_cross == never) {
                current_cross = t;
            }
            if (driven && cbc_trip == never && t >= rise + m->blank_time && s.sense >= m->limit_i) {
                cbc_trip = t;
                fall = min(fall, t + m->ocp_delay);
                r.flags |= CBC;
            }
            if (backup_cut == never && s.sense >= m->backup_limit_i) {
                backup_cut = event_time + m->backup_delay;
            }
            if (ovp_trip == never && a.voltage >= m->limit_v) {
                ovp_trip = event_time;
                ovp_fall = event_time + m->ovp_delay;
            }
            if (event_time + 1e-15 >= ovp_fall) {
                latched |= OVP;
                r.ovp_latency = ovp_fall - ovp_trip;
            }
            if (cbc_trip < never && t + 1e-15 >= fall) {
                r.ocp_latency = fall - min(cbc_trip, current_cross);
            }
            double end = min(period, t + m->max_step);
            const double events[] = {current_at, voltage_at, min(complete_at, PDU_UPDATE_DEADLINE_S),
                                     rise, fall, rise + m->blank_time,
                                     ovp_fall - start, ovp_fall + m->isolate_delay - start,
                                     backup_cut - start};
            for (size_t j = 0; j < sizeof events / sizeof events[0]; ++j) {
                if (events[j] > t + 1e-15) {
                    end = min(end, events[j]);
                }
            }
            double dt = end - t;
            if (!on && s.i > 0. && a.i < 0. && -s.i / a.i < dt) {
                dt = -s.i / a.i;
                if (dt < 1e-13) {
                    s.i = 0.;
                    continue;
                }
            }
            const State half = advance(s, a, dt / 2);
            const Slope b = slope(m, c, half, on);
            s = advance(s, b, dt);
            if (s.i <= 1e-9 && !on) {
                r.flags |= DCM;
            }
            r.low_v = min(r.low_v, min(a.voltage, b.voltage));
            r.high_v = max(r.high_v, max(a.voltage, b.voltage));
            r.low_i = min(r.low_i, min(half.i, s.i));
            r.high_i = max(r.high_i, max(half.i, s.i));
            const double fraction = dt / period;
            r.mean_v += b.voltage * fraction;
            r.rms_i += half.i * half.i * fraction;
            r.pout += b.voltage * b.load * fraction;
            const double ico = b.vc * m->c;
            const double icd = b.vd * m->cd;
            const double loss = half.i * half.i * (m->dcr + (on ? m->ron : m->diode_r))
                + (!on ? m->vf * half.i : 0.) + m->esr * ico * ico + m->rd * icd * icd;
            r.loss += loss * fraction;
            t += dt;
        }
        if (r.flags & CBC) {
            if (++cbc_score >= m->cbc_latch_cycles && m->cbc_latch_cycles != 0) {
                latched |= OVERLOAD_LATCH;
            }
        } else if (k % 4 == 0 && cbc_score > 0) {
            --cbc_score;
        }
        r.flags |= (unsigned)latched;
        r.rms_i = sqrt(r.rms_i);
        r.loss += r.duty > 0. ? m->lin_switch * c.vin * r.high_i / (2 * period) : 0.;
        result[k] = r;
        pwm = latched ? 0 : next;
    }
    return 0;
}
