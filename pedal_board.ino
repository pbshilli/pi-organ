
// 74HC165 shift register pins
#define PIN_DIN_CLOCK 12
#define PIN_DIN_LOAD 8
#define PIN_DIN_DATA 11

// 74HC165 shift register clock period
#define DIN_PULSE_WIDTH_USEC 5

void setup() {
    // Initialize the USB serial connection
    Serial.begin(9600);

    // Initialize 74HC165 shift register pins
    pinMode(PIN_DIN_CLOCK, OUTPUT);
    pinMode(PIN_DIN_LOAD, OUTPUT);
    pinMode(PIN_DIN_DATA, INPUT);    

    // Scale up the ADC clock to 1MHz since we don't need
    // more than 8 bits of resolution anyway
    // https://r6500.blogspot.com/2015/01/fast-adc-on-arduino-leonardo.html
    ADCSRA = ((ADCSRA & 0xF80) | 0x04);
}

void loop() {
    unsigned long bit_value;
    unsigned long value;
    
    // Ground the load pin to start reading the shift register
    digitalWrite(PIN_DIN_CLOCK, HIGH);
    digitalWrite(PIN_DIN_LOAD, LOW);
    delayMicroseconds(DIN_PULSE_WIDTH_USEC);
    digitalWrite(PIN_DIN_CLOCK, LOW);
    digitalWrite(PIN_DIN_LOAD, HIGH);
    delayMicroseconds(DIN_PULSE_WIDTH_USEC);
    value = 0;
    
    // Read each pedal board pin
    for(int i = 0; i < 32; i++)
    {
        bit_value = digitalRead(PIN_DIN_DATA);
        value |= bit_value << i;
        
        digitalWrite(PIN_DIN_CLOCK, HIGH);
        delayMicroseconds(DIN_PULSE_WIDTH_USEC);
        digitalWrite(PIN_DIN_CLOCK, LOW);
        delayMicroseconds(DIN_PULSE_WIDTH_USEC);
    }
    
    // Print the current state of all pedal board pins
    Serial.print(value, HEX);
    Serial.print(",");

    // Sample each swell shoe and save off the 8 most significant bits
    // (0-255 is a sufficient scale for current use cases)
    Serial.print((analogRead(A0) >> 2), HEX);
    Serial.print(",");
    Serial.print((analogRead(A1) >> 2), HEX);
    Serial.print(",");
    Serial.print((analogRead(A2) >> 2), HEX);

    // Print the delimiter
    Serial.print("\r\n");
}
