#include <FastLED.h>

#define LED_PIN     4
#define NUM_LEDS    16
#define BRIGHTNESS  5     // 0-255
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.setBrightness( BRIGHTNESS );
}

int i = 0;
bool b = false;
CRGB color = CRGB::Red;

void loop() {
  leds[i] = color;
  FastLED.show();
  i++;

  if (i == NUM_LEDS) {
    if (b) {
      color = CRGB::Black;
    } else {
      color = CRGB::Green;
    }
    i=0;
    b=!b;
  }

  delay(200);
}
