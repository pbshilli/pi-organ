
#define PIN_DIN_CLOCK 12
#define PIN_DIN_LOAD 8
#define PIN_DIN_DATA 11

#define DIN_PULSE_WIDTH_USEC 5

void setup() {
    Serial.begin(9600);
    pinMode(PIN_DIN_CLOCK, OUTPUT);
    pinMode(PIN_DIN_LOAD, OUTPUT);
    pinMode(PIN_DIN_DATA, INPUT);    
}

void loop() {
    unsigned int bit_value, value;
    
    digitalWrite(PIN_DIN_CLOCK, HIGH);
    digitalWrite(PIN_DIN_LOAD, LOW);
    delayMicroseconds(DIN_PULSE_WIDTH_USEC);
    digitalWrite(PIN_DIN_CLOCK, LOW);
    digitalWrite(PIN_DIN_LOAD, HIGH);
    delayMicroseconds(DIN_PULSE_WIDTH_USEC);
    value = 0;
    
    for(int i = 0; i < 32; i++ )
    {
        bit_value = digitalRead(PIN_DIN_DATA);
        value |= bit_value << i;
        
        digitalWrite(PIN_DIN_CLOCK, HIGH);
        delayMicroseconds(DIN_PULSE_WIDTH_USEC);
        digitalWrite(PIN_DIN_CLOCK, LOW);
        delayMicroseconds(DIN_PULSE_WIDTH_USEC);
    }
    
    Serial.print(value, HEX);
    Serial.print("\r\n");
    delay(1);
}
