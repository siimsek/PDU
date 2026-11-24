#include "stm32g4xx.h"
#include "control.h"
#include "gains.h"
#include "pdu_timing.h"

// The default image keeps PA8 low. Scope mode is for a disconnected power stage.
enum {
    MISSED_FRAME_LIMIT = 3u,
    ADC1_DMA_REQUEST = 5u
};

_Static_assert(PDU_ADC_RANKS == 6, "The ADC sequence expects two ranks per channel");
static volatile uint16_t adc_frame[PDU_ADC_RANKS];
static uint8_t discard_first_frame = 1;

typedef struct {
    uint32_t good_frames;
    uint32_t missed_frames;
    uint32_t late_frames;
    uint32_t worst_control_cycles;
    uint32_t acquisition_faults;
    uint32_t cbc_events;
    uint16_t pwm_request;
    uint8_t stopped;
} Diagnostics;

volatile Diagnostics pdu_diagnostics;
static ControlState control;
static uint32_t previous_frame;
static unsigned stale_periods;
#if PDU_SCOPE_PWM
static volatile uint8_t pending_pulse;
static uint8_t active_pulse, arm_seen_low;
static CurrentLimitHistory current_limits;
#endif

static void wait_for(volatile uint32_t *reg, uint32_t mask, uint32_t expected)
{
    while ((*reg & mask) != expected) {
        // Startup failures leave the PWM output disconnected.
    }
}

static void configure_clock(void)
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;
    (void)RCC->APB1ENR1;
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_VOS) | PWR_CR1_VOS_0;
    wait_for(&PWR->SR2, PWR_SR2_VOSF, 0);
    PWR->CR5 &= ~PWR_CR5_R1MODE;
    FLASH->ACR = FLASH_ACR_LATENCY_4WS | FLASH_ACR_ICEN | FLASH_ACR_DCEN;
    wait_for(&FLASH->ACR, FLASH_ACR_LATENCY, FLASH_ACR_LATENCY_4WS);
    RCC->CR |= RCC_CR_HSION;
    wait_for(&RCC->CR, RCC_CR_HSIRDY, RCC_CR_HSIRDY);
    RCC->PLLCFGR = RCC_PLLCFGR_PLLSRC_HSI | (3u << RCC_PLLCFGR_PLLM_Pos)
        | (85u << RCC_PLLCFGR_PLLN_Pos) | RCC_PLLCFGR_PLLREN;
    RCC->CR |= RCC_CR_PLLON;
    wait_for(&RCC->CR, RCC_CR_PLLRDY, RCC_CR_PLLRDY);
    // Range 1 boost transition requires temporary AHB division.
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_HPRE) | RCC_CFGR_HPRE_DIV2;
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    wait_for(&RCC->CFGR, RCC_CFGR_SWS, RCC_CFGR_SWS_PLL);
    for (volatile unsigned delay = 0; delay < 40; ++delay) {
        __NOP();
    }
    RCC->CFGR &= ~RCC_CFGR_HPRE;
    SystemCoreClock = PDU_CORE_HZ;
}

static void configure_pins(void)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOCEN;
    (void)RCC->AHB2ENR;
    // Active-high fault lines default to asserted if the external board is absent.
    GPIOA->AFR[1] = (GPIOA->AFR[1] & ~(0xfu << 16)) | (13u << 16); // PA12 FLT1
    GPIOC->AFR[1] = (GPIOC->AFR[1] & ~(0xfu << 16)) | (3u << 16);  // PC12 EEV1
    GPIOA->PUPDR = (GPIOA->PUPDR & ~GPIO_PUPDR_PUPD12) | GPIO_PUPDR_PUPD12_0;
    GPIOC->PUPDR = (GPIOC->PUPDR & ~GPIO_PUPDR_PUPD12) | GPIO_PUPDR_PUPD12_0;
    GPIOA->MODER = (GPIOA->MODER & ~GPIO_MODER_MODE12) | GPIO_MODER_MODE12_1;
    GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODE12) | GPIO_MODER_MODE12_1;
    GPIOA->BSRR = GPIO_BSRR_BR8;
    GPIOA->MODER = (GPIOA->MODER & ~GPIO_MODER_MODE8) | GPIO_MODER_MODE8_0;
#if PDU_SCOPE_PWM
    GPIOA->PUPDR = (GPIOA->PUPDR & ~GPIO_PUPDR_PUPD8) | GPIO_PUPDR_PUPD8_1;
    GPIOC->PUPDR = (GPIOC->PUPDR & ~GPIO_PUPDR_PUPD1) | GPIO_PUPDR_PUPD1_1;
    GPIOC->MODER &= ~GPIO_MODER_MODE1; // PC1 active-high bench enable, default low.
#endif
}

static void configure_dma(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA1EN | RCC_AHB1ENR_DMAMUX1EN;
    (void)RCC->AHB1ENR;
    DMAMUX1_Channel0->CCR = ADC1_DMA_REQUEST;
    DMA1_Channel1->CPAR = (uint32_t)(uintptr_t)&ADC1->DR;
    DMA1_Channel1->CMAR = (uint32_t)(uintptr_t)adc_frame;
    DMA1_Channel1->CNDTR = PDU_ADC_RANKS;
    DMA1->IFCR = DMA_IFCR_CGIF1;
    DMA1_Channel1->CCR = DMA_CCR_PL_1 | DMA_CCR_MSIZE_0 | DMA_CCR_PSIZE_0 |
        DMA_CCR_MINC | DMA_CCR_CIRC | DMA_CCR_TEIE | DMA_CCR_TCIE | DMA_CCR_EN;
}

static void configure_adc(void)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_ADC12EN;
    (void)RCC->AHB2ENR;
    // PA0/PA1/PC0: ADC1_IN1/2/6 for current, Vout and Vin.
    GPIOA->MODER |= GPIO_MODER_MODE0 | GPIO_MODER_MODE1;
    GPIOA->PUPDR &= ~(GPIO_PUPDR_PUPD0 | GPIO_PUPDR_PUPD1);
    GPIOC->MODER |= GPIO_MODER_MODE0;
    GPIOC->PUPDR &= ~GPIO_PUPDR_PUPD0;
    ADC12_COMMON->CCR = ADC_CCR_CKMODE; // HCLK / 4 = 42.5 MHz
    ADC1->CR &= ~ADC_CR_DEEPPWD;
    ADC1->CR |= ADC_CR_ADVREGEN;
    for (uint32_t begin = DWT->CYCCNT; DWT->CYCCNT - begin < PDU_CORE_HZ / 40000u;) {
        __NOP();
    }
    ADC1->CR |= ADC_CR_ADCAL;
    wait_for(&ADC1->CR, ADC_CR_ADCAL, 0);
    for (volatile unsigned delay = 0; delay < 16; ++delay) {
        __NOP();
    }
    ADC1->SMPR1 = ADC_SMPR1_SMP1_0 | ADC_SMPR1_SMP2_0 | ADC_SMPR1_SMP6_0;
    // ES0430: repeat each channel and use the first rank of each pair.
    // The regular group is triggered by HRTIM ADC TRG1 (EXTSEL = 21).
    ADC1->SQR1 = (PDU_ADC_RANKS - 1u) | (1u << ADC_SQR1_SQ1_Pos) |
        (1u << ADC_SQR1_SQ2_Pos) | (2u << ADC_SQR1_SQ3_Pos) | (2u << ADC_SQR1_SQ4_Pos);
    ADC1->SQR2 = (6u << ADC_SQR2_SQ5_Pos) | (6u << ADC_SQR2_SQ6_Pos);
    ADC1->CFGR = ADC_CFGR_DMAEN | ADC_CFGR_DMACFG | ADC_CFGR_JQDIS |
        ADC_CFGR_EXTSEL_4 | ADC_CFGR_EXTSEL_2 | ADC_CFGR_EXTSEL_0 | ADC_CFGR_EXTEN_0;
    ADC1->ISR = ADC_ISR_ADRDY;
    ADC1->CR |= ADC_CR_ADEN;
    wait_for(&ADC1->ISR, ADC_ISR_ADRDY, ADC_ISR_ADRDY);
    ADC1->ISR = ADC_ISR_EOS | ADC_ISR_EOC | ADC_ISR_OVR;
    ADC1->IER = ADC_IER_OVRIE;
    ADC1->CR |= ADC_CR_ADSTART;
}

static void configure_timer(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_HRTIM1EN;
    (void)RCC->APB2ENR;
    HRTIM1_COMMON->ODISR = HRTIM_ODISR_TA1ODIS;
    HRTIM1_COMMON->DLLCR = HRTIM_DLLCR_CAL;
    wait_for(&HRTIM1_COMMON->ISR, HRTIM_ISR_DLLRDY, HRTIM_ISR_DLLRDY);
    HRTIM1_COMMON->DLLCR = HRTIM_DLLCR_CALEN | HRTIM_DLLCR_CALRTE_0;
    HRTIM1_TIMA->TIMxCR = HRTIM_TIMCR_CONT | HRTIM_TIMCR_PREEN | HRTIM_TIMCR_TREPU;
    HRTIM1_TIMA->PERxR = PDU_PWM_TICKS;
    HRTIM1_TIMA->REPxR = 0;
    HRTIM1_TIMA->CMP1xR = PDU_PWM_MIN;
    HRTIM1_TIMA->CMP2xR = PDU_CBC_BLANK_TICKS;
    HRTIM1_TIMA->CMP4xR = PDU_ADC_TRIGGER_TICKS;
    HRTIM1_TIMA->SETx1R = HRTIM_SET1R_PER;
    HRTIM1_TIMA->RSTx1R = HRTIM_RST1R_CMP1 | HRTIM_RST1R_EXTVNT1;
    HRTIM1_TIMA->OUTxR = HRTIM_OUTR_FAULT1_1;
    HRTIM1_TIMA->FLTxR = HRTIM_FLTR_FLT1EN;
    HRTIM1_COMMON->EECR1 = 0; // EEV1 pad, active-high level, synchronized for per-timer blanking.
    HRTIM1_TIMA->EEFxR1 = HRTIM_EEFR1_EE1FLTR_1; // Blank EEV1 from rollover to CMP2.
    HRTIM1_TIMA->CPT1xCR = HRTIM_CPT1CR_EXEV1CPT;
    HRTIM1_COMMON->FLTINR1 = HRTIM_FLTINR1_FLT1E | HRTIM_FLTINR1_FLT1P;
    HRTIM1_COMMON->ADC1R = HRTIM_ADC1R_AD1TAC4;
    HRTIM1_COMMON->CR2 = HRTIM_CR2_TASWU;
    HRTIM1_TIMA->TIMxICR = HRTIM_TIMICR_REPC | HRTIM_TIMICR_CPT1C;
    HRTIM1_TIMA->TIMxDIER = HRTIM_TIMDIER_REPIE;
}

static void inhibit(void)
{
    HRTIM1_COMMON->ODISR = HRTIM_ODISR_TA1ODIS;
#if PDU_SCOPE_PWM
    pending_pulse = 0;
#endif
    pdu_diagnostics.pwm_request = 0;
}

static void acquisition_fault(void)
{
    ++pdu_diagnostics.acquisition_faults;
    pdu_diagnostics.stopped = 1;
    inhibit();
}

void ADC1_2_IRQHandler(void)
{
    if (ADC1->ISR & ADC_ISR_OVR) {
        ADC1->ISR = ADC_ISR_OVR;
        acquisition_fault();
    }
}

void DMA1_Channel1_IRQHandler(void)
{
    const uint32_t begin = DWT->CYCCNT;
    const uint32_t begin_counter = HRTIM1_TIMA->CNTxR;
    const uint32_t status = DMA1->ISR;
    const uint32_t overrun = ADC1->ISR & ADC_ISR_OVR;
    DMA1->IFCR = DMA_IFCR_CGIF1;
    if ((status & DMA_ISR_TEIF1) || overrun) {
        ADC1->ISR = overrun;
        acquisition_fault();
        return;
    }
    if (!(status & DMA_ISR_TCIF1)) {
        return;
    }
    if (discard_first_frame) {
        // ES0430: the first conversion after calibration/idle may be invalid.
        discard_first_frame = 0;
        return;
    }
    uint8_t enabled = !pdu_diagnostics.stopped;
    uint8_t fault = 0;
#if PDU_SCOPE_PWM
    const uint8_t arm = (GPIOC->IDR & GPIO_IDR_ID1) != 0;
    // A PC1 line left high must not re-arm the output after an IWDG reset.
    if (!arm) {
        arm_seen_low = 1;
    }
    enabled = enabled && arm && arm_seen_low;
    fault = fault || (HRTIM1_COMMON->ISR & HRTIM_ISR_FLT1);
#endif
    const ControlSample sample = {
        .vin = adc_frame[4], .vout = adc_frame[2], .current = adc_frame[0],
        .enabled = enabled, .fault = fault
    };
    uint16_t ticks = pdu_step(&control, &pdu_configs[PDU_TYPE_III], sample);
    const uint32_t elapsed = DWT->CYCCNT - begin;
    if (elapsed > pdu_diagnostics.worst_control_cycles) {
        pdu_diagnostics.worst_control_cycles = elapsed;
    }
    const uint32_t counter = HRTIM1_TIMA->CNTxR;
    if (begin_counter < PDU_ADC_EARLIEST_TICKS || counter < begin_counter ||
        counter >= PDU_UPDATE_DEADLINE_TICKS || elapsed >= PDU_PWM_TICKS / 32u) {
        ++pdu_diagnostics.late_frames;
        pdu_diagnostics.stopped = 1;
    }
    if (sample.fault || pdu_diagnostics.stopped) {
        inhibit();
        return;
    }
    pdu_diagnostics.pwm_request = ticks;
    HRTIM1_TIMA->CMP1xR = ticks ? ticks : PDU_PWM_MIN;
#if PDU_SCOPE_PWM
    pending_pulse = ticks && !(GPIOC->IDR & GPIO_IDR_ID12);
    if (pending_pulse) {
        HRTIM1_COMMON->OENR = HRTIM_OENR_TA1OEN;
    } else {
        HRTIM1_COMMON->ODISR = HRTIM_ODISR_TA1ODIS;
    }
#endif
    ++pdu_diagnostics.good_frames;
    IWDG->KR = 0xaaaau;
}

void HRTIM1_TIMA_IRQHandler(void)
{
#if PDU_SCOPE_PWM
    const uint8_t limited = active_pulse && (HRTIM1_TIMA->TIMxISR & HRTIM_TIMISR_CPT1);
    active_pulse = pending_pulse;
    pdu_diagnostics.cbc_events += limited;
    if (pdu_record_cbc(&current_limits, limited, PDU_CBC_LATCH_CYCLES)) {
        pdu_diagnostics.stopped = 1;
        inhibit();
    }
#endif
    HRTIM1_TIMA->TIMxICR = HRTIM_TIMICR_REPC | HRTIM_TIMICR_CPT1C;
    const uint32_t frame = pdu_diagnostics.good_frames;
    if (frame == previous_frame) {
        ++pdu_diagnostics.missed_frames;
        if (++stale_periods >= MISSED_FRAME_LIMIT) {
            pdu_diagnostics.stopped = 1;
            inhibit();
        }
    } else {
        stale_periods = 0;
    }
    previous_frame = frame;
}

// Called by newlib's initializer from the ST startup file.
void _init(void)
{
}

int main(void)
{
    configure_clock();
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    configure_pins();
    configure_dma();
    configure_adc();
    configure_timer();
#if PDU_SCOPE_PWM
    GPIOA->AFR[1] = (GPIOA->AFR[1] & ~0xfu) | 13u; // PA8 HRTIM TA1
    GPIOA->MODER = (GPIOA->MODER & ~GPIO_MODER_MODE8) | GPIO_MODER_MODE8_1;
#endif

    IWDG->KR = 0xccccu;
    IWDG->KR = 0x5555u;
    IWDG->PR = 0; // LSI / 4
    IWDG->RLR = 79;
    wait_for(&IWDG->SR, IWDG_SR_PVU | IWDG_SR_RVU, 0);
    IWDG->KR = 0xaaaau;

    NVIC_SetPriority(DMA1_Channel1_IRQn, 0);
    NVIC_SetPriority(ADC1_2_IRQn, 1);
    NVIC_SetPriority(HRTIM1_TIMA_IRQn, 1);
    NVIC_EnableIRQ(DMA1_Channel1_IRQn);
    NVIC_EnableIRQ(ADC1_2_IRQn);
    NVIC_EnableIRQ(HRTIM1_TIMA_IRQn);
    HRTIM1->sMasterRegs.MCR |= HRTIM_MCR_TACEN;
    for (;;) {
        __WFI();
    }
}
